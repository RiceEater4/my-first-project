"""Script for 'Why You Can't Find The Pirate Token' (Jett) - FLIP formula, roast hook, 5 screams, ~40 s test length.
Hook (JOBLESS BUM) -> flip (trained like a PIGEON) -> name it (variable reward) -> one-liner (PECKING)
-> subscribe flowing straight into the Skinner fact (NOTHING) -> that's you -> crazy part (maybe > winning)
-> the token's value -> why you can't stop -> CTA.
Sources: B.F. Skinner's variable/random reward schedules (pigeons keep pecking thousands of times without food);
Fiorillo, Tobler & Schultz 2003 (Science): sustained dopamine activity peaks when reward probability is 50/50;
Vice (Nov 2026): Fortnite Pirate Token ~1.2M V-Bucks / ~$8,700 of free Item Shop, most players won't find it.
Visuals are our own elves, snow chests and a gold token - no Fortnite characters, map or art."""
LINES = [
    ("Ever wondered why you STILL haven't found the Pirate Token, you JOBLESS BUM?!", "", ('STILL', 'PIRATE', 'TOKEN', 'JOBLESS', 'BUM')),
    ("It's not your skill. Fortnite trained you... like a PIGEON!", "", ('SKILL', 'TRAINED', 'PIGEON')),
    ("It's called a variable reward.", "", ('VARIABLE', 'REWARD')),
    ("You're not playing... you're PECKING!", "", ('PLAYING', 'PECKING')),
    ("If you're still hunting... SUBSCRIBE! 'Cause a scientist fed pigeons at random, and they pecked thousands of times... for NOTHING!", "", ('SUBSCRIBE', 'RANDOM', 'THOUSANDS', 'NOTHING')),
    ("That's you. One more chest. One more drop.", "", ('YOU', 'CHEST', 'DROP')),
    ("And here's the crazy part... your brain gets the biggest rush from maybe. Not from winning.", "", ('CRAZY', 'RUSH', 'MAYBE', 'WINNING')),
    ("That token? Worth about 8,700 dollars in skins. And most of you will never find it.", "", ('TOKEN', '8700', 'NEVER')),
    ("That's exactly why you can't stop.", "", ('STOP',)),
    ("Send this to the friend still grinding for it... or Santa's putting you on the naughty list.", "", ('SEND', 'GRINDING', 'NAUGHTY')),
]
TTS = ""
CAPTION_BREAKS = [
    "Ever wondered why | you STILL haven't found | the Pirate Token, | you JOBLESS BUM?!",
    "It's not your skill. | Fortnite trained you... | like a PIGEON!",
    "It's called | a variable reward.",
    "You're not playing... | you're PECKING!",
    "If you're still hunting... | SUBSCRIBE! | 'Cause a scientist | fed pigeons at random, | and they pecked | thousands of times... | for NOTHING!",
    "That's you. | One more chest. | One more drop.",
    "And here's | the crazy part... | your brain gets | the biggest rush | from maybe. | Not from winning.",
    "That token? | Worth about | 8,700 dollars | in skins. | And most of you | will never find it.",
    "That's exactly | why you can't stop.",
    "Send this to | the friend | still grinding for it... | or Santa's putting you | on the naughty list.",
]
for brk, (txt, _, _) in zip(CAPTION_BREAKS, LINES):
    assert brk.replace('|', ' ').split() == txt.split(), txt
