# Handoff

Read this before editing. Written for whoever or whatever picks this up next.

The speaker is **Bharath Krishnamachari**, Senior Director of Data & AI at
Delivery Hero (foodpanda, foodora, Yemeksepeti), NUS Computer Engineering 2008.
The audience is **~160 students, 8 PhD and 152 MSc, NUS Faculty of Science**,
most of whom went straight from a bachelor's into the master's with no work
experience. Many are foreign nationals who will job-hunt outside Singapore
because of visa constraints. **This is not a recruitment talk.**

---

## Hard constraints — these came from the speaker, repeatedly

1. **Ten slides total, or fewer.** Act I is 7. Acts II–IV plus the close get
   3–4. He does not want to keep flipping slides.
2. **Slides are conversation aids, not documents.** "They are there to listen to
   me." Every slide he can read aloud is a slide that failed.
3. **Not verbose.** Short lines. If a slide needs a paragraph, the paragraph
   belongs in the speaker notes.
4. **Build within a slide, not across slides.** Use `data-step`. He wants
   animation, not more pages.
5. **Never pompous.** He rejected one slide per career move as "feels very
   pompous, no way." No achievement numbers on slides — no revenue, no team
   sizes, no order volumes. He'll speak to them if he wants.
6. **Do not moralise.** Direct quote: "can u not simon sinek this a bit." Don't
   append a lesson to his stories. The stories carry it.
7. **Never imply he didn't earn something.** A slide that framed his asks as
   "asking for something I hadn't earned yet" was cut hard: "wtf? i earned it
   all. I dont want this language." Frame hustle as initiative and asking, never
   as unearned advantage.
8. **Use his own voice.** Source material is his LinkedIn posts and his Digitale
   Welt article — see [docs/content-sources.md](docs/content-sources.md).
   Paraphrasing him from a CV produced a draft he rejected. Get his actual words.
9. **Credit borrowed ideas.** Career map vs ladder is Jason Shah's, from Lenny
   Rachitsky's podcast. He asked for it credited on the slide with a QR.
10. **Copywriting is expected.** He asked for "hooky" names for his three
    anecdotes rather than a restatement of what he'd said. "use your copy chops."

## Timing

45 minutes total: **~25 minutes talking, ~15 minutes Q&A**, a few minutes of
slack. Act I currently accounts for **15.5 of the 25** — the grid header (`O`)
computes this live from the `min` fields, so keep them honest.

Two rebalances already happened because per-slide estimates were quietly summing
to a 54-minute and then a 23-minute Act I. **Sum the `min` values before you
hand anything over.**

Remaining budget: **9.5 minutes for Acts II–IV and the close.**

## Act I as built

| # | slide | beats | min |
| - | ----- | ----- | --- |
| 1 | Hello — name huge, role, delivery hero, NUS alumnus badge | 0 | 1 |
| 2 | Slido — "what do you want out of the next 45 minutes?" open text | 0 | 2 |
| 3 | The trail — 7 career chapters, colour-coded by pivot type | 7 | 4 |
| 4 | Initiative creates options — three anecdotes | 4 | 3 |
| 5 | Career map vs ladder — learning versus position, with a small source QR | 3 | 2.5 |
| 6 | The learning check — three questions, rate-of-learning, the price | 5 | 2 |
| 7 | Why this matters more now — judgment is the scarce constraint | 3 | 1 |

The trail is the spine: slide 4's three anecdotes are each the *mechanism* behind
a specific jump on it (visibility → the 2010 US move; the cold ask → the 2012
pivot; sink or swim → 2018). He flips back to the trail during slide 5 to talk
through how he chose. **Don't break that link.**

### Career facts — verified against his CV and LinkedIn, get these right

- **2008** graduated NUS, B.Eng Computer Engineering, minor Financial Mathematics
- **2008** UBS **Singapore**, Graduate Trainee in technology (Group Finance IT),
  in a learning-focused programme that included a two-month London rotation
- **2010** relocated *with UBS* to **Stamford, CT** — the bank moved him, it was
  not a job change. An earlier draft wrongly said New York in 2008.
- **2012** UBS Investment Bank Technology → **UBS Wealth Management Americas,
  corporate strategy**, New York. *This is the pivot he most wants to speak to.*
  Marked in brick red on the trail for that reason.
- **2014** Groupon / **ideeli.com**, New York — fashion e-commerce
- **2016–18** **Glu Mobile**, San Francisco — Big Data + Product Data Science
  (show the EA mark alongside; EA acquired Glu in 2021, after he left)
- **2018** **Deloitte** — *Southeast Asia focus*, not Singapore only.
- **2021 →** **Delivery Hero** — show Berlin, Singapore, Istanbul

His own framing of the whole arc, from his 2022 post: *"four role profiles, six
industries and three geographies."*

## Design

Tokens were taken from a page of his own that he pointed at as the look he
wanted: `https://bharath-cero.github.io/hex-partnership-portal/`.

Warm paper `#F7F3EB` · card `#FDFAF4` · ink `#1F1915` · muted `#5C534D` ·
hairline `#D6D0C9` · pine `#005C41` · mint `#D3E2DB` · ochre `#C68956` ·
brick `#AC312C`. Radius 6px.

Type: **Fraunces** display, **Inter Tight** body, **JetBrains Mono** labels.

Single light theme on purpose — it also survives a bright lecture hall, which a
dark deck does not. Every colour is painted explicitly so the page never inherits
a viewer's dark mode.

Official NUS, UBS, Groupon, Glu Mobile, Electronic Arts, Deloitte and Delivery
Hero marks are vendored in `assets/logos/`. The build embeds them as data URIs,
so the delivered HTML remains self-contained and works without venue wifi.

## Open items

- [ ] **Slido link.** Slide 2 shows a dashed placeholder box. Add the URL to
      `QR_TARGETS` in `src/build.py` as `QR_SLIDO` and put `<!--QR_SLIDO-->`
      where the placeholder is.
- [ ] **Acts II–IV**, 9.5 minutes, ~4 slides. Agreed shape:
      Delivery Hero + "movement of atoms" on one; the AI enterprise on one;
      "building is cheap" + what's scarce on one; close on one. Content and his
      own phrasing for all of these is in `docs/content-sources.md`.
- [ ] **Phonetic respelling of his name** on slide 1 — deliberately omitted
      rather than guessed. Only add it if he supplies it.
- [ ] He has *not* decided whether to trim Act I to protect the back half.

## Before you hand anything back

Run this in the browser console on `dist/NUS_Act1.html`. It walks every slide and
every beat and reports anything that overflows the 1280×720 stage. It has caught
real bugs; the deck is currently clean.

```js
(function(){
  var s=document.getElementById("slide"), bad=[];
  function press(k){document.dispatchEvent(new KeyboardEvent("keydown",{key:k,bubbles:true}));}
  var n=document.querySelectorAll("#gridwrap .thumb").length;
  for(var i=0;i<n;i++){
    press("Home"); for(var j=0;j<i;j++) press("ArrowDown");
    var dots=document.querySelectorAll("#dots i").length;
    for(var st=0; st<=dots; st++){
      var ov=s.scrollHeight-s.clientHeight, ow=s.scrollWidth-s.clientWidth;
      if(ov>2||ow>2) bad.push("slide"+(i+1)+"/beat"+st+" v+"+ov+" h+"+ow);
      if(st<dots) press("ArrowRight");
    }
  }
  press("Home");
  return bad.length ? bad.join("\n") : "all beats fit";
})()
```

Then check the `min` values sum to something the speaker actually has time for.
