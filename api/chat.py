import json
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from config import DEFAULT_SESSION_ID, DEFAULT_USER_ID
from core.agents import team
from utils.event_processor import process_event

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get(path='/api/chat')
async def chat(prompt: str) -> StreamingResponse:
    import time

    async def event_generator() -> AsyncGenerator:
        logger.info(f"Starting agent run for prompt: '{prompt[:50]}...'")
        try:
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

            end_event_data = json.dumps(
                {'message': 'All tools and agents have completed their runs.'}
            )
            yield f'event: end\ndata: {end_event_data}\n\n'
            logger.info('Completed!')

        except Exception as e:
            logger.error(
                'An error occurred during agent execution. Please check debug logs.',
                exc_info=True,
            )
            error_data = json.dumps({'error': str(e)})
            yield f'event: error\ndata: {error_data}\n\n'

    return StreamingResponse(content=event_generator(), media_type='text/event-stream')
