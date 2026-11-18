"""Script for 'What If Being Always Cold Made You a Genius?' (Jett). Straight-to-camera, talks to YOU, no story.
Facts: Kingma & van Marken Lichtenbelt (2015, Nature Climate Change): thermal-comfort standards rest partly on the
resting metabolic rate of a ~40-year-old, ~70 kg man; this can overestimate women's metabolic rate by up to 35%,
so rooms run too cold for many women (small study). Chang & Kajackaite (2019, PLOS ONE, N=543): women did better on
math and verbal tasks at warmer temperatures; men did slightly better cooler."""
LINES = [
    ("People who are always cold...", "People who are always cold...", ('COLD',)),
    ("are GENIUSES!", "[shouting] are GENIUSESSS!", ('GENIUSES',)),
    ("Picture this. Christmas at your family's house. Everyone's in T-shirts. You? Two hoodies, a blanket, and you're still shaking.", "Picture this. Christmas at your family's house. Everyone's in T-shirts. You? Two hoodies... a blanket... and you're STILL shaking.", ('T-SHIRTS', 'HOODIES', 'SHAKING')),
    ("And someone always says, it's not even cold, stop being dramatic.", "And someone always says... [sarcastic] it's not even cold, stop being dramatic.", ('DRAMATIC',)),
    ("But here's the thing. You're not dramatic.", "But here's the thing. [intense] You're not dramatic.", ('NOT',)),
    ("If you've ever stolen the blanket... SUBSCRIBE!", "If you've ever stolen the blanket... [shouting] SUBSCRIBE!", ('SUBSCRIBE',)),
    ("A lot of thermostat settings come from an old formula based on a 40-year-old man in a suit.", "A lot of thermostat settings come from an old formula... based on a forty-year-old man in a suit.", ('FORMULA', '40-YEAR-OLD', 'SUIT')),
    ("Scientists found it can run way too cold for lots of people, especially women, who burn less heat just sitting still.", "Scientists found it can run way too cold for lots of people... especially women, who burn less heat just sitting still.", ('COLD', 'WOMEN')),
    ("So the room was literally set for someone else.", "So the room was literally set for someone else.", ('SOMEONE', 'ELSE')),
    ("And here's the genius part nobody tells you...", "[intense] And here's the genius part nobody tells you...", ('GENIUS', 'NOBODY')),
    ("In one study, women did better on math and word tests in warmer rooms.", "In one study, women did better on math and word tests... [excited] in warmer rooms.", ('BETTER', 'WARMER')),
    ("So when you crank the heat, you're not being dramatic. You might literally be thinking better.", "So when you crank the heat, you're not being dramatic. [excited] You might literally be thinking better.", ('HEAT', 'BETTER')),
    ("The catch? Now everyone else is sweating.", "The catch? [laughs] Now everyone else is sweating.", ('CATCH', 'SWEATING')),
    ("So grab the blanket, own the thermostat, and stay cozy, genius.", "So grab the blanket... own the thermostat... [excited] and stay cozy, genius.", ('BLANKET', 'THERMOSTAT', 'GENIUS')),
    ("Tag the blanket thief you know... or Santa's putting you on the naughty list.", "Tag the blanket thief you know... [mischievous] or Santa's putting you on the naughty list.", ('TAG', 'THIEF', 'NAUGHTY')),
]
TTS = "\n\n".join(l[1] for l in LINES)
CAPTION_BREAKS = [
    "People who | are always cold...",
    "are GENIUSES!",
    "Picture this. | Christmas at | your family's house. | Everyone's in T-shirts. | You? | Two hoodies, | a blanket, | and you're still shaking.",
    "And someone always says, | it's not even cold, | stop being dramatic.",
    "But here's the thing. | You're not dramatic.",
    "If you've ever | stolen the blanket... | SUBSCRIBE!",
    "A lot of | thermostat settings | come from an old formula | based on a | 40-year-old man | in a suit.",
    "Scientists found | it can run way too cold | for lots of people, | especially women, | who burn less heat | just sitting still.",
    "So the room | was literally set | for someone else.",
    "And here's the genius part | nobody tells you...",
    "In one study, | women did better | on math and word tests | in warmer rooms.",
    "So when you | crank the heat, | you're not | being dramatic. | You might literally | be thinking better.",
    "The catch? | Now everyone else | is sweating.",
    "So grab the blanket, | own the thermostat, | and stay cozy, | genius.",
    "Tag the blanket thief | you know... | or Santa's putting you | on the naughty list.",
]
for brk, (txt, _, _) in zip(CAPTION_BREAKS, LINES):
    assert brk.replace('|', ' ').split() == txt.split(), txt
