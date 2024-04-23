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


def is_task_executed(task_id):
    result = app.AsyncResult(task_id)
    return result.status == 'SUCCESS'


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
        if is_task_executed(inference_single_csv.request.id):
            logger.info('\ntask inference_single_csv already executed.\n')
            return
        logger.info('\n---------------task: inference_single_csv-------------------\n')

        df = pd.read_csv(df_path)
        df['essay_text'] = df['essay_id'].apply(lambda x: get_essay(x, essay_folder_path))
        test_dataset = FeedBackDataset(df, CFG.CONFIG['tokenizer'], max_length=CFG.CONFIG['max_length'])
        test_loader = DataLoader(test_dataset, batch_size=CFG.CONFIG['test_batch_size'],
                                 num_workers=1, shuffle=False, pin_memory=True)

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


def process_group(essay_id, group, essay_path):
    chunk_df_path = os.path.join(CFG.GENERATED_CSV_PATH, f'{essay_id}_chunk.csv')
    sample_df_path = os.path.join(CFG.GENERATED_CSV_PATH, f'{essay_id}_sample.csv')

    sample = group[['discourse_id']].copy()
    sample['Ineffective'] = np.nan
    sample['Adequate'] = np.nan
    sample['Effective'] = np.nan

    group.to_csv(chunk_df_path, index=False)
    sample.to_csv(sample_df_path, index=False)

    logger.info(f'{chunk_df_path} and {sample_df_path}.csv SAVED')

    return chunk_df_path, essay_path, sample_df_path


@app.task(name='src.celery_app.distribute_csv_file_no_generate')
def distribute_csv_file_no_generate(df_path, essay_path):
    if is_task_executed(distribute_csv_file_no_generate.request.id):
        logger.info('\ntask distribute_csv_file_no_generate already executed.\n')
        return
    logger.info('\n---------------task: distribute_csv_file_no_generate-------------------\n')

    tasks = []
    data = pd.read_csv(df_path)

    # Group data by 'essay_id'
    grouped = data.groupby('essay_id')

    # if len(grouped) == 1:
    #     logger.info('\n only one essay file\n')
    #     tasks.append((df_path, essay_path, sample_path))
    #     return tasks

    for essay_id, group in grouped:
        tasks.append(process_group(essay_id, group, essay_path))

    logger.info('\n---------------task: distribute_csv_file_no_generate-------------------\n')
    return tasks


@app.task(name='src.celery_app.process_csv_paths')
def process_csv_paths(paths):
    try:

        if is_task_executed(process_csv_paths.request.id):
            logger.info('\ntask process_csv_paths already executed.\n')
            return

        logger.info('\n---------------task: process_csv_paths-------------------\n')
        logger.info(f"Processing CSV paths: {paths}")
        dataframes = []
        for file_path in paths:
            df = pd.read_csv(file_path)
            dataframes.append(df)
        merged_df = pd.concat(dataframes, ignore_index=True)

        final_csv = os.path.join(CFG.SUBMIT_CSV_PATH, 'final.csv')
        merged_df.to_csv(final_csv, index=False)
        logger.info(f"Saved CSV: {final_csv}")
        logger.info('\n---------------task: process_csv_paths-------------------\n')
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

