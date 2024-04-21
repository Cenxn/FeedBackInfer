from celery import Celery
from celery.utils.log import get_task_logger

import torch
import numpy as np
import pandas as pd
import torch.nn.functional as F
from torch.utils.data import DataLoader
import gc
import os
from tqdm import tqdm

from .configuration import CFG
from .dataset import FeedBackDataset
from .model import FeedBackModel

app = Celery('celery_app',
             broker='redis://:comp0239_cw_zczqmw1@10.0.0.112:6379/0',
             backend='redis://:comp0239_cw_zczqmw1@10.0.0.112:6379/0')
logger = get_task_logger(__name__)

model = FeedBackModel(CFG.CONFIG['model_name'])
model.to(CFG.CONFIG['device'])
model.load_state_dict(torch.load(CFG.MODEL_PATHS[0], map_location=CFG.CONFIG['device']))


@torch.no_grad()
def valid_fn(dataloader):
    model.eval()
    PREDS = []
    bar = tqdm(enumerate(dataloader), total=len(dataloader))
    for step, data in bar:
        ids = data['ids'].to(CFG.CONFIG['device'], dtype=torch.long)
        mask = data['mask'].to(CFG.CONFIG['device'], dtype=torch.long)

        outputs = model(ids, mask)
        outputs = F.softmax(outputs, dim=1)
        PREDS.append(outputs.cpu().detach().numpy())

    PREDS = np.concatenate(PREDS)
    gc.collect()

    return PREDS


def get_essay(essay_id, essay_folder_path):
    essay_path = os.path.join(essay_folder_path, f"{essay_id}.txt")
    essay_text = open(essay_path, 'r').read()
    return essay_text


@app.task(name='src.celery_app.inference_single_csv')
def inference_single_csv(df_path, essay_folder_path, output_csv_path):
    try:
        logger.info('\n---------------task: inference_single_csv-------------------\n')

        df = pd.read_csv(df_path)
        df['essay_text'] = df['essay_id'].apply(lambda x: get_essay(x, essay_folder_path))
        test_dataset = FeedBackDataset(df, CFG.CONFIG['tokenizer'], max_length=CFG.CONFIG['max_length'])
        test_loader = DataLoader(test_dataset, batch_size=CFG.CONFIG['test_batch_size'],
                                 num_workers=2, shuffle=False, pin_memory=True)

        logger.info(f'Starting task with param: {df_path}')

        preds = valid_fn(test_loader)
        sample = pd.read_csv(output_csv_path)
        sample['Adequate'] = preds[:, 0]
        sample['Effective'] = preds[:, 1]
        sample['Ineffective'] = preds[:, 2]

        sample_path = os.path.join(CFG.SUBMIT_CSV_PATH,os.path.basename(output_csv_path))
        sample.to_csv(sample_path, index=False)

        logger.info(f'Saved result to {sample_path}')
        logger.info('\n---------------task: inference_single_csv-------------------\n')
        return sample_path

    except Exception as e:
        logger.error(f"!!! Error processing file {df_path}: {str(e)} !!!")
        raise


@app.task(name='src.celery_app.distribute_csv_file_no_generate')
def distribute_csv_file_no_generate(df_path, essay_path, sample_path):
    logger.info('\n---------------task: distribute_csv_file_no_generate-------------------\n')

    tasks = []
    data = pd.read_csv(df_path)
    total_rows = data.shape[0]
    if total_rows < 5:
        print("Less than 5 records")
        tasks.append((df_path, essay_path, sample_path))
        return tasks

    rows_per_chunk = total_rows // 5
    for i in range(5):
        start_index = i * rows_per_chunk
        if i == 4:
            end_index = total_rows
        else:
            end_index = start_index + rows_per_chunk
        chunk = data.iloc[start_index:end_index]

        sample = chunk[['discourse_id']].copy()
        sample['Adequate'] = np.nan
        sample['Effective'] = np.nan
        sample['Ineffective'] = np.nan

        chunk_df = os.path.join(CFG.GENERATED_CSV_PATH, f'chunk_{i + 1}.csv')
        sample_df = os.path.join(CFG.GENERATED_CSV_PATH, f'sample_{i + 1}.csv')

        chunk.to_csv(chunk_df, index=False)
        sample.to_csv(sample_df, index=False)

        tasks.append((chunk_df, essay_path, sample_df))

        logger.info(f'chunk_{i + 1}.csv and sample_{i + 1}.csv SAVED, {start_index} to {end_index - 1}。')

    logger.info('\n---------------task: distribute_csv_file_no_generate-------------------\n')
    return tasks


@app.task(name='src.celery_app.process_csv_paths')
def process_csv_paths(paths):
    try:
        logger.info('\n---------------task: process_csv_paths-------------------\n')
        logger.info(f"Processing CSV paths: {paths}")
        dataframes = []
        for file_path in paths:
            df = pd.read_csv(file_path)
            dataframes.append(df)
        merged_df = pd.concat(dataframes, ignore_index=True)
        logger.info('\n---------------task: process_csv_paths-------------------\n')

        final_csv = os.path.join(CFG.SUBMIT_CSV_PATH, 'final.csv')
        final_csv.to_csv(merged_df, index=False)
        return final_csv
    except Exception as e:
        logger.error(f"!!! Failed to process CSV paths: {str(e)} !!!")
        raise


# @app.task()
# def distribute_csv_file_with_generate(file_paths):
#     pass


@app.task(bind=True, name='src.celery_app.prepare_inference_tasks')
def prepare_inference_tasks(self, distribute_result):
    # Assuming distribute_result is a list of tuples with (chunk_df, essay_path, sample_df)
    task_signatures = [
        inference_single_csv.s(chunk_df, essay_path, sample_df)
        for chunk_df, essay_path, sample_df in distribute_result
    ]
    return task_signatures

