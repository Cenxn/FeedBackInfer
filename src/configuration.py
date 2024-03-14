from transformers import AutoTokenizer
import torch

class CFG:
    MODEL_PATHS = [
        '/data/input/pytorch-feedback-deberta-v3-baseline/Loss-Fold-0.bin',
        '/data/input/pytorch-feedback-deberta-v3-baseline/Loss-Fold-1.bin',
        '/data/input/pytorch-feedback-deberta-v3-baseline/Loss-Fold-2.bin'
    ]
    ENCODER_PATH = "/data/input/pytorch-feedback-deberta-v3-baseline/le.pkl"
    TEST_DIR = "/data/input/feedback-prize-effectiveness/test"
    TEST_CSV = "/data/input/feedback-prize-effectiveness/test.csv"
    RESULT_PATH = "/data/input/feedback-prize-effectiveness/sample_submission.csv"
    SUBMIT_CSV_PATH = "/data/input/feedback-prize-effectiveness/sample_submission.csv"
    RESULT_PATH = "/data/submission.csv"
    CONFIG = dict(
        seed=42,
        model_name='/data/input/debertav3base',
        test_batch_size=16,
        max_length=512,
        num_classes=3,
        device=torch.device("cpu")
    )
    CONFIG["tokenizer"] = AutoTokenizer.from_pretrained(CONFIG['model_name'])
