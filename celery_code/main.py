from celery import group, chain, chord
from src.celery_app import app, inference_single_csv, distribute_csv_file_no_generate, process_csv_paths


def main():
    df_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/test.csv'
    essay_path = r'/beegfs-FeedBackInfer/input/feedback-prize-effectiveness/test'

    distribute_task = distribute_csv_file_no_generate.s(df_path=df_path, essay_path=essay_path).delay()
    group = (
        [inference_single_csv.s(chunk_df_path, essay_path, sample_df_path)
         for chunk_df_path, essay_path, sample_df_path in distribute_task.get()]
    )
    print(f"[Executing] Generated result from distribute_csv_file_no_generate and prepare_inference_tasks.")
    result_chord = chord(group)(process_csv_paths.s())
    final_result = result_chord.get()
    print(f"[FINISH] Workflow executed. Output file at {final_result}")


if __name__ == '__main__':
    main()
