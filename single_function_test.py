from celery_code.src.celery_app import distribute_csv_file_no_generate, prepare_inference_tasks
from celery import group, chain, chord

df_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/test.csv'
essay_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/test'
sample_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/sample_submission.csv'

distribute_task = distribute_csv_file_no_generate.s(df_path, essay_path, sample_path)
callback_chain = chain(distribute_task, prepare_inference_tasks.s())
result = callback_chain.apply_async()
