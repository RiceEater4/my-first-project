"""Script for 'Why Is It So Hard To Lose Weight?' (Jett) - FLIP formula, roast hook with a bleep.
Hook (bleeped) -> flip (not lazy, body fights you) -> name it (metabolic adaptation) -> how (leptin) -> one-liner
-> short subscribe -> the study (6 years, ~500 cal/day) -> what it means -> twist (can't outrun it) -> fix -> CTA.
Sources: Fothergill et al. 2016 (Obesity, NIH): 14 Biggest Loser contestants, 6 years later resting metabolism
~500 kcal/day below expected. Leptin falls with fat loss -> more hunger, less energy use. Pontzer et al. 2012:
Hadza hunter-gatherers' daily energy expenditure similar to Westerners'.
The swear is a BEEP in the pause after "so..." (never said). Narration sped up 1.1-1.15x before word timing."""
LINES = [
    ("Ever wondered why you're so... #$%@ing FAAAAT?!", "", ('FAAAAT',)),
    ("It's not because you're lazy. Your body is literally FIGHTING you. It's called... metabolic adaptation.", "", ('LAZY', 'FIGHTING', 'METABOLIC', 'ADAPTATION')),
    ("When you lose weight, your fat makes less of a hormone called leptin. Your brain sees that... and panics. Hunger goes UP. Energy goes DOWN.", "", ('LEPTIN', 'PANICS', 'UP', 'DOWN')),
    ("You're not weak. Your body thinks you're starving.", "", ('WEAK', 'STARVING')),
    ("Tried every diet? SUBSCRIBE! The study's insane.", "", ('DIET', 'SUBSCRIBE', 'INSANE')),
    ("Scientists tracked contestants from a weight-loss TV show for six years. They'd lost a TON of weight. But six years later... their bodies were burning about 500 fewer calories a day than they should.", "", ('TV', 'TON', '500', 'FEWER')),
    ("That's a whole meal your body refuses to burn... every single day.", "", ('MEAL', 'EVERY')),
    ("But here's the part nobody tells you... you can't outrun it. Hunter-gatherers who walk miles every day burn about the same calories as people sitting at a desk.", "", ('NOBODY', 'OUTRUN', 'SAME', 'DESK')),
    ("So forget crazy diets. Small changes you can keep forever... win every time.", "", ('CRAZY', 'SMALL', 'FOREVER', 'WIN')),
    ("Send this to your friend who's always on a diet... or Santa's putting you on the naughty list.", "", ('SEND', 'DIET', 'NAUGHTY')),
]
TTS = ""
CAPTION_BREAKS = [
    "Ever wondered why | you're so... | #$%@ing FAAAAT?!",
    "It's not because | you're lazy. | Your body is literally | FIGHTING you. | It's called... | metabolic adaptation.",
    "When you lose weight, | your fat makes less | of a hormone | called leptin. | Your brain sees that... | and panics. | Hunger goes UP. | Energy goes DOWN.",
    "You're not weak. | Your body thinks | you're starving.",
    "Tried every diet? | SUBSCRIBE! | The study's insane.",
    "Scientists tracked contestants | from a weight-loss TV show | for six years. | They'd lost | a TON of weight. | But six years later... | their bodies were burning | about 500 fewer calories | a day | than they should.",
    "That's a whole meal | your body refuses to burn... | every single day.",
    "But here's the part | nobody tells you... | you can't outrun it. | Hunter-gatherers | who walk miles every day | burn about | the same calories | as people | sitting at a desk.",
    "So forget crazy diets. | Small changes | you can keep forever... | win every time.",
    "Send this to | your friend | who's always on a diet... | or Santa's putting you | on the naughty list.",
]
for brk, (txt, _, _) in zip(CAPTION_BREAKS, LINES):
    assert brk.replace('|', ' ').split() == txt.split(), txt
