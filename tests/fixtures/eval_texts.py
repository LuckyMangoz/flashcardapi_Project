"""Fixed evaluation set for the card generator.

Do not alter during tests.

"""

EVAL_TEXTS = [

    # definitions: OOP, data structures, SQL, Docker
    ("definition", "Encapsulation is a principle that hides an object's internal data "
                   "and exposes only the methods that need to be public."),
    ("definition", "A hash map is a data structure that stores key and value pairs."),
    ("definition", "A primary key is a column that uniquely identifies each row in a table."),
    ("definition", "Docker is a tool that packages an application with everything "
                   "it needs to run."),

    # people
    ("person", "Linus Torvalds created Git in 2005."),
    ("person", "John Ternus became the CEO of Apple in 2026."),
    ("person", "Jensen Huang co-founded Nvidia in 1993."),

    # locations
    ("location", "Nvidia's headquarters is located in Santa Clara, California."),
    ("location", "Microsoft's main campus is in Redmond, Washington."),
    ("location", "Apple is headquartered in Cupertino, California."),

    # dates
    ("date", "GitHub was founded in 2008."),
    ("date", "Docker was first released in 2013."),

    # multi: more than one fact in a sentence
    ("multi", "INNER JOIN returns only the rows that match, while LEFT JOIN keeps "
              "every row from the left table."),
    ("multi", "Git stores snapshots instead of differences, and every commit points "
              "to the commit before it."),

    # process descriptions: no pattern to match
    ("process", "When you run git commit, the files in the staging area are saved as "
                "a new snapshot and the branch pointer moves forward."),
    ("process", "Binary search checks the middle item, throws away the half that cannot "
                "contain the target, and repeats until it finds the item."),
    ("process", "Breadth first search uses a queue to process nodes layer by layer, "
                "visiting all immediate neighbors before moving deeper into the graph."),


    # unstructured prose
    ("prose", "Indexes make reads faster and writes slower, because every insert has to "
              "update every index on the table."),

    # edge case
    ("edge", "Polymorphism."),
    ("edge", "University Of Washington"),

]