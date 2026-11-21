"""Script for 'What If Being Late to School Made You a Genius?' (Jett). Younger-sibling v2 order.
Facts: around puberty teens' sleep-wake cycle shifts later (up to ~2 h) with later melatonin release; AAP (2014)
recommends middle/high schools start no earlier than 8:30 AM. Dunster et al. 2018 (Science Advances): Seattle moved
high-school start from 7:50 to 8:45; median school-night sleep +34 min, biology grades ~4.5% higher, less tardiness.
Morning light shifts the body clock earlier (standard circadian science)."""
LINES = [
    ("People who are always late to school...", "People who are always late to school...", ('LATE',)),
    ("are GENIUSES!", "[shouting] are GENIUSESSS!", ('GENIUSES',)),
    ("Look at you. Snooze. Snooze. Snooze. Running in with one shoe on.", "Look at you. Snooze. Snooze. Snooze. [laughs] Running in with one shoe on.", ('SNOOZE', 'SHOE')),
    ("So is being late actually smart? Scientists tested it... and kind of, yes. When you hit puberty, your body clock shifts up to 2 hours later.", "So is being late actually smart? Scientists tested it... and kind of, yes. When you hit puberty, your body clock shifts up to two hours later.", ('SMART', 'YES', '2')),
    ("So 7 AM... can feel like 5 AM.", "So seven AM... [excited] can feel like five AM.", ('7', '5')),
    ("If you've ever been late to first period... SUBSCRIBE! 'Cause the next part is even crazier.", "If you've ever been late to first period... [shouting] SUBSCRIBE! [excited] 'Cause the next part is even crazier.", ('SUBSCRIBE', 'CRAZIER')),
    ("When Seattle pushed school back almost an hour, students got 34 more minutes of sleep... and their grades went up.", "When Seattle pushed school back almost an hour, students got thirty-four more minutes of sleep... [excited] and their grades went up.", ('34', 'GRADES')),
    ("Doctors even say school shouldn't start before 8:30.", "Doctors even say school shouldn't start before eight thirty.", ('DOCTORS', '8:30')),
    ("So you're not lazy. Your body is literally on a different clock.", "So you're not lazy. [intense] Your body is literally on a different clock.", ('LAZY', 'CLOCK')),
    ("But here's the part nobody tells you...", "[intense] But here's the part nobody tells you...", ('NOBODY',)),
    ("Your teacher doesn't care about your body clock.", "[laughs] Your teacher doesn't care about your body clock.", ('TEACHER',)),
    ("So put the phone down an hour before bed... and get sunlight the second you wake up. It pulls your clock earlier.", "So put the phone down an hour before bed... and get sunlight the second you wake up. [excited] It pulls your clock earlier.", ('PHONE', 'SUNLIGHT', 'EARLIER')),
    ("Send this to the friend who's always late... or Santa's putting you on the naughty list.", "Send this to the friend who's always late... [mischievous] or Santa's putting you on the naughty list.", ('SEND', 'LATE', 'NAUGHTY')),
]
TTS = "\n\n".join(l[1] for l in LINES)
CAPTION_BREAKS = [
    "People who are | always late to school...",
    "are GENIUSES!",
    "Look at you. | Snooze. | Snooze. | Snooze. | Running in | with one shoe on.",
    "So is being late | actually smart? | Scientists tested it... | and kind of, yes. | When you hit puberty, | your body clock shifts | up to 2 hours later.",
    "So 7 AM... | can feel like 5 AM.",
    "If you've ever been | late to first period... | SUBSCRIBE! | 'Cause the next part | is even crazier.",
    "When Seattle | pushed school back | almost an hour, | students got 34 more | minutes of sleep... | and their grades went up.",
    "Doctors even say | school shouldn't start | before 8:30.",
    "So you're not lazy. | Your body is literally | on a different clock.",
    "But here's the part | nobody tells you...",
    "Your teacher | doesn't care | about your body clock.",
    "So put the phone down | an hour before bed... | and get sunlight | the second you wake up. | It pulls your clock earlier.",
    "Send this to the friend | who's always late... | or Santa's putting you | on the naughty list.",
]
for brk, (txt, _, _) in zip(CAPTION_BREAKS, LINES):
    assert brk.replace('|', ' ').split() == txt.split(), txt
