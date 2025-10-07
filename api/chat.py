import json
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from config import DEFAULT_SESSION_ID, DEFAULT_USER_ID
from core.agents import get_team
from core.ticker_store import ticker_store
from utils.event_processor import process_event

chat_router = APIRouter()

logger = logging.getLogger(__name__)


@chat_router.get(path='/api/chat')
async def chat(prompt: str) -> StreamingResponse:
    import time

    ticker_store.clear()
    logger.info('Cleared previous tickers for new prompt')

    async def event_generator() -> AsyncGenerator:
        start_time = time.time()
        logger.info(f"Starting agent run for prompt: '{prompt[:50]}...'")

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
                yield process_event(event)
                time.sleep(0.01)

            end_time = time.time()

            total_duration = end_time - start_time

            final_tickers = ticker_store.get_tickers()
            logger.info(f'Completed in {total_duration:.2f} seconds')
            end_event_data = json.dumps(
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
            error_data = json.dumps({'error': str(e)})
            yield f'event: error\ndata: {error_data}\n\n'

    return StreamingResponse(content=event_generator(), media_type='text/event-stream')
