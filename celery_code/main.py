from celery import group, chain, chord
from src.celery_app import app, prepare_inference_tasks, distribute_csv_file_no_generate, process_csv_paths


def main():
    df_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/train.csv'
    essay_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/train'
    # sample_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/sample_submission.csv'

    distribute_task = distribute_csv_file_no_generate.s(df_path, essay_path, sample_path=None)
    callback_chain = chain(distribute_task, prepare_inference_tasks.s()).apply_async()
    task_signatures = callback_chain.get()
    print(
        f"[Executing] Generated result from distribute_csv_file_no_generate and prepare_inference_tasks. \n get {task_signatures}")

    task_list = [
        app.signature(task['task'], args=task['args'], kwargs=task['kwargs'],
                      options=task['options'], immutable=task['immutable']) for task in task_signatures
    ]

    result_chord = chord(task_list)(process_csv_paths.s())
    final_result = result_chord.get()
    print(f"[FINISH] Workflow executed. Output file at {final_result}")


if __name__ == '__main__':
    main()
