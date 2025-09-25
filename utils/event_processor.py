import json
from dataclasses import asdict, is_dataclass
from typing import Any, Callable

from utils import event_handler as event_handlers

HANDLER_MAP: dict[str, Callable[[str, dict[str, Any]], dict[str, Any]]] = {
    'Tool': event_handlers.handle_tool_event,
    'Content': event_handlers.handle_content_event,
    'Reasoning': event_handlers.handle_reasoning_event,
    'Run': event_handlers.handle_run_event,
}


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


def process_event(event) -> str:
    """
    Processes an agent event and formats it for Server-Sent Events (SSE).

    Args:
        event: The event object to process (dataclass, object with to_dict, or regular object)

    Returns:
        str: Formatted SSE string with event type and JSON data
    """
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

        sse_data = {
            'event': cleaned_payload.pop('event', event_name),
            'type': processed_data.get('type', 'log'),
            'meta': {
                'runId': cleaned_payload.pop('run_id', None),
                'sessionId': cleaned_payload.pop('session_id', None),
            },
            'payload': processed_data.get('payload', {}),
        }

        json_data = json.dumps(sse_data)
        event_type = sse_data['type']
        return f'event: {event_type}\ndata: {json_data}\n\n'

    except Exception as e:
        # Return error event if processing fails
        error_data = {
            'event': 'error',
            'type': 'error',
            'meta': {'runId': None, 'sessionId': None},
            'payload': {'error': f'Failed to process event: {str(e)}'},
        }
        return f'event: error\ndata: {json.dumps(error_data)}\n\n'
