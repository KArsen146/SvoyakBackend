web: gunicorn Svoyak_backend.asgi:application -k uvicorn.workers.UvicornWorker
worker: celery worker --app=tasks.app