from fastapi import FastAPI

import apps.core.models
from apps.core.api.endpoints import router as video_api_router
from apps.core.api.endpoints.jobs_endpoints import router as jobs_api_router

app = FastAPI()

# Register routers
app.include_router(video_api_router, prefix="/api/v1/videos", tags=["Video Processing"])
app.include_router(jobs_api_router, prefix="/api/v1/jobs", tags=["Jobs"])
