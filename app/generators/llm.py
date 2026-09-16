"""Card generation using Gemini API."""
import os
from dotenv import load_dotenv
from google import genai
import json
import logging
import time

from app import config

log = logging.getLogger(__name__)

MAX_QUESTION_LENGTH = 400
MAX_ANSWER_LENGTH = 800

SYSTEM_PROMPT = """You write study flashcards from a passage of text.

Rules for every card:
- The question must be answerable by someone who has NOT seen the source text.
- Never invert a definition. Ask "What is Python?" rather than
  "What is a programming language?".
- One fact per card. Split compound sentences into separate cards.
- No yes or no questions.
- Keep the answer short: a word, a name, a date, or one clear sentence.
- Only use facts that are in the text. Do not add outside knowledge.

Set difficulty to 1 for direct recall and 2 if it needs any thinking."""

CARD_SCHEMA = {
    "type": "object",
    "properties": {
        "cards": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "answer": {"type": "string"},
                    "type": {
                        "type": "string",
                        "enum": ["definition", "person", "date", "location", "concept"],
                    },
                    "difficulty": {"type": "integer"},
                },
                "required": ["question", "answer", "type", "difficulty"],
            },
        }
    },
    "required": ["cards"],
}


def _call_api(text, num):
    """The only function that talks to Google. Swapped for a fake in tests."""

    client = genai.Client(api_key=config.LLM_API_KEY)

    prompt = f"{SYSTEM_PROMPT}\n\nWrite exactly {num} flashcards from this text:\n\n{text}"

    interaction = client.interactions.create(
        model=config.LLM_MODEL,
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": CARD_SCHEMA,
        },
    )

    return json.loads(interaction.output_text)


def _validate(payload, num):
    """Check the response before we trust it. Returns only the good cards."""
    cards = payload.get("cards")

    if not isinstance(cards, list):
        log.warning("The response had no 'cards' list")
        return []

    good_cards = []

    for card in cards:
        if len(good_cards) >= num:
            break

        question = card.get("question", "")
        answer = card.get("answer", "")

        if not isinstance(question, str) or not isinstance(answer, str):
            log.warning("Skipped a card because a field was not text")
            continue

        question = question.strip()
        answer = answer.strip()

        if question == "" or answer == "":
            log.warning("Skipped a card because a field was empty")
            continue

        if len(question) > MAX_QUESTION_LENGTH:
            log.warning("Skipped a card because the question was too long")
            continue

        if len(answer) > MAX_ANSWER_LENGTH:
            log.warning("Skipped a card because the answer was too long")
            continue

        good_card = {
            "question": question,
            "answer": answer,
            "type": card.get("type", "concept"),
            "difficulty": card.get("difficulty", 1),
        }
        good_cards.append(good_card)

    return good_cards


def generate(text, num=5):
    """Ask Gemini for flashcards. Returns a list, possibly empty."""
    if config.LLM_API_KEY == "" or config.LLM_MODEL == "":
        log.warning("LLM_API_KEY or LLM_MODEL is missing from .env")
        return []

    start_time = time.perf_counter()

    payload = _call_api(text, num)
    cards = _validate(payload, num)

    seconds = time.perf_counter() - start_time
    log.info(f"Gemini returned {len(cards)} usable cards in {seconds:.2f} seconds")

    return cards