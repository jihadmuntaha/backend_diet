import re

STOPWORDS = {
    "yang","dan","di","ke","dari","itu","ini","adalah","apa",
    "bagaimana","cara","untuk","dengan","pada"
}

def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOPWORDS]
    return " ".join(tokens)
