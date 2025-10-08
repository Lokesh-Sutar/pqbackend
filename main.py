import logging
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.chat import chat_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


app: FastAPI = FastAPI()

app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=['*'],
)


@app.get(path='/')
async def root() -> JSONResponse:
    return JSONResponse(
        {
            'message': 'Hello, World! The server is running.',
            'timestamp': datetime.now().isoformat() + 'Z',
            'version': '1.0.0',
            'software': 'PersonaQuant Backend',
            'license': 'MIT',
        }
    )


app.include_router(chat_router)
