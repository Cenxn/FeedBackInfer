from celery import group, chain, chord

from src.celery_app import app, distribute_csv_file_no_generate, inference_single_csv, process_csv_paths


@app.task
def prepare_inference_tasks(distribute_result):
    # Returns a list of task ready to be used in a group call.
    return [inference_single_csv.s(chunk_df, sample_df, essay_path) for chunk_df, sample_df, essay_path in distribute_result]


def main():
    df_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/test.csv'
    essay_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/test'
    sample_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/sample_submission.csv'

    # Chain to distribute tasks, then process all results in a group and consolidate the data to process_csv_paths.
    workflow = chord(
        (distribute_csv_file_no_generate.s(df_path, essay_path, sample_path) | prepare_inference_tasks()),
        process_csv_paths.s()
    )

    result = workflow.apply_async()
    final_result = result.get()
    print(f"[FINISH] Workflow executed. Output file at {final_result}")


if __name__ == '__main__':
    main()
