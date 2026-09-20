from pathlib import Path


DOCS_PATH = Path('./docs')
RAW_PATH = DOCS_PATH / 'raw'
CONVERTED_PATH = DOCS_PATH / 'converted'
HEADERS_TO_SPLIT_ON = [
    ('#', 'Header 1'),
    ('##', 'Header 2'),
    ('###', 'Header 3'),
    ('####', 'Header 4'),
    ('#####', 'Header 5'),
    ('######', 'Header 6'),
]
