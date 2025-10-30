import json
import logging
from collections.abc import AsyncGenerator
from datetime import datetime
from logging import Logger
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from config import DEFAULT_SESSION_ID, DEFAULT_USER_ID
from core.agents import get_team
from utils.event_processor import clear_tool_history, get_tool_history, process_event
from utils.ticker_store import ticker_store

chat_router = APIRouter()

logger: Logger = logging.getLogger(__name__)

CONVERSATION_DIR = Path('conversation')
CONVERSATION_DIR.mkdir(exist_ok=True)


def save_final_output(prompt: str, final_event_data: dict) -> None:
    """Saves the final agent output to a JSON file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{timestamp}_{prompt[:30].replace(" ", "_")}.json'
    filepath = CONVERSATION_DIR / filename

    try:
        tool_history = extract_tool_history_from_response(final_event_data)
        event_tool_history = get_tool_history()
        final_tool_history = tool_history if tool_history else event_tool_history

        with open(filepath, 'w') as f:
            json.dump(
                {
                    'prompt': prompt,
                    'timestamp': datetime.now().isoformat(),
                    'response': final_event_data,
                    'tool_history': final_tool_history,
                },
                f,
                indent=2,
            )
        logger.info(
            f'Saved final conversation to {filepath} with {len(final_tool_history)} tool history entries'
        )
    except Exception:
        logger.error(f'Failed to save conversation to {filepath}', exc_info=True)


def extract_tool_history_from_response(response_data: dict) -> list[dict]:
    """
    Extract tool history from the response data structure.

    Args:
        response_data: The final event data containing agent results

    Returns:
        list[dict]: List of tool call records with details
    """
    tool_history = []
    payload = response_data.get('payload', {})
    agents = payload.get('agents', payload.get('member_responses', []))

    for agent in agents:
        agent_id = agent.get('agent_id')
        agent_name = agent.get('agent_name', agent.get('name', 'Unknown'))
        tools = agent.get('tools', [])

        for tool in tools:
            tool_record = {
                'event_name': 'ToolCallCompletedEvent',
                'timestamp': tool.get('created_at'),
                'agent_id': agent_id,
                'agent_name': agent_name,
                'tool_name': tool.get('tool_name'),
                'tool_args': tool.get('tool_args'),
                'tool_result': tool.get('result'),
            }
            tool_history.append(tool_record)

    return tool_history


@chat_router.get(path='/api/chat')
async def chat(prompt: str) -> StreamingResponse:
    import time

    ticker_store.clear()
    clear_tool_history()
    logger.info('Cleared previous tickers and tool history for new prompt')

    async def event_generator() -> AsyncGenerator:
        start_time = time.time()
        logger.info("Starting team run now!'")
        final_event_data = None
        try:
            team = get_team()
            for event in team.run(
                prompt,
                stream=True,
                stream_intermediate_steps=True,
                user_id=DEFAULT_USER_ID,
                exponential_backoff=True,
                delay_between_retries=3,
                retries=10,
                session_id=DEFAULT_SESSION_ID,
            ):
                processed_event = process_event(event)
                if (
                    'TeamRunCompleted' in processed_event
                    or 'RunCompleted' in processed_event
                ):
                    try:
                        data_str = processed_event.split('data: ')[1].strip()
                        final_event_data = json.loads(data_str)
                    except (json.JSONDecodeError, IndexError):
                        logger.warning(
                            'Could not parse final event data.', exc_info=True
                        )

                yield processed_event
                time.sleep(0.01)

            end_time: float = time.time()

            if final_event_data:
                save_final_output(prompt, final_event_data)

            total_duration: float = end_time - start_time

            final_tickers: list[str] = ticker_store.get_tickers()
            logger.info(f'Completed in {total_duration:.2f} seconds')
            end_event_data: str = json.dumps(
                {
                    'message': 'All tools and agents have completed their runs.',
                    'tickers_used': final_tickers,
                    'execution_time': {
                        'start_time': start_time,
                        'end_time': end_time,
                        'total_duration_seconds': round(total_duration, 2),
                        'total_duration_formatted': f'{total_duration:.2f}s',
                    },
                }
            )
            yield f'event: end\ndata: {end_event_data}\n\n'
            logger.info(end_event_data)

        except Exception as e:
            logger.error(
                'An error occurred during agent execution. Please check debug logs.',
                exc_info=True,
            )
            error_data: str = json.dumps({'error': str(e)})
            yield f'event: error\ndata: {error_data}\n\n'

    return StreamingResponse(content=event_generator(), media_type='text/event-stream')
