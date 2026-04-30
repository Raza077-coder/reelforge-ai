# 🎬 ReelForge AI — Content Generator for Reels & Shorts

Single-file Streamlit agent that generates viral short-form video scripts using free LLM APIs.

---

## Setup (3 steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py

# 3. Enter your API key in the sidebar and start generating
```

---

## Get a Free API Key

| Provider | Free Tier | Get Key |
|----------|-----------|---------|
| **Google Gemini** (recommended) | 15 req/min, 1M tokens/day | https://aistudio.google.com/app/apikey |
| **Groq** | 14,400 req/day, very fast | https://console.groq.com |

Both are completely free. No credit card required.

---

## Features

### 4 Generation Modes

| Mode | What it does |
|------|-------------|
| ⚡ Quick Generate | 2 hooks + full script + CTA + 3 thumbnail texts |
| 🧱 Structured JSON | Machine-parseable JSON output for automation |
| 📱 Platform Specific | Tuned for Reels (30-45s) or Shorts (45-60s) |
| 🎭 Tone Selection | Educational / Hype / Storytelling / Controversial / Relatable |

### Other Features
- 📁 Saves last 50 generations to `content_history.json`
- ⬇ Export any output as `.txt` or `.json`
- 📏 Character counter with platform limits (Reels: 1000, Shorts: 1500)
- 🎲 "Hook of the Day" random suggestion button
- ✓ API key validator before first use
- 🔄 Auto-retry on rate limits (exponential backoff)

---

## Sample Output — "How to wake up at 5 AM"

### Quick Generate output:

```
HOOK 1:
Nobody actually wakes up at 5 AM happy. Here's what they don't tell you.

HOOK 2:
I set 7 alarms every morning for a year. Then I found the real problem.

SCRIPT:
The reason you can't wake up at 5 AM isn't your alarm. It's your evening.
Most people try to fix the morning — but the problem starts the night before.

Here's what actually works:

First — set a hard stop time. No screens after 9:30 PM. Your brain needs
darkness to build melatonin, and your phone is sabotaging it every single night.

Second — prep your reason to get up before you sleep. Put your gym shoes
by the bed. Fill your water bottle. Make getting up the path of least resistance.

Third — the first 90 seconds matter most. Don't lie there negotiating
with yourself. Feet on the floor before your brain wakes up enough to argue.

Do this for 5 days. The alarm stops feeling like punishment.

CTA:
Follow for more habits that actually stick — and drop your biggest morning
struggle in the comments.

THUMBNAIL TEXT 1:
WHY 5AM IS LYING TO YOU

THUMBNAIL TEXT 2:
WAKE UP EARLIER (IT'S NOT HARD)

THUMBNAIL TEXT 3:
3 TRICKS FOR 5AM WAKE-UPS
```

---

## File Structure

```
reelforge/
├── app.py                  # Full Streamlit application (single file)
├── requirements.txt        # Only dependency: streamlit
├── README.md               # This file
└── content_history.json    # Auto-created on first generation
```

---

## Error Reference

| Error | Fix |
|-------|-----|
| `API error 400` | Bad API key format |
| `API error 401` | Invalid or expired key |
| `API error 429` | Rate limited — app retries automatically; wait 30s |
| `JSON decode error` | Structured mode only — retry once, usually fixes itself |
| `No API key set` | Enter key in sidebar |

---

## Notes

- No external dependencies beyond `streamlit`. All API calls use Python's built-in `urllib`.
- History is local — stored in `content_history.json` in the working directory.
- The JSON structured mode sometimes requires a retry if the LLM adds markdown fences. The app handles stripping them, but rare edge cases may need a second attempt.
