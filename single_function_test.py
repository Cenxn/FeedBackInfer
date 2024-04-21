from celery_code.src.celery_app import inference_single_csv

df_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/test.csv'
essay_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/test'
sample_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/sample_submission.csv'

print(inference_single_csv(df_path=df_path, essay_folder_path=essay_path, output_csv_path=sample_path))
