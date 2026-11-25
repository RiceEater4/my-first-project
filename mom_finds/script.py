"""Script for 'What If Your Mom Has a Superpower?' (Jett). Direct, talks to YOU.
Facts: Voyer et al. (2007) meta-analysis / Silverman & Eals (1992): women often show a (small) advantage in remembering
where objects are. Visual-search research (Wolfe; The Conversation 2026; Frontiers for Young Minds 2019): the brain
searches with a 'target template'; items that don't match what you picture get missed even in plain sight, and people
keep re-checking clear spaces instead of cluttered ones. Tip: picture the exact object, scan clutter slowly."""
LINES = [
    ("Ever wondered how your mom...", "Ever wondered how your mom...", ('MOM',)),
    ("ALWAYS finds your stuff?!", "[shouting] ALWAYS finds your stuff?!", ('ALWAYS',)),
    ("Look at you. 10 minutes searching for your phone. She walks in and finds it in 2 seconds.", "Look at you. Ten minutes searching for your phone. [excited] She walks in and finds it in two seconds.", ('10', 'PHONE', '2')),
    ("So do moms actually have a superpower? Scientists tested it... and kind of, yes. Women are often better at remembering where things are.", "So do moms actually have a superpower? Scientists tested it... and kind of, yes. Women are often better at remembering where things are.", ('SUPERPOWER', 'YES', 'REMEMBERING')),
    ("Not by a lot. But enough to beat you every single time.", "[laughs] Not by a lot. But enough to beat you every single time.", ('LOT', 'EVERY')),
    ("If your mom has this superpower... SUBSCRIBE!", "If your mom has this superpower... [shouting] SUBSCRIBE!", ('SUBSCRIBE',)),
    ("But that's only half of it. Your brain searches with a picture of the thing. If it looks different than you imagined, your eyes skip right over it.", "But that's only half of it. Your brain searches with a picture of the thing. If it looks different than you imagined... [excited] your eyes skip right over it.", ('HALF', 'PICTURE', 'SKIP')),
    ("So it can be right in front of you, and you literally don't see it.", "So it can be right in front of you... and you literally don't see it.", ('FRONT', "DON'T")),
    ("And here's the part nobody tells you...", "[intense] And here's the part nobody tells you...", ('NOBODY',)),
    ("You keep checking the same empty spots. Mom checks the messy ones.", "You keep checking the same empty spots. [excited] Mom checks the messy ones.", ('EMPTY', 'MESSY')),
    ("Oh, and she's probably the one who put it there.", "Oh... [laughs] and she's probably the one who put it there.", ('PUT',)),
    ("So next time, picture exactly what you're looking for, and search the messy spots slowly.", "So next time, picture exactly what you're looking for... and search the messy spots slowly.", ('EXACTLY', 'SLOWLY')),
    ("Or just yell MOM. It works every time.", "Or just yell... [shouting] MOM! [laughs] It works every time.", ('MOM', 'EVERY')),
    ("Send this to your mom... or Santa's putting you on the naughty list.", "Send this to your mom... [mischievous] or Santa's putting you on the naughty list.", ('SEND', 'MOM', 'NAUGHTY')),
]
TTS = "\n\n".join(l[1] for l in LINES)
CAPTION_BREAKS = [
    "Ever wondered | how your mom...",
    "ALWAYS finds | your stuff?!",
    "Look at you. | 10 minutes searching | for your phone. | She walks in | and finds it | in 2 seconds.",
    "So do moms | actually have | a superpower? | Scientists tested it... | and kind of, yes. | Women are often better | at remembering | where things are.",
    "Not by a lot. | But enough to beat you | every single time.",
    "If your mom | has this superpower... | SUBSCRIBE!",
    "But that's only | half of it. | Your brain searches | with a picture | of the thing. | If it looks different | than you imagined, | your eyes skip | right over it.",
    "So it can be | right in front of you, | and you literally | don't see it.",
    "And here's the part | nobody tells you...",
    "You keep checking | the same empty spots. | Mom checks | the messy ones.",
    "Oh, | and she's probably | the one who put it there.",
    "So next time, | picture exactly | what you're looking for, | and search | the messy spots slowly.",
    "Or just yell | MOM. | It works every time.",
    "Send this to | your mom... | or Santa's putting you | on the naughty list.",
]
for brk, (txt, _, _) in zip(CAPTION_BREAKS, LINES):
    assert brk.replace('|', ' ').split() == txt.split(), txt
