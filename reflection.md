# Reflection: Profile Pair Comparisons

Each section below compares two user profiles and explains what changed between
their outputs and why that makes sense — in plain language, no code required.

---

## Pair 1: High-Energy Pop vs. Chill Lofi

The High-Energy Pop profile asked for pop music, a happy mood, and energy near
the top of the scale (0.85). The Chill Lofi profile asked for the opposite:
lofi music, a chill mood, and very low energy (0.38).

Both profiles got strong, accurate top results. Sunrise City dominated for the
pop listener; Library Rain and Midnight Coding filled the top two spots for the
lofi listener. The rankings flipped almost perfectly — the songs a pop listener
ranked first were near the bottom (or absent) for the lofi listener, and vice
versa.

**Why it makes sense:** Energy is the clearest dividing line between these two
genres in real life. Pop and EDM are made to get you moving; lofi is made to
fade into the background while you study. When the scoring system sees a target
energy of 0.85 vs. 0.38, it correctly steers toward completely different
corners of the catalog. The acoustic preference also helped: the lofi listener
said they like acoustic sounds, which matched the lofi tracks' high acousticness
scores and pushed electronic pop songs down.

---

## Pair 2: High-Energy Pop vs. Deep Intense Rock

Both profiles want high energy. The pop listener targets 0.85 energy and a
happy mood; the rock listener targets 0.90 energy and an intense mood. On paper
these seem similar — yet their top-5 lists are almost completely different.

The pop listener's top 5 included Sunrise City, Gym Hero, Rooftop Lights,
Signal Burst, and Storm Runner. The rock listener's top 5 included Storm Runner,
Gym Hero, Iron Cascade, Night Drive Loop, and Signal Burst.

**Why it makes sense:** Genre and mood are the deciding factor here, not energy.
"Happy" and "intense" point the system toward completely different songs even at
similar energy levels. Storm Runner (rock/intense) appeared for the rock listener
at #1 but only at #5 for the pop listener, where it snuck in purely on energy
proximity with no identity match at all. This pair shows that when two users
want the same physical intensity, what they actually want to feel is what
separates them.

**The Gym Hero problem:** Gym Hero (pop/intense, energy 0.93) shows up at #2
for the rock listener. Why would a pop song aimed at gym workouts rank highly for
someone who asked for deep rock? Because the system only looks at the word
"intense" — and Gym Hero carries that label. The system doesn't know that
"intense pop" and "intense rock" feel nothing alike to a real listener. A
playlist algorithm at Spotify or Apple Music would factor in tempo, distortion
level, and instrumentation. This one only has a text label.

---

## Pair 3: Chill Lofi vs. Conflicting Energy vs. Mood (adversarial)

The Chill Lofi profile is coherent: everything about it points in the same
direction — low energy, acoustic, relaxed. The Conflicting profile is
deliberately broken: it says genre: folk and mood: sad, but also sets energy
at 0.90, which is near the top of the scale. Folk and sad songs are some of
the quietest in the catalog.

The Chill Lofi profile returned a confident, tight top-5 with scores clustered
near 6.0 / 6.5. The Conflicting profile's top score was 4.44 — noticeably
lower — and the remaining four results were a scattered mix of metal, rock, and
indie pop that have nothing to do with folk or sad music.

**Why it makes sense:** The system is doing exactly what the math says: it found
the one folk/sad song (Ember Road) and gave it the identity bonus. But Ember
Road has energy 0.25 — very far from the target of 0.90 — so the energy signal
dragged its score down hard. Then the remaining four slots went to whatever was
closest to energy 0.90, which is metal and EDM. This shows the system can't
detect that a user's preferences contradict each other. It just tries its best
with each signal independently and produces a nonsensical playlist as a result.

---

## Pair 4: Deep Intense Rock vs. Classical but Hyper-Energy (adversarial)

The Rock profile is a well-formed request. The Classical/Hyper-Energy profile
is adversarial: it asks for a genre (classical) and an energy level (0.95) that
are complete opposites in real life. Classical music is quiet and acoustic;
0.95 energy describes stadium EDM.

Under the original weights, Morning Sonata (classical) won for the classical
profile because the genre and mood bonus was large enough to overrule the energy
mismatch. The rock profile, by contrast, returned Storm Runner at the top with
a high, confident score because genre, mood, and energy all pointed the same
direction.

After the weight experiment (energy doubled, genre halved), Morning Sonata
disappeared entirely from the classical profile's top 5 and was replaced by
Gym Hero, Signal Burst, and Storm Runner — essentially the same songs as the
rock profile. The two profiles became almost identical after the weight change,
which is revealing: when energy dominates, the "classical" label stops mattering
and both users get served the same high-energy songs.

**Why it makes sense:** Genre labels in this system are just words with a fixed
point value. When you tune the weights so energy counts for more, the word
"classical" becomes worth very little against the strong pull of a 0.95 energy
target. This is a good reminder that changing one number in a scoring formula
can fundamentally change the character of what the system recommends — not just
the order, but the entire genre composition of the results.

---

## Pair 5: All-Neutral vs. Any Named Profile

The All-Neutral profile has no genre, no mood, and sets energy and valence both
to 0.50. It is the most honest way to ask the system "what do you recommend
with no information about me?"

Compared to any of the named profiles, the All-Neutral results look bland.
The top 5 are all mid-tempo, mid-energy songs — lofi, soul, r&b — with scores
topping out at 3.70 / 6.50. No named profile scored this low; even the
adversarial Classical/Hyper profile hit 4.42 for its top result.

**Why it makes sense:** The system is built around identity signals (genre and
mood matching). Without them, only continuous signals fire, and those just find
the songs closest to the mathematical midpoint of the dataset. The "best"
songs for an All-Neutral user are the songs most average in energy and valence
— not the most popular, not the highest quality, not the most interesting. This
is the core limitation of preference-matching recommenders: if you tell them
nothing, they give you the middle of the catalog, not a discovery.

This also explains why Gym Hero keeps appearing for pop listeners who only asked
for "happy." The system found that Gym Hero is a pop song with high energy and
high valence — close enough to every pop/happy preference to keep scoring well
— even though a real human listener knows a gym-playlist track feels nothing
like a Sunday-morning feel-good pop song.
