# app.py

from celery import Celery
import time

# Create Celery instance
app = Celery('app', broker='redis://redis:6379/0',backend='redis://redis:6379/0')


if __name__ == '__main__':
    app.start()