import json
import logging
from dataclasses import asdict, is_dataclass

logger = logging.getLogger(__name__)

FINANCE_AGENT_ID = 'agent_1'
SENTIMENT_AGENT_ID = 'agent_2'


def clean_payload(payload: dict) -> dict:
    """Removes internal attributes and non-serializable objects."""
    cleaned = {}
    for key, value in payload.items():
        if key.startswith('_') or isinstance(value, logging.Logger):
            continue
        cleaned[key] = value
    return cleaned


def handle_tool_event(event_name: str, payload: dict) -> dict:
    """Processes events related to tools."""
    logger.info(f'Handling tool event: {event_name}')
    agent_id = payload.get('agent_id')

    TOOL_HANDLER_MAP = {
        FINANCE_AGENT_ID: handle_finance_tool_event,
        SENTIMENT_AGENT_ID: handle_sentiment_tool_event,
    }

    handler = TOOL_HANDLER_MAP.get(agent_id, handle_default_tool_event)

    return handler(payload)


def handle_content_event(event_name: str, payload: dict) -> dict:
    """Processes content-related events."""
    logger.info(f'Handling content event: {event_name}')
    return {'type': 'content', 'payload': payload}


def handle_reasoning_event(event_name: str, payload: dict) -> dict:
    """Processes reasoning or thought events."""
    logger.info(f'Handling reasoning event: {event_name}')
    return {'type': 'reasoning', 'payload': payload}


def handle_run_event(event_name: str, payload: dict) -> dict:
    """Processes high-level run status events."""
    logger.info(f'Handling run event: {event_name}')

    if event_name == 'RunCompletedEvent' and 'metrics' in payload:
        logger.info('--- AGENT RUN COMPLETED ---')
        metrics_json = json.dumps(payload.get('metrics', {}), indent=2)
        logger.info(f'Final Metrics:\n{metrics_json}')
        logger.info('---------------------------')

    return {'type': 'run', 'payload': payload}


def handle_finance_tool_event(payload: dict) -> dict:
    """Custom logic for tool calls from the finance agent."""
    logger.info('Processing a tool call from the Finance Agent.')
    payload['source_agent_name'] = 'Finance'
    return {'type': 'tool-finance', 'payload': payload}


def handle_sentiment_tool_event(payload: dict) -> dict:
    """Custom logic for tool calls from the sentiment agent."""
    logger.info('Processing a tool call from the Sentiment Agent.')
    payload['source_agent_name'] = 'Sentiment'
    return {'type': 'tool-sentiment', 'payload': payload}


def handle_default_tool_event(payload: dict) -> dict:
    """Fallback for tool calls from any other agent."""
    logger.warning(
        f'Processing a tool call from an unknown agent: {payload.get("agent_id")}'
    )
    payload['source_agent_name'] = 'Unknown'
    return {'type': 'tool', 'payload': payload}


def handle_default_event(event_name: str, payload: dict) -> dict:
    """A fallback for any other event types."""
    logger.info(f'Handling default/log event: {event_name}')
    return {'type': 'log', 'payload': payload}
