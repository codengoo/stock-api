from fastapi import APIRouter

from app.api.v1.endpoints import analysis, market, reference, screener, system

api_router = APIRouter()

# Market data: /price-board, /quote/intraday/{symbol}, /quote/history/{symbol}
api_router.include_router(market.router)

# Reference data: /listing, /company/{symbol}
api_router.include_router(reference.router)

# Technical analysis: /analysis/ma/{symbol}
api_router.include_router(analysis.router, prefix="/analysis")

# Screener: /screener/suggest
api_router.include_router(screener.router, prefix="/screener")

# System: /health
api_router.include_router(system.router)
