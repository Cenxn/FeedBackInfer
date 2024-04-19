from celery import Celery

app = Celery('feedback_infer_app', broker='')