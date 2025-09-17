import json
from dataclasses import asdict, is_dataclass

from utils import event_handler as event_handlers

HANDLER_MAP = {
    'Tool': event_handlers.handle_tool_event,
    'Content': event_handlers.handle_content_event,
    'Reasoning': event_handlers.handle_reasoning_event,
    'Run': event_handlers.handle_run_event,
}


def event_to_dict(event) -> dict:
    """Converts a dataclass or object to a dictionary."""
    if hasattr(event, 'to_dict'):
        return event.to_dict()
    if is_dataclass(event):
        return asdict(event)
    return vars(event)


def process_event(event) -> str:
    """
    Processes an agent event and formats it for Server-Sent Events (SSE).
    """
    event_name = event.__class__.__name__
    raw_payload = event_to_dict(event)

    handler = event_handlers.handle_default_event
    for key, h in HANDLER_MAP.items():
        if key in event_name:
            handler = h
            break

    cleaned_payload = event_handlers.clean_payload(raw_payload)
    print(f'Cleaned Data =================\n{cleaned_payload}')
    print()
    print()
    processed_data = handler(event_name, cleaned_payload)
    print(f'Processed Data =================\n{processed_data}')

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
