"""Card generation process. Tries the LLM first falls back to the rules engine if needed."""

import logging

from app import config
from app.generators import rules

log = logging.getLogger(__name__)


def try_llm(text, num):
    """Ask the LLM for cards. Returns an empty list if anything goes wrong."""
    try:
        from app.generators import llm
        return llm.generate(text, num)
    except Exception:
        log.exception("The LLM call failed")
        return []


def generate_cards(text, num=5):
    """Make flashcards. Always returns a list, never raises."""
    if config.CARD_GENERATOR == "llm":
        cards = try_llm(text, num)

        if len(cards) > 0:
            return cards

        log.warning("No cards from the LLM, using the rules engine instead")

    return rules.generate_cards(text, num)