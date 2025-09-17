import asyncio
import json
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from config import DEFAULT_SESSION_ID, DEFAULT_USER_ID
from utils.agents import team
from utils.event_processor import process_event

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get(path='/api/chat')
async def chat(prompt: str) -> StreamingResponse:
    async def event_generator() -> AsyncGenerator:
        logger.info(f"Starting agent run for prompt: '{prompt[:50]}...'")
        try:
            async for event in team.arun(
                prompt,
                stream=True,
                stream_intermediate_steps=True,
                user_id=DEFAULT_USER_ID,
                session_id=DEFAULT_SESSION_ID,
            ):
                yield process_event(event)

                await asyncio.sleep(0.01)

            end_event_data = json.dumps({'message': 'RunCompleted'})
            yield f'event: end\ndata: {end_event_data}\n\n'
            logger.info('Agent run completed successfully.')

        except Exception as e:
            logger.error(f'An error occurred during agent execution: {e}', exc_info=True)
            error_data = json.dumps({'error': str(e)})
            yield f'event: error\ndata: {error_data}\n\n'

    return StreamingResponse(content=event_generator(), media_type='text/event-stream')
