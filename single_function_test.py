from celery_code.src.celery_app import app, prepare_inference_tasks, inference_single_csv, \
    distribute_csv_file_no_generate, prepare_inference_tasks
from celery import group, chain, chord

df_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/test.csv'
essay_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/test'
sample_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/sample_submission.csv'

distribute_task = distribute_csv_file_no_generate.s(df_path, essay_path, sample_path)
callback_chain = chain(distribute_task, prepare_inference_tasks.s()).apply_async()

task_signatures = callback_chain.get()
print(f'\nHIGHLIGHT!!!!!\n {task_signatures} type: \n {type(task_signatures)}')

task_list = [
    app.signature(task['task'], args=task['args'], kwargs=task['kwargs'],
                  options=task['options'], immutable=task['immutable']) for task in task_signatures
]

result_group = group(task_list)
result = result_group.apply_async()

print(result.get())
