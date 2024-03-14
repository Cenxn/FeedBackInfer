import pandas as pd
import os


FILE_PATH = r"D:\RUI\warehourse\feedback-prize-effectiveness"


def drop_specific_column(old_path, new_path):
    df = pd.read_csv(old_path)
    df = df.drop('discourse_effectiveness', axis=1)
    df.to_csv(new_path, index=False)
    print(f'[SUCCESS] generate {new_path} from {old_path}')


def combine_csv(first_file, second_file, new_path):
    df1 = pd.read_csv(first_file)
    df2 = pd.read_csv(second_file)

    merged_df = pd.concat([df1, df2])

    merged_df.to_csv(new_path, index=False)
    print(f'[SUCCESS] combine {first_file} with {second_file} as {new_path}')


def generate_submission_csv(csv_path, output_csv_path):
    df = pd.read_csv(csv_path)
    discourse_ids = df['discourse_id']
    df_new = pd.DataFrame({
        'discourse_id': discourse_ids,
        'Ineffective': [0] * len(discourse_ids),
        'Adequate': [0] * len(discourse_ids),
        'Effective': [0] * len(discourse_ids)
    })
    df_new.to_csv(output_csv_path, index=False)
    print(f'[SUCCESS] generate {output_csv_path} from {csv_path}')


def main():
    drop_specific_column(old_path=os.path.join(FILE_PATH, 'train.csv'),
                         new_path=os.path.join(FILE_PATH, 'new_train.csv'))
    combine_csv(first_file=os.path.join(FILE_PATH, 'new_train.csv'),
                second_file=os.path.join(FILE_PATH, 'test.csv'),
                new_path=os.path.join(FILE_PATH, 'new_test.csv'))
    generate_submission_csv(csv_path=os.path.join(FILE_PATH, 'new_test.csv'),
                            output_csv_path=os.path.join(FILE_PATH, 'new_result.csv'))


if __name__ == '__main__':
    main()
