from celery_code.src.celery_app import distribute_csv_file_no_generate

df_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/test.csv'
essay_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/test'
sample_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/sample_submission.csv'

result = distribute_csv_file_no_generate(df_path=df_path, essay_path=essay_path, sample_path=sample_path)
result.ready()
print(result.get())
