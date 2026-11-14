"""Narration script for 'What If Santa's Reindeer Were Boys?' (one entry per voice line).
Each line: (narration, caption chunks, highlight words). Facts: male reindeer shed antlers in early
winter after the autumn rut; females keep theirs until spring; bulls can lose ~20-25% of their
body weight during the rut; young males keep their antlers longer than adult bulls."""
LINES = [
    ("Santa's reindeer are all girls.", ["SANTA'S REINDEER", "ARE ALL GIRLS."], ('GIRLS',)),
    ("Look at the antlers.", ["LOOK AT", "THE ANTLERS."], ('ANTLERS',)),
    ("Boy reindeer drop their antlers in early winter... way before Christmas.", ["BOYS DROP", "THEIR ANTLERS", "IN EARLY WINTER...", "BEFORE CHRISTMAS."], ('DROP', 'BEFORE')),
    ("Girls keep theirs all winter long.", ["GIRLS KEEP THEIRS", "ALL WINTER."], ('KEEP', 'WINTER')),
    ("So every reindeer pulling Santa's sleigh on Christmas Eve...", ["SO EVERY REINDEER", "PULLING THE SLEIGH", "ON CHRISTMAS EVE..."], ('EVERY', 'CHRISTMAS')),
    ("is a girl. Yes. Even Rudolph.", ["IS A GIRL.", "EVEN RUDOLPH."], ('GIRL', 'RUDOLPH')),
    ("So what if Santa's reindeer were boys?", ["SO WHAT IF THEY", "WERE BOYS?"], ('BOYS',)),
    ("Nine reindeer. Zero antlers.", ["NINE REINDEER.", "ZERO ANTLERS."], ('ZERO',)),
    ("And they'd be exhausted. Boys spend the whole fall fighting... and lose up to a quarter of their weight.", ["AND EXHAUSTED.", "THEY FIGHT", "ALL FALL...", "AND LOSE A QUARTER", "OF THEIR WEIGHT."], ('EXHAUSTED', 'FIGHT', 'QUARTER')),
    ("Santa would never make it.", ["SANTA WOULD", "NEVER MAKE IT."], ('NEVER',)),
    ("Unless they're teenage boys. Young ones keep their antlers longer.", ["UNLESS THEY'RE", "TEENAGE BOYS.", "YOUNG ONES KEEP", "THEIRS LONGER."], ('TEENAGE', 'LONGER')),
    ("But Rudolph? Definitely a girl. Merry Christmas.", ["BUT RUDOLPH?", "DEFINITELY A GIRL.", "MERRY CHRISTMAS."], ('RUDOLPH', 'GIRL', 'CHRISTMAS')),
]
NARRATION = "\n\n".join(l[0] for l in LINES)
