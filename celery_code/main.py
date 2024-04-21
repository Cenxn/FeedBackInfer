from celery import group, chain, chord

from .src.celery_app import prepare_inference_tasks, distribute_csv_file_no_generate, process_csv_paths


def main():
    df_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/test.csv'
    essay_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/test'
    sample_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/sample_submission.csv'

    # Initial task to distribute CSV file processing
    distribute_task = distribute_csv_file_no_generate.s(df_path, essay_path, sample_path)
    # Setup a callback chain where the result of distribute_task is passed explicitly to prepare_inference_tasks
    callback_chain = distribute_task | prepare_inference_tasks.s()
    # Wrap the callback chain in a chord and set process_csv_paths as the callback
    workflow = chord(
        callback_chain,
        process_csv_paths.s()
    )

    result = workflow.apply_async()
    final_result = result.get()
    print(f"[FINISH] Workflow executed. Output file at {final_result}")


if __name__ == '__main__':
    main()
