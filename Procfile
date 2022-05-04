web: gunicorn Svoyak_backend.asgi:application -k uvicorn.workers.UvicornWorker
worker: python3.8 manage.py celery -A Svoyak_backend worker -l info