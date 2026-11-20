# Video rules (notes from feedback)

## Hook (first 5-7 seconds)
- No rewind / "let me explain" cold open.
- Open with a bold, direct statement or command, the way the reference shorts do
  ("Your house needs crocodiles.", "Stack three bones.", "One tree. 813 soldiers.").
- Work the "what if" into the hook itself.
- The first 5-7 seconds are straight and direct: say the thing and show it happening. No setup.

## Story / script
- FORMAT (what works): straight-to-camera explainer, not a story. Hook, then talk directly to the viewer ("you")
  with punchy relatable logic ("you spend 20 minutes on corners... they rip it in 2 seconds"), then the facts/study,
  then a feel-good reframe ("you're not lazy, you're managing expectations"), a catch, a send-off and the CTA.
  One character stands in for the viewer and acts out each line. Viral hook words: GENIUS, FURIOUS, etc.
- DIRECT after the hook: blunt commands and facts aimed at the viewer ("Look around the room." "Walk up to the
  thermostat." "Turn the heat up." "Crank it."), like the 'dig a moat around your house' shorts. No "Picture this" setups.
- NOT a story: no named characters, no plot ("Meet Tinsel... then there's Holly"). Always talk to "you".
  One quick relatable scenario is fine ("Picture this. Christmas morning. Your aunt hands you a gift..."), set up
  right after the hook so the viewer knows what's going on before any new person or object appears.
- Every line has to make sense on its own and follow from the line before. If a fact matters,
  say WHY it matters (e.g. "teenage boys keep their antlers" -> say what that changes).
- No dangling endings. The last 10 seconds must pay off the hook and land a clear point,
  not just repeat a line ("Rudolph? Definitely a girl." -> "...and? so what?").
- Length: about 1 minute. Minimum 58 seconds, and it should run over 58 seconds,
  so there is room to explain everything properly.

## Mid-video subscribe (every video)
- Viewers drop around 40 s, so the subscribe ask goes in the MIDDLE, around 20-25 s, right after the first big payoff.
- It is SCREAMED like the hook: a short identity line, then [shouting] "SUBSCRIBE!" with the same screen shake,
  boom and a big SUBSCRIBE button pop + click on screen. e.g. "If you wrap like a raccoon too... [shouting] SUBSCRIBE!"
- Keep it quick (~2-3 s), then straight back into the explanation.

## Ending + CTA (every video)
- Order: story payoff line first, then the CTA as the very last line (~3 s). No "Merry Christmas" sign-off.
- CTA = a specific comment question about the video's topic + the naughty-list subscribe joke, e.g.
  "Comment which superpower you'd want... and subscribe, or Santa's putting you on the naughty list."
  Swap the question per topic ("Comment if you'd let a penguin near Santa...", "Comment boy or girl Rudolph...").
  The naughty-list subscribe line stays the same every time (signature ending).
- Voice: comment part said normally, naughty-list part [mischievous] / smirking.
- Visuals: the main character turns to camera; a pixel comment bubble pops up showing the answer options;
  a red pixel SUBSCRIBE button gets pressed (click + sparkle); Santa slides in beside (never overlapping)
  holding a NAUGHTY LIST scroll. Captions as usual, COMMENT and SUBSCRIBE in yellow.

## Script order that works (younger-sibling v2 format)
1. Hook (screamed word).  2. The relatable thing first: a quick, funny example of it happening ("Eating cereal with a fork.
Asking if fish get thirsty.").  3. Re-ask the hook as a plain question ("So are younger siblings actually dumber?").
4. "Scientists tested it... and yes / kind of." + the fact with a number.  5. A punchy reaction ("Two. That's it.
Barely anything.").  6. Screamed SUBSCRIBE.  7. Why / theory, re-hook, twist, payoff, CTA.

## Script clarity check (before recording)
- Read every line right after the one before it. Pronouns must point at the right thing: after a joke line about
  something else (e.g. "asking if fish get thirsty"), name the subject again ("So are younger siblings actually
  dumber? Scientists tested it...") instead of "they actually are".

## Narration (ElevenLabs, voice: Jett - Gritty, Spunky Young Hero, 6IwYbsNENZgAB1dtBZDp)
- Use Jett from now on (was Ethan, uB5dGadiIOtRLnqbQl9M).
- Use eleven_v4 acting tags: calmer setup lines, then [shouting] / [excited] / [intense] on the hook
  words with stretched spelling, e.g. "Santa's reindeer... are all girls. [shouting] WHAAAAT?!"
- Hook style: blunt fact -> big shouted reaction -> the proof.
- Captions use the narration's exact words, timed word by word to the voice.
- Music sits well under the voice (calm, quiet bed); voice clear but not too loud.

## Characters
- Continuity: characters never vanish and reappear. If something happens to them (explosion, crash), show where
  they go (e.g. blasted out of the fireball, arcing down, crash-landing) before the next shot uses them.
- Characters never block each other: give every character its own space (no overlapping sprites).
- Every character has all its body parts, kept SIMPLE: Santa gets plain arms + mittens, animals get
  clear legs and ears. Simple shapes, not detailed anatomy.
- Draw characters in layers (body, head, arms...) each with its own outline, flat colours, no dither
  noise on faces. Reference: style_study/santa_redone_closeup.png
- Clean, readable faces and details: eyes, nose, mouth, beak are clear shapes (with a highlight),
  not single dots. Check every character up close at full size before rendering.

## Layout
- Shading on bubbles/props is a smooth blend, not hard bands. Text on objects (signs, lists) must be fully readable:
  big enough, inside its plate, never clipped (style_study/scenery.py: school(), naughty_list()). Places get real detail.
- Details + alignment check before rendering: props need real detail (e.g. phone = case, screen gradient, app icons,
  notch, shine); held items anchor to the elf's hand (mom_finds/props.py hand()), floor items get a shadow, groups
  inside bubbles/cards are centred using real text widths, grids use columns centred on the screen.
- Pointer labels and thought bubbles: always use style_study/ui.py (callout = tag box with shadow + chunky outlined
  elbow line + glowing target dot; thought_bubble = puffy cloud with outline, drop shadow, 3-shade shading, trail).
- No platform/island by default: characters and objects stand on an invisible floor with a soft pixel shadow under
  each one (like other pixel-art YouTubers). Use a platform only when the scene needs one. Use the whole width for movement.
- The visual sits in the middle of the screen or a bit higher.
- The caption sits right below the visual (see style_study/layout_reference.png).
- Captions: one line, bold, no box, yellow key word.

## Style
- Blueprint pixel art: navy grid background, small chunky sprites with navy outlines and dithering,
  floating dioramas, pixel labels / tags / counters.
- Christmas theme and public-domain Christmas music in every video. No voice (so far).
- Every video ships with a title and description in copyable blocks.

## What has not worked
- Slow explainer ideas ("What if it never stopped snowing?": ~200 views, ~30% stayed).
- Tiny subjects, long intros, the rewind hook.

## Channel plan (from vidIQ check, Nov 19)
- Best performers so far: the "What If Earth Was ___?" series (flat Earth: 78% avg watched, 10 subs; two moons 79%; donut 73%).
- Now: keep making the GENIUS / FURIOUS relatable shorts (engagement climbing, ~70% on the latest).
- Next week or so: bring back the Earth/space "what if" series with the new hooks, direct script style and Christmas look
  (e.g. "What If Earth Was a Snow Globe?"), then compare the numbers at the next check-in.
- vidIQ check every 1st and 15th (reminder set); renewable credits only, never the add-on ones.
