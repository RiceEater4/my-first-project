"""Script for 'What If Your Younger Sibling Really Is Dumber?' (Jett). Direct, talks to YOU (the older sibling).
Facts: Kristensen & Bjerkedal (2007, Science): 241,310 Norwegian men, eldest ~2.3 IQ points higher on average.
Rohrer, Egloff & Schmukle (2015, PNAS): small decline in measured intelligence with birth order; lead author: in about
4 of 10 cases the later-born is still smarter. Tutoring younger siblings is one proposed explanation (not proven).
Hotz & Pantano (2015, J. Population Economics): parents say they'd be less likely to punish later-born children."""
LINES = [
    ("Ever wondered why your younger sibling is so...", "Ever wondered why your younger sibling is so...", ('YOUNGER', 'SIBLING')),
    ("DUMB?!", "[shouting] DUMBBB?!", ('DUMB',)),
    ("Look at them. Eating cereal with a fork. Asking if fish get thirsty.", "Look at them. Eating cereal... with a fork. [laughs] Asking if fish get thirsty.", ('FORK', 'FISH')),
    ("So are younger siblings actually dumber? Scientists tested it... and yes. Older siblings score about 2 IQ points higher.", "So are younger siblings actually dumber? Scientists tested it... and yes. [excited] Older siblings score about two IQ points higher.", ('DUMBER', 'YES', '2')),
    ("2. That's it. Barely anything.", "Two. That's it. [laughs] Barely anything.", ('2', 'BARELY')),
    ("If you're the smart one... SUBSCRIBE!", "If you're the smart one... [shouting] SUBSCRIBE!", ('SUBSCRIBE',)),
    ("A study of over 240,000 brothers found the oldest scored just a little higher.", "A study of over two hundred forty thousand brothers found the oldest scored just a little higher.", ('240,000', 'OLDEST')),
    ("And one theory? You spent years explaining everything to them... and teaching makes your own brain stronger.", "And one theory? You spent years explaining everything to them... [excited] and teaching makes your own brain stronger.", ('EXPLAINING', 'TEACHING', 'STRONGER')),
    ("So they didn't make you dumb. They made you smarter.", "So they didn't make you dumb. [excited] They made you smarter.", ('SMARTER',)),
    ("But here's the part nobody tells you...", "[intense] But here's the part nobody tells you...", ('NOBODY',)),
    ("Parents get way less strict with each kid. You got grounded for a B. They get a cookie for a C.", "Parents get way less strict with each kid. You got grounded for a B. [laughs] They get a cookie for a C.", ('STRICT', 'GROUNDED', 'COOKIE')),
    ("And in about 4 out of 10 families, the younger one is actually smarter.", "And in about four out of ten families... [intense] the younger one is actually smarter.", ('4', '10', 'SMARTER')),
    ("So be nice. One day, they might be the genius.", "So be nice. [mischievous] One day, they might be the genius.", ('NICE', 'GENIUS')),
    ("Send this to your younger sibling... or Santa's putting you on the naughty list.", "Send this to your younger sibling... [mischievous] or Santa's putting you on the naughty list.", ('SEND', 'SIBLING', 'NAUGHTY')),
]
TTS = "\n\n".join(l[1] for l in LINES)
CAPTION_BREAKS = [
    "Ever wondered why | your younger sibling | is so...",
    "DUMB?!",
    "Look at them. | Eating cereal | with a fork. | Asking if fish | get thirsty.",
    "So are younger siblings | actually dumber? | Scientists tested it... | and yes. | Older siblings score | about 2 IQ points higher.",
    "2. | That's it. | Barely anything.",
    "If you're | the smart one... | SUBSCRIBE!",
    "A study of over | 240,000 brothers | found the oldest | scored just | a little higher.",
    "And one theory? | You spent years | explaining everything | to them... | and teaching makes | your own brain stronger.",
    "So they didn't | make you dumb. | They made you smarter.",
    "But here's the part | nobody tells you...",
    "Parents get way less strict | with each kid. | You got grounded | for a B. | They get a cookie | for a C.",
    "And in about | 4 out of 10 families, | the younger one | is actually smarter.",
    "So be nice. | One day, | they might be the genius.",
    "Send this to | your younger sibling... | or Santa's putting you | on the naughty list.",
]
for brk, (txt, _, _) in zip(CAPTION_BREAKS, LINES):
    assert brk.replace('|', ' ').split() == txt.split(), txt
