* [x]   Task 3.5: **Model Imports & Alembic:**
    *   Ensure `apps/core/models/__init__.py` imports all model classes (e.g., `from .video_model import VideoModel`) and `Base`.
    *   Update `apps/core/alembic/env.py` `target_metadata` to `Base.metadata`.
* [x]   Task 3.6: **Generate and Apply Migrations:**
    *   Run `cd apps/core && alembic revision --autogenerate -m "create_video_processing_tables"`.
    *   Inspect the generated migration script in `apps/core/alembic/versions/`.
    *   Run `cd apps/core && alembic upgrade head` to apply to your local Supabase DB. 