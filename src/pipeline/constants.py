from pathlib import Path

from pydantic import AnyUrl


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / 'data'
ANSWERS_PATH = DATA_DIR / 'answers.json'
QUESTIONS_PATH = DATA_DIR / 'questions.json'

DOCS_DIR = PROJECT_ROOT / 'docs'
RAW_PATH = DOCS_DIR / 'raw'
CONVERTED_PATH = DOCS_DIR / 'converted'

HF_URL = AnyUrl('https://router.huggingface.co/v1/chat/completions')
HEADERS_TO_SPLIT_ON = [
    ('#', 'Header 1'),
    ('##', 'Header 2'),
    ('###', 'Header 3'),
    ('####', 'Header 4'),
    ('#####', 'Header 5'),
    ('######', 'Header 6'),
]
