from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from ctenex.domain.in_memory.matching_engine.model import MatchingEngine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:
    # Instantiate the matching engine
    app.state.matching_engine = MatchingEngine()
    app.state.matching_engine.start()
    yield
    # Clean up all order books
    app.state.matching_engine.stop()
