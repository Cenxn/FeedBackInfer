import torch
from torch.utils.data import Dataset


class FeedBackDataset(Dataset):
    def __init__(self, df, tokenizer, max_length):
        self.df = df
        self.max_len = max_length
        self.tokenizer = tokenizer
        self.discourse = df['discourse_text'].values
        self.essay = df['essay_text'].values

    def __len__(self):
        return len(self.df)

    def __getitem__(self, index):
        discourse = self.discourse[index]
        essay = self.essay[index]
        text = discourse + " " + self.tokenizer.sep_token + " " + essay
        inputs = self.tokenizer.encode_plus(
            text,
            truncation=True,
            add_special_tokens=True,
            max_length=self.max_len,
            padding='max_length'
        )

        ids = inputs['input_ids']
        mask = inputs['attention_mask']

        return {
            'ids': torch.tensor(ids, dtype=torch.long),
            'mask': torch.tensor(mask, dtype=torch.long)
        }
