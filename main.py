import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.chat import router as chat_router
from config import APP_HOST, APP_PORT

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
async def root():
    return {'message': 'Hello, World! The server is running.'}


app.include_router(chat_router)

if __name__ == '__main__':
    uvicorn.run('main:app', host=APP_HOST, port=APP_PORT, reload=True)
