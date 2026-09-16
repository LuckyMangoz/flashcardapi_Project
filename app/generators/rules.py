import re
import random
from typing import List, Dict, Optional
import nltk

# Downloads the NLTK sentence tokenizer just in case
for _resource in ('punkt', 'punkt_tab'):
    try:
        nltk.data.find(f'tokenizers/{_resource}')
    except (LookupError, OSError):
        nltk.download(_resource, quiet=True)

# Words that are too common to be useful keywords
FILLER_WORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'it', 'its', 'this', 'that', 'and', 'or', 'but', 'in', 'on', 'at',
    'to', 'for', 'of', 'with', 'by', 'from', 'as'
}


def split_into_sentences(text: str) -> List[str]:
    """Split text into a list of chunks using NLTK's tokenizer"""
    sentences = nltk.sent_tokenize(text)
    return [s.strip() for s in sentences if s.strip()]


def extract_keywords(sentence: str) -> List[str]:
    """Picks useful words from a sentence that could be used as keywords."""
    tokens = re.findall(r'[a-zA-Z]+', sentence)
    keywords = []
    for word in tokens:
        lower_word = word.lower()
        if lower_word not in FILLER_WORDS and len(word) > 3:
            keywords.append(word)
    return keywords


def create_definition_card(sentence: str) -> Optional[Dict[str, str]]:
    """Try to make a definition card: 'X is/are a/an/the Y'."""
    match = re.search(
        r'([^.]+) (is|are|was|were) (a|an|the) ([^.]+)',
        sentence,
        re.IGNORECASE
    )
    if match:
        subject = match.group(1).strip()
        subject = re.sub(r'^(the|a|an)\s+', '', subject, flags=re.IGNORECASE)
        return {
            'question': f"What {match.group(2)} {match.group(3)} {match.group(4).strip()}?",
            'answer': subject,
            'type': 'definition'
        }
    return None


def create_person_card(sentence: str) -> Optional[Dict[str, str]]:
    """Try to make a person card: 'FirstName LastName created/invented/wrote ...'."""
    match = re.search(
        r'([A-Z][a-z]+ [A-Z][a-z]+) (created|invented|discovered|developed|founded|wrote) ([^.]+)',
        sentence
    )
    if match:
        return {
            'question': f"Who {match.group(2)} {match.group(3).strip()}?",
            'answer': match.group(1),
            'type': 'person'
        }
    return None


def create_date_card(sentence: str) -> Optional[Dict[str, str]]:
    """Try to make a date card: '... in/on/during YYYY ...'."""
    match = re.search(
        r'([^.]*)(in|on|during) (the year )?(\d{4})([^.]*)',
        sentence,
        re.IGNORECASE
    )
    if match:
        before = match.group(1).strip()
        after = match.group(5).strip()
        context = (before + ' ' + after).strip()
        context = re.sub(r'^(the|a|an)\s+', '', context, flags=re.IGNORECASE)
        if context:
            return {
                'question': f"When did {context}?",
                'answer': match.group(4),
                'type': 'date'
            }
    return None


def create_keyword_card(sentence: str) -> Optional[Dict[str, str]]:
    """Fallback card – blank out a random keyword (whole word only)."""
    keywords = extract_keywords(sentence)
    if not keywords:
        return None
    keyword = random.choice(keywords)

    # Use regex word boundaries to replace only whole words
    pattern = re.compile(r'\b' + re.escape(keyword) + r'\b')
    question_text = pattern.sub('_______', sentence, 1)

    return {
        'question': f"Fill in the blank: {question_text}",
        'answer': keyword,
        'type': 'fill_blank'
    }


def create_location_card(sentence: str) -> Optional[Dict[str, str]]:
    """Try to make a location card: 'X is located in/in/ lies in Y'."""
    match = re.search(
        r'([^.]+) (is located in|is in|lies in) ([^.]+)',
        sentence,
        re.IGNORECASE
    )
    if match:
        place = match.group(1).strip()
        location = match.group(3).strip()
        return {
            'question': f"Where is {place}?",
            'answer': location,
            'type': 'location'
        }
    return None


def generate_cards(text: str, num: int = 5) -> List[Dict]:
    """Create a list of flashcard dictionaries from the given text."""
    sentences = split_into_sentences(text)
    cards = []
    used_sentences = set()

    creators = [
        create_definition_card,
        create_person_card,
        create_date_card,
        create_location_card
    ]

    for sentence in sentences:
        if sentence in used_sentences:
            continue
        for creator in creators:
            card = creator(sentence)
            if card:
                cards.append(card)
                used_sentences.add(sentence)
                break

    if len(cards) < num:
        for sentence in sentences:
            if sentence in used_sentences:
                continue
            card = create_keyword_card(sentence)
            if card:
                cards.append(card)
                used_sentences.add(sentence)
            if len(cards) >= num:
                break

    result = cards[:num]
    for i, card in enumerate(result):
        card['id'] = i + 1
        card['difficulty'] = 1 if card['type'] == 'definition' else 2

    return result


if __name__ == '__main__':
    sample = (
        "A group of crows is a murder.",
        "Lamos Creano invented something.",
        "The first iPhone was released during the year 2007.",
        "A cloud can weigh more than a million pounds."
    )

    for text in sample:
        for c in generate_cards(text, num=1):
            print(c)
