import re
import random
from typing import List, Dict
import nltk

# Downloads the NLTK sentence tokenizer just in case
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

# Words that are too common to be useful keywords
FILLER_WORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'it', 'its', 'this', 'that', 'and', 'or', 'but', 'in', 'on', 'at',
    'to', 'for', 'of', 'with', 'by', 'from', 'as'
}


def chunk_text(text: str) -> List[str]:
    """Split text into a list of chunks using NLTK's tokenizer"""
    sentences = nltk.sent_tokenize(text)
    return [s.strip() for s in sentences if s.strip()]

def extract_keywords(sentences: str) -> List[Str]:
    """ Extract potential keywords from sentences """
    tokens = re.findall(r'[a-zA-Z]+', sentences)
    keywords = []
    for word in tokens:
        lower_word = word.lower()
        if lower_word not in FILLER_WORDS and len(word) > 3:
            keywords.append(word)
    return keywords

