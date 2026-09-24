# Generator evaluation

## Rubric

A card must fulfill these four criteria to be counted as usable:

1. Answerable - you are able to answer it relying on the produced card.
2. Correct - the answer is actually right.
3. Grammatical - it reads like a question a person would write.
4. Atomic - it tests one fact and not three.

No partial credit. A text producing no cards counts as a failure.

## Method

Both generators run over the same 20 texts. To remove biases the results
are shuffled together into one file labeled A and B, then graded.

## Results (2026-09-13)

| Generator | Cards made | Usable | Usable per text |
|-----------|-----------|--------|-----------------|
| A - rules  | 20 | 12 (60%) | 0.60 |
| B - Gemini | 40 | 39 (98%) | 1.95 |

Model: gemini-3.5-flash-lite.
Seed 42 for the rules run.


## Rules engine failures (8 of 20)

**Grammar (4):** The date pattern inserts the fragment into 
"When did ___?" without changing the verb:

- "When did Docker was first released?"
- "When did GitHub was founded?"
- "When did John Ternus became the CEO of Apple?"
- "When did Jensen Huang co-founded Nvidia?"

**Fill-in-the-blank (4):** The wrong word was blanked:

- "Fill in the blank: _______." (one-word text, no context)
- "Fill in the blank: _______ Of Washington" (almost any word fits)
- "and _______ commit points to the commit before it" (blanks "every")
- "...every insert has to update every _______ on the table" 
(blanks "index", but "Indexes" starts the same sentence)

`create_keyword_card` picks a random keyword and blanks its first occurrence 
without checking whether the word appears elsewhere in the sentence.

## Rules engine successes (12 of 20)

- **Person cards** work with two capitalized words and a known verb: "Who created Git in 2005?" / "Linus Torvalds"


- **Location cards** work for "is in" and "is located in".


- **Inverted definitions** are usable: "What is a column that uniquely identifies each row in a table?" / "primary key"


- **Fill-in-the-blank** works when the key word is blanked: 
"Breadth first search uses a _______ to process nodes" / "queue"

## Gemini failures (1 of 40)

- "What software technology was first released in 2013?" / "Docker". 
The question has many valid answers because the model lost the subject when inverting the sentence.

## Limitations

- **Not blind:** Labels were visible during grading, so treat borderline calls as soft.


- **Rubric gap:** There is no "grounded in source text" criterion. Four Gemini cards came from 
contentless fragments ("Polymorphism.", "University Of Washington") and used outside knowledge. 
They are correct but ignore the prompt. The rubric was frozen before grading, so this run keeps it unchanged.


- **Fragments:** Two of the 20 texts are fragments, and they caused the hallucinations.


- **Small and preliminary:** The test used 20 texts, with one grader who also wrote the set. 
Gemini is non-deterministic, so re-runs will vary.