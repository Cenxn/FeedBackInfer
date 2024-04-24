"""
Extracted from https://www.kaggle.com/code/debarshichanda/feedback-inference
"""
import os
import gc

# For data manipulation
import numpy as np
import pandas as pd

# Pytorch Imports
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

# Utils
from tqdm import tqdm
from celery_code.src.configuration import CFG
from celery_code.src.dataset import FeedBackDataset
from celery_code.src.model import FeedBackModel


def get_essay(essay_id):
    essay_path = os.path.join(CFG.TEST_DIR, f"{essay_id}.txt")
    essay_text = open(essay_path, 'r').read()
    return essay_text


@torch.no_grad()
def valid_fn(model, dataloader, device):
    model.eval()

    PREDS = []

    bar = tqdm(enumerate(dataloader), total=len(dataloader))
    for step, data in bar:
        ids = data['ids'].to(device, dtype=torch.long)
        mask = data['mask'].to(device, dtype=torch.long)

        outputs = model(ids, mask)
        outputs = F.softmax(outputs, dim=1)
        PREDS.append(outputs.cpu().detach().numpy())

    PREDS = np.concatenate(PREDS)
    gc.collect()

    return PREDS


def inference(model_paths, dataloader, device):
    final_preds = []
    for i, path in enumerate(model_paths):
        model = FeedBackModel(CFG.CONFIG['model_name'])
        model.to(CFG.CONFIG['device'])
        model.load_state_dict(torch.load(path, map_location=CFG.CONFIG['device']))

        print(f"Getting predictions for model {i + 1}")
        preds = valid_fn(model, dataloader, device)
        final_preds.append(preds)

    final_preds = np.array(final_preds)
    final_preds = np.mean(final_preds, axis=0)
    return final_preds


def main():
    df = pd.read_csv(CFG.TEST_CSV)
    df['essay_text'] = df['essay_id'].apply(get_essay)

    test_dataset = FeedBackDataset(df, CFG.CONFIG['tokenizer'], max_length=CFG.CONFIG['max_length'])
    test_loader = DataLoader(test_dataset, batch_size=CFG.CONFIG['test_batch_size'],
                             num_workers=2, shuffle=False, pin_memory=True)

    preds = inference(CFG.MODEL_PATHS, test_loader, CFG.CONFIG['device'])
    sample = pd.read_csv(CFG.RESULT_PATH)
    sample['Adequate'] = preds[:, 0]
    sample['Effective'] = preds[:, 1]
    sample['Ineffective'] = preds[:, 2]
    sample.to_csv(CFG.SUBMIT_CSV_PATH, index=False)


if __name__ == '__main__':
    main()
