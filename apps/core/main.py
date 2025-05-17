from fastapi import FastAPI

import apps.core.models
from apps.core.api.endpoints import router as api_router

app = FastAPI()

# Register routers
app.include_router(api_router, prefix="/api/v1/videos", tags=["Video Processing"])
