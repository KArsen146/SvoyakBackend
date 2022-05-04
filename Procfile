web: gunicorn Svoyak_backend.asgi:application -k uvicorn.workers.UvicornWorker
worker: celery -A Svoyak_backend worker -l info