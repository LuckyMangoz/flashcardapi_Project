from app import config
from app.generators import llm, generate_cards

GOOD_RESPONSE = {
    "cards": [
        {
            "question": "Who created Git in 2005?",
            "answer": "Linus Torvalds",
            "type": "person",
            "difficulty": 1,
        }
    ]
}

EMPTY_QUESTION_RESPONSE = {
    "cards": [
        {
            "question": "   ",
            "answer": "Linus Torvalds",
            "type": "person",
            "difficulty": 1,
        }
    ]
}


def fake_api_good(text, num):
    return GOOD_RESPONSE


def fake_api_empty_question(text, num):
    return EMPTY_QUESTION_RESPONSE


def fake_api_crashes(text, num):
    raise ConnectionError("API unreachable")


def pretend_key_is_set(monkeypatch):
    """So generate() does not stop early on the missing key check."""
    monkeypatch.setattr(config, "LLM_API_KEY", "test-key")
    monkeypatch.setattr(config, "LLM_MODEL", "test-model")


def test_good_response_is_parsed(monkeypatch):
    pretend_key_is_set(monkeypatch)
    monkeypatch.setattr(llm, "_call_api", fake_api_good)

    cards = llm.generate("Linus Torvalds created Git in 2005.", 1)

    assert len(cards) == 1
    assert cards[0]["answer"] == "Linus Torvalds"


def test_empty_question_is_skipped(monkeypatch):
    pretend_key_is_set(monkeypatch)
    monkeypatch.setattr(llm, "_call_api", fake_api_empty_question)

    cards = llm.generate("anything", 1)

    assert cards == []


def test_api_failure_falls_back_to_rules(monkeypatch):
    pretend_key_is_set(monkeypatch)
    monkeypatch.setattr(config, "CARD_GENERATOR", "llm")
    monkeypatch.setattr(llm, "_call_api", fake_api_crashes)

    cards = generate_cards("Linus Torvalds created Git in 2005.", 1)

    assert len(cards) == 1
    assert cards[0]["answer"] == "Linus Torvalds"