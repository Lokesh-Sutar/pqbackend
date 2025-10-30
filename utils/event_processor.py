import json
from dataclasses import asdict, is_dataclass
from typing import Any, Callable

from utils import event_handler as event_handlers
from utils.ticker_store import ticker_store
from utils.token_tracker import token_tracker

HANDLER_MAP: dict[str, Callable[[str, dict[str, Any]], dict[str, Any]]] = {
    'Tool': event_handlers.handle_tool_event,
    'Content': event_handlers.handle_content_event,
    'Reasoning': event_handlers.handle_reasoning_event,
    'Run': event_handlers.handle_run_event,
}

_tool_event_history: list[dict] = []


def clear_tool_history() -> None:
    """Clear the tool event history."""
    global _tool_event_history
    _tool_event_history = []


def get_tool_history() -> list[dict[str, Any]]:
    """Get the complete tool event history for the current conversation."""
    return _tool_event_history.copy()


def event_to_dict(event: Any) -> dict[str, Any]:
    """
    Converts a dataclass or object to a dictionary.

    Args:
        event: The event object to convert (dataclass, object with to_dict method, or regular object)

    Returns:
        dict[str, Any]: Dictionary representation of the event
    """
    if hasattr(event, 'to_dict'):
        return event.to_dict()
    if is_dataclass(event):
        return asdict(event)  # pyright: ignore[reportArgumentType]
    return vars(event)


def _track_token_metrics(
    event_name: str, cleaned_payload: dict[str, Any], processed_data: dict[str, Any]
) -> None:
    """
    Extract and track token metrics from run events.

    Args:
        event_name: Name of the event (RunCompleted, TeamRunCompleted, etc.)
        cleaned_payload: Cleaned payload from the event
        processed_data: Processed data from the event handler
    """
    try:
        payload = processed_data.get('payload', {})

        metrics = payload.get('metrics')
        if not metrics:
            return

        agent_id = payload.get('agent_id')
        agent_name = payload.get('agent_name')
        team_name = payload.get('team_name')
        run_id = cleaned_payload.get('run_id')
        session_id = cleaned_payload.get('session_id')
        parent_run_id = payload.get('parent_run_id')

        token_tracker.track_event(
            event_name=event_name,
            agent_id=agent_id,
            agent_name=agent_name,
            team_name=team_name,
            metrics=metrics,
            run_id=run_id,
            session_id=session_id,
            parent_run_id=parent_run_id,
        )
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f'Failed to track token metrics: {e}')


def _extract_and_store_tool_history(payload: dict) -> None:
    """
    Extract tool history from RunCompleted events and append to global tool history.

    This captures tool calls with their full details (name, args, result) from completed agent runs.

    Args:
        payload: The cleaned event payload from a RunCompleted event
    """
    import logging

    logger = logging.getLogger(__name__)
    global _tool_event_history

    agent_id = payload.get('agent_id')
    agent_name = payload.get('agent_name', payload.get('name', 'Unknown'))

    tools = payload.get('tools', [])

    if not tools and 'agents' in payload:
        for agent_result in payload.get('agents', []):
            agent_tools = agent_result.get('tools', [])
            if agent_tools:
                sub_agent_id = agent_result.get('agent_id')
                sub_agent_name = agent_result.get(
                    'agent_name', agent_result.get('name', 'Unknown')
                )
                logger.info(
                    f'Extracting {len(agent_tools)} tools from nested agent {sub_agent_name}'
                )

                for tool in agent_tools:
                    tool_event_record = {
                        'event_name': 'ToolCallCompletedEvent',
                        'timestamp': tool.get('created_at'),
                        'agent_id': sub_agent_id,
                        'agent_name': sub_agent_name,
                        'tool_name': tool.get('tool_name'),
                        'tool_args': tool.get('tool_args'),
                        'tool_result': tool.get('result'),
                    }
                    _tool_event_history.append(tool_event_record)
        return

    logger.info(
        f'Extracting tool history for agent {agent_name} (ID: {agent_id}): {len(tools)} tools found'
    )

    if not tools:
        return

    for tool in tools:
        tool_event_record = {
            'event_name': 'ToolCallCompletedEvent',
            'timestamp': tool.get('created_at'),
            'agent_id': agent_id,
            'agent_name': agent_name,
            'tool_name': tool.get('tool_name'),
            'tool_args': tool.get('tool_args'),
            'tool_result': tool.get('result'),
        }
        _tool_event_history.append(tool_event_record)
        logger.info(f'Added tool {tool.get("tool_name")} to history')


def process_event(event) -> str:
    """
    Processes an agent event and formats it for Server-Sent Events (SSE).

    Args:
        event: The event object to process (dataclass, object with to_dict, or regular object)

    Returns:
        str: Formatted SSE string with event type and JSON data
    """
    global _tool_event_history
    try:
        event_name = event.__class__.__name__
        raw_payload = event_to_dict(event)

        handler = event_handlers.handle_default_event
        for key, h in HANDLER_MAP.items():
            if key in event_name:
                handler = h
                break

        cleaned_payload = event_handlers.clean_payload(raw_payload)
        processed_data = handler(event_name, cleaned_payload)

        if 'RunCompleted' in event_name:
            _extract_and_store_tool_history(cleaned_payload)

        if 'RunCompleted' in event_name or 'TeamRunCompleted' in event_name:
            _track_token_metrics(event_name, cleaned_payload, processed_data)

        current_tickers = ticker_store.get_tickers()
        sse_data = {
            'event': cleaned_payload.pop('event', event_name),
            'type': processed_data.get('type', 'log'),
            'meta': {
                'runId': cleaned_payload.pop('run_id', None),
                'sessionId': cleaned_payload.pop('session_id', None),
            },
            'payload': processed_data.get('payload', {}),
            'tickers': current_tickers,
            'ticker_count': len(current_tickers),
        }

        json_data = json.dumps(sse_data)
        event_type = sse_data['type']
        return f'event: {event_type}\ndata: {json_data}\n\n'

    except Exception as e:
        error_data = {
            'event': 'error',
            'type': 'error',
            'meta': {'runId': None, 'sessionId': None},
            'payload': {'error': f'Failed to process event: {str(e)}'},
        }
        return f'event: error\ndata: {json.dumps(error_data)}\n\n'
