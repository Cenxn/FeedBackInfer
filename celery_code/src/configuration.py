from transformers import AutoTokenizer
import torch
import os


class CFG:
    DATA_PATH = '/beegfs-FeedBackInfer/input'
    MODEL_PATHS = [
        os.path.join(DATA_PATH, '/pytorch-feedback-deberta-v3-baseline/Loss-Fold-0.bin'),
        os.path.join(DATA_PATH, '/pytorch-feedback-deberta-v3-baseline/Loss-Fold-1.bin'),
        os.path.join(DATA_PATH, '/pytorch-feedback-deberta-v3-baseline/Loss-Fold-2.bin')
    ]
    ENCODER_PATH = os.path.join(DATA_PATH, "/pytorch-feedback-deberta-v3-baseline/le.pkl")
    TEST_DIR = os.path.join(DATA_PATH, "/feedback-prize-effectiveness/test")
    TEST_CSV = os.path.join(DATA_PATH, "/feedback-prize-effectiveness/test.csv")
    RESULT_PATH = os.path.join(DATA_PATH, "/feedback-prize-effectiveness/sample_submission.csv")
    GENERATED_ESSAY_PATH = '/beegfs-FeedBackInfer/user_input/essay'
    GENERATED_CSV_PATH = '/beegfs-FeedBackInfer/user_input/distributed_csv'
    SUBMIT_CSV_PATH = '/beegfs-FeedBackInfer/output'
    RESULT_PATH = os.path.join(DATA_PATH, "/data/submission.csv")
    CONFIG = dict(
        seed=42,
        model_name='/beegfs-FeedBackInfer/input/debertav3base',
        test_batch_size=16,
        max_length=512,
        num_classes=3,
        device=torch.device("cpu")
    )
    CONFIG["tokenizer"] = AutoTokenizer.from_pretrained(CONFIG['model_name'])
