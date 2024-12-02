import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from aiokafka import AIOKafkaProducer  # type: ignore
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .api import api_router
from .config import settings
from .kafka_logger import batch_sender

kafka_producer: AIOKafkaProducer = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global kafka_producer
    kafka_producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
    )

    await kafka_producer.start()
    batch_task = asyncio.create_task(batch_sender())

    try:
        yield
    finally:
        if kafka_producer:
            await kafka_producer.stop()
        batch_task.cancel()


# Initialize a FastAPI application with custom settings
app = FastAPI(
    title=settings.TITLE,
    description=settings.DESCRIPTION,
    docs_url=settings.DOCS_URL,
    openapi_url=settings.OPENAPI_URL,
    redoc_url=settings.REDOC_URL,
    lifespan=lifespan,
)

# Add CORS middleware to the FastAPI application
# This middleware allows configuring how the server
# should respond to cross-origin requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.IS_ALLOWED_CREDENTIALS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)
