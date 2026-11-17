"""Script for 'What If Bad Gift Wrapping Made You a Genius?' v2 - straight-to-camera explainer (narrated by Jett).
Format: hook -> relatable logic aimed at YOU -> the study -> why -> feel-good reframe -> catch -> send-off -> CTA.
Study: Rixom, Mas & Rixom (2020), Journal of Consumer Psychology 30(2): same gift wrapped neat vs sloppy; from a
friend the sloppy one was liked more (neat wrapping raised expectations the gift then missed); from an acquaintance
the neat one was liked more."""
LINES = [
    ("People who wrap presents badly...", "People who wrap presents badly...", ('BADLY',)),
    ("are GENIUSES!", "[shouting] are GENIUSESSS!", ('GENIUSES',)),
    ("Think about it. You spend 20 minutes folding perfect little corners... and they rip it open in 2 seconds.", "Think about it. You spend twenty minutes folding perfect little corners... and they rip it open in two seconds.", ('20', 'MINUTES', '2', 'SECONDS')),
    ("20 minutes. Gone. Straight in the trash.", "Twenty minutes. Gone. Straight in the trash.", ('GONE', 'TRASH')),
    ("A messy wrap? 30 seconds. Same gift. Same smile.", "A messy wrap? Thirty seconds. Same gift. Same smile.", ('30', 'SMILE')),
    ("And scientists actually proved it. They gave people the same gift, wrapped neat or wrapped sloppy...", "And scientists actually proved it. They gave people the same gift, wrapped neat or wrapped sloppy...", ('PROVED', 'NEAT', 'SLOPPY')),
    ("and people liked the sloppy one more.", "[excited] and people liked the sloppy one MORE.", ('SLOPPY', 'MORE')),
    ("Because a perfect wrap screams, something amazing is in here. So when it's just socks... you're disappointed.", "Because a perfect wrap screams, something AMAZING is in here. So when it's just socks... you're disappointed.", ('AMAZING', 'SOCKS', 'DISAPPOINTED')),
    ("A messy wrap? Expectations hit the floor... so the gift feels way better than it is.", "A messy wrap? Expectations hit the floor... [excited] so the gift feels way better than it is.", ('FLOOR', 'BETTER')),
    ("You're not lazy. You're managing expectations. That's basically a business skill.", "You're not lazy. You're managing expectations. [excited] That's basically a business skill.", ('LAZY', 'BUSINESS')),
    ("But here's the catch nobody tells you...", "[intense] But here's the catch nobody tells you...", ('CATCH', 'NOBODY')),
    ("It only works with friends and family. For your boss, wrap it perfect, because to them, a neat wrap means you care.", "It only works with friends and family. For your boss, wrap it perfect, because to them, a neat wrap means you care.", ('FRIENDS', 'FAMILY', 'BOSS', 'CARE')),
    ("So this year... grab the tape, skip the corners, and let the genius in you shine.", "So this year... grab the tape, skip the corners, [excited] and let the genius in you shine.", ('TAPE', 'GENIUS')),
    ("Tag the worst wrapper you know... and subscribe, or Santa's putting you on the naughty list.", "Tag the worst wrapper you know... [mischievous] and subscribe, or Santa's putting you on the naughty list.", ('TAG', 'SUBSCRIBE', 'NAUGHTY')),
]
TTS = "\n\n".join(l[1] for l in LINES)
CAPTION_BREAKS = [
    "People who | wrap presents badly...",
    "are GENIUSES!",
    "Think about it. | You spend 20 minutes | folding perfect | little corners... | and they rip it open | in 2 seconds.",
    "20 minutes. | Gone. | Straight in the trash.",
    "A messy wrap? | 30 seconds. | Same gift. | Same smile.",
    "And scientists | actually proved it. | They gave people | the same gift, | wrapped neat | or wrapped sloppy...",
    "and people liked | the sloppy one more.",
    "Because a perfect wrap | screams, | something amazing | is in here. | So when it's | just socks... | you're disappointed.",
    "A messy wrap? | Expectations | hit the floor... | so the gift feels | way better | than it is.",
    "You're not lazy. | You're managing | expectations. | That's basically | a business skill.",
    "But here's the catch | nobody tells you...",
    "It only works | with friends | and family. | For your boss, | wrap it perfect, | because to them, | a neat wrap | means you care.",
    "So this year... | grab the tape, | skip the corners, | and let the genius | in you shine.",
    "Tag the worst wrapper | you know... | and subscribe, | or Santa's putting you | on the naughty list.",
]
for brk, (txt, _, _) in zip(CAPTION_BREAKS, LINES):
    assert brk.replace('|', ' ').split() == txt.split(), txt
