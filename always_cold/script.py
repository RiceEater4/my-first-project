"""Script for 'What If Being Always Cold Made You a Genius?' v2 - direct, command-style (Jett). Talks to YOU.
Facts: Kingma & van Marken Lichtenbelt (2015, Nature Climate Change): comfort standards rest partly on the resting
metabolic rate of a ~40-year-old man; can overestimate women's metabolic rate by up to 35% (small study).
Chang & Kajackaite (2019, PLOS ONE, N=543): women did better on math and verbal tasks in warmer rooms."""
LINES = [
    ("People who are always cold...", "People who are always cold...", ('COLD',)),
    ("are GENIUSES!", "[shouting] are GENIUSESSS!", ('GENIUSES',)),
    ("Look around the room. Everyone's in T-shirts. You? Two hoodies. A blanket. Still shaking.", "Look around the room. Everyone's in T-shirts. You? Two hoodies. A blanket. [excited] STILL shaking.", ('T-SHIRTS', 'HOODIES', 'SHAKING')),
    ("Someone calls you dramatic. Ignore them. Your body isn't broken. The room is.", "Someone calls you dramatic. Ignore them. Your body isn't broken... [intense] the room is.", ('DRAMATIC', 'IGNORE', 'ROOM')),
    ("Blanket thieves... SUBSCRIBE!", "Blanket thieves... [shouting] SUBSCRIBE!", ('SUBSCRIBE',)),
    ("Walk up to the thermostat. Those settings come from an old formula, built around a 40-year-old man in a suit. Not you. Him.", "Walk up to the thermostat. Those settings come from an old formula... built around a forty-year-old man in a suit. Not you. [intense] Him.", ('THERMOSTAT', '40-YEAR-OLD', 'HIM')),
    ("Women burn less heat just sitting still. So that normal room is freezing for a lot of people.", "Women burn less heat just sitting still. So that normal room... is freezing for a lot of people.", ('LESS', 'FREEZING')),
    ("Now here's the genius part nobody tells you...", "[intense] Now here's the genius part nobody tells you...", ('GENIUS', 'NOBODY')),
    ("Turn the heat up. In one study, women did better on math and word tests in warmer rooms.", "Turn the heat up. In one study, women did better on math and word tests... [excited] in warmer rooms.", ('HEAT', 'BETTER', 'WARMER')),
    ("So crank it. Grab the blanket. Own the thermostat. You're not dramatic, you might literally be thinking better.", "So crank it. Grab the blanket. Own the thermostat. You're not dramatic... [excited] you might literally be thinking better.", ('CRANK', 'BLANKET', 'THERMOSTAT', 'BETTER')),
    ("The catch? Everyone else starts sweating. Not your problem.", "The catch? Everyone else starts sweating. [laughs] Not your problem.", ('CATCH', 'SWEATING')),
    ("Tag the blanket thief you know... or Santa's putting you on the naughty list.", "Tag the blanket thief you know... [mischievous] or Santa's putting you on the naughty list.", ('TAG', 'THIEF', 'NAUGHTY')),
]
TTS = "\n\n".join(l[1] for l in LINES)
CAPTION_BREAKS = [
    "People who | are always cold...",
    "are GENIUSES!",
    "Look around the room. | Everyone's in T-shirts. | You? | Two hoodies. | A blanket. | Still shaking.",
    "Someone calls you | dramatic. | Ignore them. | Your body | isn't broken. | The room is.",
    "Blanket thieves... | SUBSCRIBE!",
    "Walk up to | the thermostat. | Those settings come | from an old formula, | built around | a 40-year-old man | in a suit. | Not you. | Him.",
    "Women burn less heat | just sitting still. | So that normal room | is freezing | for a lot of people.",
    "Now here's | the genius part | nobody tells you...",
    "Turn the heat up. | In one study, | women did better | on math and word tests | in warmer rooms.",
    "So crank it. | Grab the blanket. | Own the thermostat. | You're not dramatic, | you might literally | be thinking better.",
    "The catch? | Everyone else | starts sweating. | Not your problem.",
    "Tag the blanket thief | you know... | or Santa's putting you | on the naughty list.",
]
for brk, (txt, _, _) in zip(CAPTION_BREAKS, LINES):
    assert brk.replace('|', ' ').split() == txt.split(), txt
