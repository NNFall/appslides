from __future__ import annotations

from contextlib import asynccontextmanager
import asyncio
import shutil
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.router import api_router
from src.core.dependencies import get_billing_service
from src.core.logging import configure_logging, get_logger
from src.core.settings import get_settings
from src.repositories.artifacts import delete_artifacts_under
from src.repositories.jobs import fail_incomplete_jobs
from src.repositories.storage import configure_database_path, init_storage


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    settings.data_dir.mkdir(parents=True, exist_ok=True)
    configure_database_path(settings.database_path)
    init_storage(settings.database_path)
    recovered_jobs = fail_incomplete_jobs()
    settings.temp_dir.mkdir(parents=True, exist_ok=True)
    settings.templates_dir.mkdir(parents=True, exist_ok=True)
    logger = get_logger('appslides.backend.app')
    billing_service = get_billing_service()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        auto_renew_task: asyncio.Task[None] | None = None
        temp_cleanup_task: asyncio.Task[None] | None = None

        logger.info(
            'Backend starting: env=%s data_dir=%s database_path=%s temp_dir=%s templates_dir=%s temp_ttl=%ss',
            settings.app_env,
            settings.data_dir,
            settings.database_path,
            settings.temp_dir,
            settings.templates_dir,
            settings.temp_ttl_seconds,
        )
        if recovered_jobs:
            logger.warning('Marked %s incomplete jobs as failed after restart', recovered_jobs)
        if billing_service.is_configured:
            auto_renew_task = asyncio.create_task(_auto_renew_loop(billing_service, settings.auto_renew_interval, logger))
        temp_cleanup_task = asyncio.create_task(
            _temp_cleanup_loop(
                temp_dir=settings.temp_dir,
                ttl_seconds=settings.temp_ttl_seconds,
                interval_seconds=settings.temp_clean_interval,
                logger=logger,
            )
        )
        yield
        for task in (auto_renew_task, temp_cleanup_task):
            if task is None:
                continue
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url='/docs',
        redoc_url='/redoc',
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.include_router(api_router)

    @app.get('/', tags=['system'])
    async def root() -> dict[str, str]:
        return {
            'service': settings.app_name,
            'version': settings.app_version,
            'environment': settings.app_env,
        }

    return app


app = create_app()


async def _auto_renew_loop(service, interval_seconds: int, logger) -> None:
    while True:
        try:
            processed = await service.process_due_auto_renewals_once()
            if processed:
                logger.info('Processed %s subscription auto-renew checks', processed)
        except Exception:  # noqa: BLE001
            logger.exception('Auto-renew loop failed')
        await asyncio.sleep(max(10, interval_seconds))


async def _temp_cleanup_loop(
    *,
    temp_dir: Path,
    ttl_seconds: int,
    interval_seconds: int,
    logger,
) -> None:
    while True:
        try:
            removed_dirs, removed_files, removed_artifacts = await asyncio.to_thread(
                _cleanup_temp_dir_once,
                temp_dir,
                ttl_seconds,
            )
            if removed_dirs or removed_files or removed_artifacts:
                logger.info(
                    'Temp cleanup removed dirs=%s files=%s artifact_rows=%s',
                    removed_dirs,
                    removed_files,
                    removed_artifacts,
                )
        except Exception:  # noqa: BLE001
            logger.exception('Temp cleanup loop failed')
        await asyncio.sleep(max(60, interval_seconds))


def _cleanup_temp_dir_once(temp_dir: Path, ttl_seconds: int) -> tuple[int, int, int]:
    temp_root = temp_dir.resolve()
    temp_root.mkdir(parents=True, exist_ok=True)
    if ttl_seconds <= 0:
        return 0, 0, 0

    cutoff = time.time() - ttl_seconds
    removed_dirs = 0
    removed_files = 0
    removed_paths: list[Path] = []

    for bucket_name in ('uploads', 'conversions', 'presentations'):
        bucket = (temp_root / bucket_name).resolve()
        if not bucket.exists() or not bucket.is_dir():
            continue
        if temp_root not in bucket.parents:
            continue

        for path in bucket.iterdir():
            try:
                if path.stat().st_mtime >= cutoff:
                    continue
                resolved_path = path.resolve()
                if temp_root not in resolved_path.parents:
                    continue
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                    removed_dirs += 1
                else:
                    path.unlink(missing_ok=True)
                    removed_files += 1
                removed_paths.append(resolved_path)
            except FileNotFoundError:
                continue

    removed_artifacts = delete_artifacts_under(removed_paths)
    return removed_dirs, removed_files, removed_artifacts
