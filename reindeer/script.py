"""Narration script for 'What If Santa's Reindeer Were Boys?' (v2, ~1 minute).
Facts: reindeer regrow antlers every year; adult males drop theirs in early winter after the autumn rut;
females keep theirs until spring; bulls can lose up to ~25% of their weight in the rut; young males
fight far less and keep their antlers through winter."""
LINES = [
    ("Santa's reindeer are all girls.", ('GIRLS',)),
    ("And the proof is right on their heads.", ('PROOF', 'HEADS')),
    ("Every year, reindeer grow brand new antlers... then drop them.", ('GROW', 'DROP')),
    ("Boy reindeer drop theirs in early winter... way before Christmas.", ('BOY', 'BEFORE')),
    ("Girls keep theirs until spring.", ('GIRLS', 'KEEP')),
    ("So on Christmas Eve, a reindeer with antlers is almost always a girl.", ('ANTLERS', 'GIRL')),
    ("And Santa's reindeer always have antlers.", ('ALWAYS', 'ANTLERS')),
    ("So yes. Even Rudolph is a girl.", ('RUDOLPH', 'GIRL')),
    ("But what if Santa's reindeer were boys?", ('BOYS',)),
    ("By Christmas Eve: nine reindeer, zero antlers.", ('ZERO',)),
    ("And they'd be exhausted. Boys fight all fall... and lose up to a quarter of their weight.", ('EXHAUSTED', 'FIGHTING', 'QUARTER')),
    ("Pulling a sleigh around the world? Santa would never make it.", ('NEVER',)),
    ("Unless they're teenage boys. Young ones barely fight, so they keep their antlers... and their energy.", ('TEENAGE', 'KEEP', 'ENERGY')),
    ("So Santa's team is girls... or teenagers.", ('GIRLS', 'TEENAGERS')),
    ("And Rudolph always has antlers on Christmas Eve. Grown-up boys don't. So the most famous reindeer in the world... is a girl. Merry Christmas.", ('RUDOLPH', "DON'T", 'GIRL', 'CHRISTMAS')),
]
NARRATION = "\n\n".join(l[0] for l in LINES)
CAPTION_BREAKS = [
    "Santa's reindeer | are all girls.",
    "And the proof | is right on their heads.",
    "Every year, | reindeer grow | brand new antlers... | then drop them.",
    "Boy reindeer | drop theirs | in early winter... | way before Christmas.",
    "Girls keep theirs | until spring.",
    "So on Christmas Eve, | a reindeer with antlers | is almost always | a girl.",
    "And Santa's reindeer | always have antlers.",
    "So yes. | Even Rudolph | is a girl.",
    "But what if | Santa's reindeer | were boys?",
    "By Christmas Eve: | nine reindeer, | zero antlers.",
    "And they'd be exhausted. | Boys fight | all fall... | and lose up to | a quarter | of their weight.",
    "Pulling a sleigh | around the world? | Santa would | never make it.",
    "Unless | they're teenage boys. | Young ones | barely fight, | so they keep | their antlers... | and their energy.",
    "So Santa's team | is girls... | or teenagers.",
    "And Rudolph | always has antlers | on Christmas Eve. | Grown-up boys don't. | So the most famous | reindeer in the world... | is a girl. | Merry Christmas.",
]
for brk, (txt, _) in zip(CAPTION_BREAKS, LINES):
    assert brk.replace('|', ' ').split() == txt.split(), txt
