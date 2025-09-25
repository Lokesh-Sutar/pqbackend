import logging
from typing import Any, Callable

from config import FINANCE_AGENT_ID, SENTIMENT_AGENT_ID

logger: logging.Logger = logging.getLogger(__name__)


def clean_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Removes internal attributes and non-serializable objects.

    Args:
        payload: Raw payload dictionary with potentially private/internal attributes

    Returns:
        dict[str, Any]: Cleaned payload with internal attributes removed
    """
    cleaned = {}
    for key, value in payload.items():
        if key.startswith('_') or isinstance(value, logging.Logger):
            continue
        cleaned[key] = value
    return cleaned


def handle_tool_event(event_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """
    Processes events related to tools.

    Args:
        event_name: Name of the event class
        payload: Event data payload

    Returns:
        dict[str, Any]: Processed event data with type and payload
    """
    logger.info(f'Handling tool event: {event_name}')
    agent_id = payload.get('agent_id')

    TOOL_HANDLER_MAP: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
        FINANCE_AGENT_ID: handle_finance_tool_event,
        SENTIMENT_AGENT_ID: handle_sentiment_tool_event,
    }

    handler = TOOL_HANDLER_MAP.get(agent_id, handle_default_tool_event)  # pyright: ignore[reportArgumentType, reportCallIssue]

    return handler(payload)


def handle_content_event(event_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """
    Processes content-related events.

    Args:
        event_name: Name of the event class
        payload: Event data payload

    Returns:
        dict[str, Any]: Processed event data with type 'content'
    """
    logger.info(f'Handling content event: {event_name}')
    return {'type': 'content', 'payload': payload}


def handle_reasoning_event(event_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """
    Processes reasoning or thought events.

    Args:
        event_name: Name of the event class
        payload: Event data payload

    Returns:
        dict[str, Any]: Processed event data with type 'reasoning'
    """
    logger.info(f'Handling reasoning event: {event_name}')
    return {'type': 'reasoning', 'payload': payload}


def handle_run_event(event_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """
    Processes high-level run status events.

    Args:
        event_name: Name of the event class
        payload: Event data payload

    Returns:
        dict[str, Any]: Processed event data with type 'run'
    """
    logger.info(f'Handling run event: {event_name}')
    return {'type': 'run', 'payload': payload}


def handle_finance_tool_event(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Custom logic for tool calls from the finance agent.

    Args:
        payload: Event data payload from finance agent

    Returns:
        dict[str, Any]: Processed event data with type 'tool-finance'
    """
    logger.info('Processing a tool call from the Finance Agent.')
    payload['source_agent_name'] = 'Finance'
    return {'type': 'tool-finance', 'payload': payload}


def handle_sentiment_tool_event(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Custom logic for tool calls from the sentiment agent.

    Args:
        payload: Event data payload from sentiment agent

    Returns:
        dict[str, Any]: Processed event data with type 'tool-sentiment'
    """
    logger.info('Processing a tool call from the Sentiment Agent.')
    payload['source_agent_name'] = 'Sentiment'
    return {'type': 'tool-sentiment', 'payload': payload}


def handle_default_tool_event(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Fallback for tool calls from any other agent.

    Args:
        payload: Event data payload from unknown agent

    Returns:
        dict[str, Any]: Processed event data with type 'tool'
    """
    logger.warning('Processing a tool call from an Unknown_Agent')
    payload['source_agent_name'] = 'Unknown_Agent'
    return {'type': 'tool', 'payload': payload}


def handle_default_event(event_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """
    A fallback for any other event types.

    Args:
        event_name: Name of the event class
        payload: Event data payload

    Returns:
        dict[str, Any]: Processed event data with type 'log'
    """
    logger.info(f'Handling default/log event: {event_name}')
    return {'type': 'log', 'payload': payload}
