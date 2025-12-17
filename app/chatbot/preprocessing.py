import re


def clean_text(text: str) -> str:
    """
    Basic text preprocessing:
    - lowercase
    - remove symbols & numbers
    - remove extra spaces
    """
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()
