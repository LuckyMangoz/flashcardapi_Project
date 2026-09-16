"""Evaluates and scores the card generator models.

Run these from the repo root, following this order:

    python scripts/evaluate.py run rules
    python scripts/evaluate.py run llm
    python scripts/evaluate.py mix
    python scripts/evaluate.py score

Use -m: It puts the current folder on the import path
"""
import csv
import os
import random
import sys
import time

from tests.fixtures.eval_texts import EVAL_TEXTS

SEED = 42
CARDS_PER_TEXT = 2
SECONDS_BETWEEN_API_CALLS = 5

RULES_FILE = "docs/eval_rules.csv"
LLM_FILE = "docs/eval_llm.csv"
MIXED_FILE = "docs/eval_mixed.csv"
KEY_FILE = "docs/eval_key.txt"


def read_csv(path):
    """Read a CSV file into a list of dictionaries."""
    rows = []
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def write_csv(path, header, rows):
    """Write one header row and then all the data rows."""
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)


def percent(part, whole):
    """Work out a percentage. Returns 0 instead of crashing on an empty set."""
    if whole == 0:
        return 0
    return round(part / whole * 100)


def run(generator_name):
    """Run one generator over every eval text and save the cards to a CSV."""
    if generator_name == "rules":
        from app.generators import rules
        output_file = RULES_FILE
        pause = 0
    elif generator_name == "llm":
        from app.generators import llm
        output_file = LLM_FILE
        pause = SECONDS_BETWEEN_API_CALLS
    else:
        print("Unknown generator. Use 'rules' or 'llm'.")
        return

    os.makedirs("docs", exist_ok=True)
    random.seed(SEED)

    rows = []
    empty_count = 0
    text_number = 0

    for kind, text in EVAL_TEXTS:
        text_number = text_number + 1
        print(f"[{text_number}/{len(EVAL_TEXTS)}] {text[:50]}")

        if generator_name == "rules":
            cards = rules.generate_cards(text, num=CARDS_PER_TEXT)
        else:
            cards = llm.generate(text, num=CARDS_PER_TEXT)

        if len(cards) == 0:
            empty_count = empty_count + 1
            rows.append([kind, text, "(no cards generated)", ""])
        else:
            for card in cards:
                rows.append([kind, text, card["question"], card["answer"]])

        if pause > 0:
            time.sleep(pause)

    write_csv(output_file, ["kind", "source", "question", "answer"], rows)

    print("")
    print(f"{len(EVAL_TEXTS)} texts produced {len(rows)} cards")
    print(f"{empty_count} texts produced nothing at all")
    print(f"Wrote {output_file}")


def mix():
    """Put both sets of cards in one file, labelled A and B, and shuffle them."""
    rows = []

    for row in read_csv(RULES_FILE):
        rows.append(["A", row["kind"], row["source"],
                     row["question"], row["answer"], ""])

    for row in read_csv(LLM_FILE):
        rows.append(["B", row["kind"], row["source"],
                     row["question"], row["answer"], ""])

    random.seed(SEED)
    random.shuffle(rows)

    header = ["set", "kind", "source", "question", "answer", "usable"]
    write_csv(MIXED_FILE, header, rows)

    with open(KEY_FILE, "w", encoding="utf-8") as f:
        f.write("A = rules\n")
        f.write("B = llm\n")

    print(f"Wrote {MIXED_FILE} with {len(rows)} cards")
    print(f"Wrote {KEY_FILE}")
    print("Grade eval_mixed.csv. Do not open eval_key.txt until you are finished.")


def score():
    """Count how many cards in each set were marked usable."""
    rules_usable = 0
    rules_total = 0
    llm_usable = 0
    llm_total = 0
    ungraded = 0

    for row in read_csv(MIXED_FILE):
        mark = row["usable"].strip()

        if mark != "0" and mark != "1":
            ungraded = ungraded + 1
            continue

        if row["set"] == "A":
            rules_total = rules_total + 1
            if mark == "1":
                rules_usable = rules_usable + 1
        else:
            llm_total = llm_total + 1
            if mark == "1":
                llm_usable = llm_usable + 1

    if ungraded > 0:
        print(f"WARNING: {ungraded} cards have not been graded yet")
        print("")

    rules_percent = percent(rules_usable, rules_total)
    llm_percent = percent(llm_usable, llm_total)

    print(f"Set A (rules): {rules_usable} of {rules_total} usable ({rules_percent}%)")
    print(f"Set B (llm):   {llm_usable} of {llm_total} usable ({llm_percent}%)")


if __name__ == "__main__":
    arguments = sys.argv[1:]

    if len(arguments) == 2 and arguments[0] == "run":
        run(arguments[1])
    elif len(arguments) == 1 and arguments[0] == "mix":
        mix()
    elif len(arguments) == 1 and arguments[0] == "score":
        score()
    else:
        print(__doc__)