"""Script for 'What If Rudolph's Nose Was Real?' (narrated by Jett).
(caption text = exactly what is said, text sent to the voice with acting tags, highlight words)
Facts: a 2012 BMJ study used thermal imaging and found reindeer noses glow red with heat; their nasal
lining has a much denser network of blood vessels than humans', which keeps the nose warm and stops it
freezing. Arctic reindeer eyes (tapetum) shift from gold in summer to deep blue in the dark winter, which
gathers more light. Reindeer can see ultraviolet light: snow reflects UV, while lichen and wolf fur absorb
it, so they stand out dark against the bright snow."""
LINES = [
    ("Rudolph's red nose is real.", "Rudolph's red nose... is real.", ('REAL',)),
    ("WHAAAAT?!", "[shouting] WHAAAAT?!", ('WHAAAAT',)),
    ("Scientists pointed a heat camera at real reindeer in the snow...", "Scientists pointed a heat camera at real reindeer in the snow...", ('HEAT',)),
    ("and their noses lit up bright red.", "[excited] and their noses lit up bright red.", ('RED',)),
    ("Here's why. Reindeer noses are packed with tiny blood vessels. Way more than ours.", "Here's why. Reindeer noses are packed with tiny blood vessels. Way more than ours.", ('BLOOD', 'MORE')),
    ("In the Arctic, it gets down to minus forty.", "In the Arctic, it gets down to [intense] minus forty.", ('MINUS', 'FORTY')),
    ("So warm blood rushes to the nose, to keep it from freezing while they sniff for food under the snow.", "So warm blood rushes to the nose, to keep it from freezing while they sniff for food under the snow.", ('WARM', 'FREEZING')),
    ("So what if Rudolph's nose really glowed?", "[excited] So what if Rudolph's nose really glowed?", ('GLOWED',)),
    ("To a heat camera, it does. Every reindeer is a Rudolph.", "To a heat camera... it does. [excited] Every reindeer is a Rudolph.", ('DOES', 'EVERY')),
    ("But plot twist... that's not even their best superpower.", "But plot twist... [shouting] that's not even their best superpower.", ('TWIST', 'SUPERPOWER')),
    ("Reindeer eyes change color. Gold in summer, blue in winter.", "Reindeer eyes change color. Gold in summer... [excited] blue in winter.", ('GOLD', 'BLUE')),
    ("The Arctic winter stays dark for weeks. Blue eyes catch more light, so they can see in the dark.", "The Arctic winter stays dark for weeks. Blue eyes catch more light, so they can see in the dark.", ('DARK', 'LIGHT')),
    ("And they see ultraviolet light. Snow reflects it, so food and wolves stand out dark against the glowing snow.", "And they see ultraviolet light. Snow reflects it, so food and wolves stand out dark against the glowing snow.", ('ULTRAVIOLET', 'WOLVES')),
    ("So they find food, and spot wolves before the wolves spot them.", "So they find food... and spot wolves [intense] before the wolves spot them.", ('FOOD', 'BEFORE')),
    ("A glowing nose, and night vision.", "[intense] A glowing nose... and night vision.", ('GLOWING', 'NIGHT')),
    ("Santa didn't pick reindeer by accident. Merry Christmas.", "Santa didn't pick reindeer by accident. [excited] Merry Christmas.", ('ACCIDENT', 'CHRISTMAS')),
]
TTS = "\n\n".join(l[1] for l in LINES)
CAPTION_BREAKS = [
    "Rudolph's red nose | is real.",
    "WHAAAAT?!",
    "Scientists pointed | a heat camera | at real reindeer | in the snow...",
    "and their noses | lit up bright red.",
    "Here's why. | Reindeer noses | are packed with | tiny blood vessels. | Way more than ours.",
    "In the Arctic, | it gets down to | minus forty.",
    "So warm blood | rushes to the nose, | to keep it | from freezing | while they sniff for food | under the snow.",
    "So what if | Rudolph's nose | really glowed?",
    "To a heat camera, | it does. | Every reindeer | is a Rudolph.",
    "But plot twist... | that's not even | their best superpower.",
    "Reindeer eyes | change color. | Gold in summer, | blue in winter.",
    "The Arctic winter | stays dark for weeks. | Blue eyes | catch more light, | so they can see | in the dark.",
    "And they see | ultraviolet light. | Snow reflects it, | so food and wolves | stand out dark | against the glowing snow.",
    "So they find food, | and spot wolves | before the wolves | spot them.",
    "A glowing nose, | and night vision.",
    "Santa didn't pick | reindeer by accident. | Merry Christmas.",
]
for brk, (txt, _, _) in zip(CAPTION_BREAKS, LINES):
    assert brk.replace('|', ' ').split() == txt.split(), txt
