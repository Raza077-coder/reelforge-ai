import streamlit as st
import json
import os
import time
import random
from datetime import datetime
from pathlib import Path

# ── .env file auto-load (agar file hai toh) ───────────────────────────────────
def load_env_file():
    env_path = Path(".env")
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

load_env_file()

# .env se keys session mein daal do (agar session mein nahi hain)
if "api_key" not in st.session_state:
    gemini = os.environ.get("GEMINI_API_KEY", "")
    groq = os.environ.get("GROQ_API_KEY", "")
    if gemini and gemini != "your_gemini_key_here":
        st.session_state["api_key"] = gemini
        st.session_state["provider"] = "Gemini"
    elif groq and groq != "your_groq_key_here":
        st.session_state["api_key"] = groq
        st.session_state["provider"] = "Groq"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ReelForge AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Constants ─────────────────────────────────────────────────────────────────
HISTORY_FILE = "content_history.json"
MAX_CHARS_REELS = 1000
MAX_CHARS_SHORTS = 1500

HOOK_OF_THE_DAY_POOL = [
    "Nobody talks about this, but it changed everything for me…",
    "I did this every day for 30 days. Here's what happened.",
    "Stop doing it the hard way. There's a shortcut nobody tells you.",
    "This single habit made me 3x more productive — and it takes 5 minutes.",
    "The advice everyone gives you is actually backwards. Here's the truth.",
    "I wasted 2 years before I learned this. Don't make my mistake.",
    "If I had to start over with nothing, I'd do exactly this.",
    "Most people quit at step 3. Here's how to get past it.",
    "This is the thing successful people do that they never admit.",
    "You've been doing it wrong. Here's the right way.",
]

TONES = ["Educational", "Hype", "Storytelling", "Controversial", "Relatable"]
PLATFORMS = ["Instagram Reels", "YouTube Shorts"]
MODES = ["⚡ Quick Generate", "🧱 Structured JSON", "📱 Platform Specific", "🎭 Tone Selection"]

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

.main { background: #0a0a0f; }

.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 50%, #0a0a0f 100%);
}

/* Header */
.forge-header {
    background: linear-gradient(90deg, #ff2d55, #ff6b35, #ffd60a);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem;
    font-weight: 700;
    letter-spacing: -1px;
    margin-bottom: 0;
    line-height: 1;
}

.forge-sub {
    color: #888;
    font-size: 0.9rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 4px;
}

/* Cards */
.output-card {
    background: #13131f;
    border: 1px solid #1e1e30;
    border-radius: 12px;
    padding: 20px 24px;
    margin: 12px 0;
    position: relative;
}

.output-card-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #ff2d55;
    margin-bottom: 10px;
}

.output-card-content {
    color: #e8e8f0;
    font-size: 0.95rem;
    line-height: 1.7;
    white-space: pre-wrap;
}

/* JSON block */
.json-block {
    background: #0d0d18;
    border: 1px solid #252538;
    border-radius: 10px;
    padding: 16px 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #7dd3fc;
    overflow-x: auto;
}

/* Char counter */
.char-counter {
    font-size: 0.75rem;
    color: #666;
    text-align: right;
    margin-top: 6px;
    font-family: 'JetBrains Mono', monospace;
}

.char-over { color: #ff2d55; }
.char-ok { color: #34d399; }

/* Hook badge */
.hook-badge {
    display: inline-block;
    background: linear-gradient(90deg, #ff2d55, #ff6b35);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1px;
    color: white;
    text-transform: uppercase;
    margin-bottom: 8px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d0d18;
    border-right: 1px solid #1a1a2e;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #ff2d55, #ff6b35) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    padding: 0.5rem 1.5rem !important;
    transition: opacity 0.2s !important;
}

.stButton > button:hover { opacity: 0.85 !important; }

/* Secondary buttons */
.stDownloadButton > button {
    background: #1e1e30 !important;
    color: #e8e8f0 !important;
    border: 1px solid #2e2e48 !important;
    border-radius: 8px !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: #13131f;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #1e1e30;
}

.stTabs [data-baseweb="tab"] {
    color: #888 !important;
    font-weight: 500;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #ff2d55, #ff6b35) !important;
    color: white !important;
    border-radius: 8px !important;
}

/* Text inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #13131f !important;
    border: 1px solid #1e1e30 !important;
    color: #e8e8f0 !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #ff2d55 !important;
    box-shadow: 0 0 0 2px rgba(255,45,85,0.15) !important;
}

/* Select boxes */
.stSelectbox > div > div {
    background: #13131f !important;
    border-color: #1e1e30 !important;
    color: #e8e8f0 !important;
}

/* Info boxes */
.stInfo {
    background: #0d1117 !important;
    border-color: #1e40af !important;
    color: #93c5fd !important;
}

/* Divider */
hr { border-color: #1e1e30 !important; }

/* Progress */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #ff2d55, #ff6b35) !important;
}

/* History card */
.history-card {
    background: #13131f;
    border: 1px solid #1e1e30;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 8px 0;
    cursor: pointer;
    transition: border-color 0.2s;
}

.history-card:hover { border-color: #ff2d55; }

.history-topic {
    font-weight: 600;
    color: #e8e8f0;
    font-size: 0.95rem;
}

.history-meta {
    font-size: 0.75rem;
    color: #555;
    margin-top: 4px;
}

.hotd-box {
    background: linear-gradient(135deg, #1a0a10, #1a100a);
    border: 1px solid #3d1a20;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 10px 0;
    color: #ffd60a;
    font-style: italic;
    font-size: 0.95rem;
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)


# ── History helpers ────────────────────────────────────────────────────────────
def load_history():
    if Path(HISTORY_FILE).exists():
        try:
            with open(HISTORY_FILE) as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_to_history(topic: str, mode: str, platform: str, tone: str, output: dict):
    history = load_history()
    entry = {
        "id": int(time.time() * 1000),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "topic": topic,
        "mode": mode,
        "platform": platform,
        "tone": tone,
        "output": output,
    }
    history.insert(0, entry)
    history = history[:50]  # keep last 50
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


# ── LLM Client ────────────────────────────────────────────────────────────────
def call_gemini(api_key: str, prompt: str, retries: int = 2) -> str:
    """Call Google Gemini free API."""
    import urllib.request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.85, "maxOutputTokens": 1500},
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            if "429" in str(e.code) and attempt < retries:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"Gemini API error {e.code}: {body}")
    raise RuntimeError("Max retries exceeded")


def call_groq(api_key: str, prompt: str, retries: int = 2) -> str:
    """Call Groq free API."""
    import http.client
    import ssl

    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.85,
        "max_tokens": 1500,
    })

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "python-httpx/0.24.0",
        "Accept": "application/json",
    }

    for attempt in range(retries + 1):
        try:
            ctx = ssl.create_default_context()
            conn = http.client.HTTPSConnection("api.groq.com", context=ctx, timeout=30)
            conn.request("POST", "/openai/v1/chat/completions", body=payload, headers=headers)
            resp = conn.getresponse()
            raw = resp.read()
            # handle gzip
            import gzip as _gzip
            encoding = resp.getheader("Content-Encoding", "")
            if "gzip" in encoding:
                raw = _gzip.decompress(raw)
            body = raw.decode("utf-8")
            conn.close()

            if resp.status == 200:
                data = json.loads(body)
                return data["choices"][0]["message"]["content"]
            elif resp.status == 429 and attempt < retries:
                time.sleep(2 ** attempt)
                continue
            else:
                raise RuntimeError(f"Groq API error {resp.status}: {body}")
        except RuntimeError:
            raise
        except Exception as e:
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"Groq connection error: {e}")
    raise RuntimeError("Max retries exceeded")


def generate_content(prompt: str) -> str:
    provider = st.session_state.get("provider", "Gemini")
    api_key = st.session_state.get("api_key", "")
    if not api_key:
        raise RuntimeError("No API key set. Enter your key in the sidebar.")
    if provider == "Gemini":
        return call_gemini(api_key, prompt)
    else:
        return call_groq(api_key, prompt)


def validate_key(provider: str, api_key: str) -> bool:
    """Quick validation call."""
    try:
        if provider == "Gemini":
            result = call_gemini(api_key, "Reply with the word OK only.", retries=0)
        else:
            result = call_groq(api_key, "Reply with the word OK only.", retries=0)
        return bool(result and len(result.strip()) > 0)
    except RuntimeError as e:
        err = str(e)
        # 429 = valid key, just rate limited — treat as valid
        if "429" in err:
            return True
        return False
    except Exception:
        return False


# ── Prompt builders ────────────────────────────────────────────────────────────
def build_quick_prompt(topic: str) -> str:
    return f"""You are a viral short-form video scriptwriter. Generate content for the topic: "{topic}"

Return EXACTLY this format (use these exact labels):

HOOK 1:
[Write a single powerful hook sentence — max 15 words, designed for the first 3 seconds]

HOOK 2:
[Write a different hook style — question, shock, or contrarian angle]

SCRIPT:
[Write a complete 30-60 second script. Use natural spoken language. Include pauses as "...". No camera directions.]

CTA:
[One clear, urgent call-to-action sentence]

THUMBNAIL TEXT 1:
[Bold 3-5 word thumbnail text]

THUMBNAIL TEXT 2:
[Different angle, bold 3-5 word thumbnail text]

THUMBNAIL TEXT 3:
[Curiosity-gap or number-based thumbnail text]

Be direct. No preamble. No explanations. Just the content."""


def build_structured_prompt(topic: str) -> str:
    return f"""You are a viral short-form video scriptwriter. Generate content for: "{topic}"

Return ONLY valid JSON with this exact structure. No markdown, no code fences, no explanation:
{{
  "hook": "single powerful opening sentence max 15 words",
  "problem_statement": "1-2 sentences identifying the pain point",
  "solution_bullets": ["bullet 1", "bullet 2", "bullet 3"],
  "cta": "single clear call to action",
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "thumbnail_texts": ["TEXT 1", "TEXT 2", "TEXT 3"]
}}"""


def build_platform_prompt(topic: str, platform: str) -> str:
    if platform == "Instagram Reels":
        spec = "30-45 seconds, punchy and fast-paced, short sentences, high energy, speaks to Gen Z/Millennial audience"
        max_chars = MAX_CHARS_REELS
    else:
        spec = "45-60 seconds, storytelling arc with setup/conflict/resolution, slightly longer sentences, YouTube audience"
        max_chars = MAX_CHARS_SHORTS

    return f"""You are a viral short-form video scriptwriter optimizing for {platform}.

Topic: "{topic}"
Requirements: {spec}
Target script length: under {max_chars} characters

Return EXACTLY this format:

HOOK:
[Opening hook — max 12 words]

SCRIPT:
[Complete script optimized for {platform}. Natural speech only.]

CTA:
[Platform-appropriate call to action]

HASHTAGS:
[5-7 relevant hashtags as comma-separated list]

No preamble. No labels beyond what's shown."""


def build_tone_prompt(topic: str, tone: str) -> str:
    tone_instructions = {
        "Educational": "Teach clearly. Use 'Did you know…' framing. Cite 1 statistic. Break it into 3 easy steps.",
        "Hype": "Maximum energy. Short punchy sentences. All-caps words for emphasis. Exclamation marks. Hype the viewer up.",
        "Storytelling": "Open with a personal story or 'I once…' framing. Build tension. Reveal the lesson at the end.",
        "Controversial": "Lead with a hot take. Say something that challenges common wisdom. Back it up. End with a debate-starting question.",
        "Relatable": "Use 'You know that feeling when…' framing. Make the viewer feel understood. Self-deprecating humor is ok.",
    }

    return f"""You are a viral short-form video scriptwriter. Write in {tone} tone.

Tone instruction: {tone_instructions.get(tone, "")}
Topic: "{topic}"

Return EXACTLY this format:

HOOK:
[Opening hook perfectly matching {tone} tone — max 15 words]

SCRIPT:
[45-75 second script fully committed to {tone} tone throughout]

CTA:
[Call to action that fits {tone} tone]

THUMBNAIL TEXT 1:
[Bold text matching {tone} energy]

THUMBNAIL TEXT 2:
[Alternative thumbnail text]

No preamble. Output only the content."""


# ── Output renderers ───────────────────────────────────────────────────────────
def render_card(label: str, content: str, key_suffix: str = ""):
    char_count = len(content)
    max_chars = MAX_CHARS_REELS
    counter_class = "char-ok" if char_count <= max_chars else "char-over"
    st.markdown(f"""
    <div class="output-card">
        <div class="output-card-label">{label}</div>
        <div class="output-card-content">{content}</div>
    </div>
    """, unsafe_allow_html=True)
    st.code(content, language=None)
    cols = st.columns([3, 1])
    with cols[1]:
        st.markdown(f'<div class="char-counter {counter_class}">{char_count} chars</div>', unsafe_allow_html=True)


def parse_quick_output(raw: str) -> dict:
    """Parse labeled sections from quick generate output."""
    result = {}
    labels = {
        "HOOK 1": "hook1",
        "HOOK 2": "hook2",
        "SCRIPT": "script",
        "CTA": "cta",
        "THUMBNAIL TEXT 1": "thumb1",
        "THUMBNAIL TEXT 2": "thumb2",
        "THUMBNAIL TEXT 3": "thumb3",
    }
    current_key = None
    current_lines = []
    for line in raw.split("\n"):
        stripped = line.strip()
        matched = False
        for label, key in labels.items():
            if stripped.upper().startswith(label + ":") or stripped.upper() == label + ":":
                if current_key:
                    result[current_key] = "\n".join(current_lines).strip()
                current_key = key
                current_lines = []
                remainder = stripped[len(label) + 1:].strip()
                if remainder:
                    current_lines.append(remainder)
                matched = True
                break
        if not matched and current_key is not None:
            current_lines.append(line)
    if current_key:
        result[current_key] = "\n".join(current_lines).strip()
    return result


def parse_generic_output(raw: str) -> dict:
    """Parse generic labeled output (HOOK, SCRIPT, CTA, HASHTAGS, etc.)"""
    result = {}
    labels = ["HOOK", "SCRIPT", "CTA", "HASHTAGS", "THUMBNAIL TEXT 1", "THUMBNAIL TEXT 2"]
    current_key = None
    current_lines = []
    for line in raw.split("\n"):
        stripped = line.strip()
        matched = False
        for label in labels:
            if stripped.upper().startswith(label + ":") or stripped.upper() == label + ":":
                if current_key:
                    result[current_key] = "\n".join(current_lines).strip()
                current_key = label.lower().replace(" ", "_")
                current_lines = []
                remainder = stripped[len(label) + 1:].strip()
                if remainder:
                    current_lines.append(remainder)
                matched = True
                break
        if not matched and current_key is not None:
            current_lines.append(line)
    if current_key:
        result[current_key] = "\n".join(current_lines).strip()
    return result


def render_export_button(content_str: str, filename: str):
    st.download_button(
        label="⬇ Export as .txt",
        data=content_str,
        file_name=filename,
        mime="text/plain",
        key=f"dl_{filename}_{int(time.time())}",
    )


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="forge-header">🎬 ReelForge</div>', unsafe_allow_html=True)
    st.markdown('<div class="forge-sub">AI Content Agent</div>', unsafe_allow_html=True)
    st.markdown("---")

    provider = st.selectbox("LLM Provider", ["Gemini (Free)", "Groq (Free)"])
    st.session_state["provider"] = "Gemini" if "Gemini" in provider else "Groq"

    if st.session_state["provider"] == "Gemini":
        st.caption("Get free key → [aistudio.google.com](https://aistudio.google.com/app/apikey)")
    else:
        st.caption("Get free key → [console.groq.com](https://console.groq.com)")

    api_key = st.text_input(
        "API Key",
        type="password",
        value=st.session_state.get("api_key", ""),
        placeholder="Paste your key here",
    )
    if api_key:
        st.session_state["api_key"] = api_key

    if st.button("✓ Validate Key"):
        if not api_key:
            st.error("Enter an API key first.")
        else:
            with st.spinner("Testing…"):
                ok = validate_key(st.session_state["provider"], api_key)
            if ok:
                st.success("Key is valid ✓")
                st.session_state["key_valid"] = True
            else:
                st.error("Invalid or rate-limited key.")
                st.session_state["key_valid"] = False

    st.markdown("---")

    # Hook of the Day
    st.markdown("**🎲 Hook of the Day**")
    if st.button("Roll a Hook"):
        st.session_state["hotd"] = random.choice(HOOK_OF_THE_DAY_POOL)

    if "hotd" in st.session_state:
        st.markdown(f'<div class="hotd-box">"{st.session_state["hotd"]}"</div>', unsafe_allow_html=True)

    st.markdown("---")

    # History
    st.markdown("**📁 History**")
    history = load_history()
    if not history:
        st.caption("No history yet.")
    else:
        for entry in history[:8]:
            with st.expander(f"🎬 {entry['topic'][:30]}…" if len(entry['topic']) > 30 else f"🎬 {entry['topic']}"):
                st.caption(f"{entry['timestamp']} · {entry['mode']} · {entry['platform']}")
                if st.button("Load", key=f"load_{entry['id']}"):
                    st.session_state["loaded_output"] = entry["output"]
                    st.session_state["loaded_topic"] = entry["topic"]

        if st.button("🗑 Clear History"):
            if Path(HISTORY_FILE).exists():
                os.remove(HISTORY_FILE)
            st.rerun()


# ── Main content ───────────────────────────────────────────────────────────────
st.markdown('<div class="forge-header">ReelForge AI</div>', unsafe_allow_html=True)
st.markdown('<div class="forge-sub">Short-form content generation agent for Reels & Shorts</div>', unsafe_allow_html=True)
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(MODES)

# ─ Tab 1: Quick Generate ──────────────────────────────────────────────────────
with tab1:
    st.markdown("### ⚡ Quick Generate")
    st.caption("Drop a topic. Get hooks, script, CTA, and thumbnail ideas in one shot.")

    col1, col2 = st.columns([4, 1])
    with col1:
        topic_quick = st.text_input(
            "Topic",
            placeholder='e.g. "How to wake up at 5 AM" or "Why your morning routine is wrong"',
            key="topic_quick",
            label_visibility="collapsed",
        )
    with col2:
        generate_quick = st.button("Generate →", key="gen_quick", use_container_width=True)

    if generate_quick:
        if not topic_quick.strip():
            st.error("Enter a topic.")
        elif not st.session_state.get("api_key"):
            st.error("Add your API key in the sidebar.")
        else:
            progress = st.progress(0, text="Building hooks…")
            try:
                progress.progress(20, text="Crafting script…")
                prompt = build_quick_prompt(topic_quick.strip())
                progress.progress(50, text="Generating content…")
                raw = generate_content(prompt)
                progress.progress(85, text="Parsing output…")
                parsed = parse_quick_output(raw)
                progress.progress(100, text="Done!")
                time.sleep(0.3)
                progress.empty()

                st.session_state["quick_output"] = parsed
                st.session_state["quick_topic"] = topic_quick.strip()
                st.session_state["quick_raw"] = raw
                save_to_history(topic_quick.strip(), "Quick", "Both", "—", parsed)

            except Exception as e:
                progress.empty()
                st.error(f"Generation failed: {e}")

    if "quick_output" in st.session_state:
        p = st.session_state["quick_output"]
        topic_label = st.session_state.get("quick_topic", "")

        st.markdown("---")
        st.markdown(f"**Results for:** *{topic_label}*")

        # Hooks
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="hook-badge">Hook Option 1</div>', unsafe_allow_html=True)
            st.code(p.get("hook1", "—"), language=None)
        with c2:
            st.markdown('<div class="hook-badge">Hook Option 2</div>', unsafe_allow_html=True)
            st.code(p.get("hook2", "—"), language=None)

        # Script
        script_text = p.get("script", "")
        st.markdown('<div class="output-card-label" style="color:#ff2d55;font-size:0.75rem;letter-spacing:2px;font-weight:600;text-transform:uppercase;margin-top:16px;">📝 SCRIPT</div>', unsafe_allow_html=True)
        char_count = len(script_text)
        st.text_area("Script", script_text, height=200, key="script_display_quick", label_visibility="collapsed")
        color = "#34d399" if char_count <= MAX_CHARS_REELS else "#ff2d55"
        st.markdown(f'<div class="char-counter" style="color:{color}">{char_count} / {MAX_CHARS_REELS} chars (Reels max)</div>', unsafe_allow_html=True)

        # CTA
        st.markdown('<div class="output-card-label" style="color:#ff6b35;font-size:0.75rem;letter-spacing:2px;font-weight:600;text-transform:uppercase;margin-top:16px;">📣 CALL TO ACTION</div>', unsafe_allow_html=True)
        st.code(p.get("cta", "—"), language=None)

        # Thumbnails
        st.markdown('<div class="output-card-label" style="color:#ffd60a;font-size:0.75rem;letter-spacing:2px;font-weight:600;text-transform:uppercase;margin-top:16px;">🖼 THUMBNAIL TEXT IDEAS</div>', unsafe_allow_html=True)
        tc1, tc2, tc3 = st.columns(3)
        for col, key in zip([tc1, tc2, tc3], ["thumb1", "thumb2", "thumb3"]):
            with col:
                st.code(p.get(key, "—"), language=None)

        # Export
        export_str = f"""TOPIC: {topic_label}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
{'='*50}
HOOK 1: {p.get('hook1','')}
HOOK 2: {p.get('hook2','')}
{'='*50}
SCRIPT:
{p.get('script','')}
{'='*50}
CTA: {p.get('cta','')}
{'='*50}
THUMBNAIL TEXTS:
1. {p.get('thumb1','')}
2. {p.get('thumb2','')}
3. {p.get('thumb3','')}
"""
        render_export_button(export_str, f"reelforge_{topic_label[:20].replace(' ','_')}.txt")


# ─ Tab 2: Structured JSON ─────────────────────────────────────────────────────
with tab2:
    st.markdown("### 🧱 Structured JSON Output")
    st.caption("Get machine-parseable output. Perfect for automation pipelines.")

    topic_json = st.text_input(
        "Topic",
        placeholder='e.g. "Morning routine for entrepreneurs"',
        key="topic_json",
        label_visibility="collapsed",
    )
    gen_json = st.button("Generate JSON →", key="gen_json")

    if gen_json:
        if not topic_json.strip():
            st.error("Enter a topic.")
        elif not st.session_state.get("api_key"):
            st.error("Add your API key in the sidebar.")
        else:
            progress = st.progress(0, text="Building structured output…")
            try:
                progress.progress(30)
                prompt = build_structured_prompt(topic_json.strip())
                progress.progress(60, text="Generating…")
                raw = generate_content(prompt)
                progress.progress(85, text="Parsing JSON…")

                # Strip markdown fences if present
                clean = raw.strip()
                if clean.startswith("```"):
                    lines = clean.split("\n")
                    clean = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

                parsed_json = json.loads(clean)
                progress.progress(100)
                time.sleep(0.3)
                progress.empty()

                st.session_state["json_output"] = parsed_json
                st.session_state["json_topic"] = topic_json.strip()
                save_to_history(topic_json.strip(), "Structured JSON", "Both", "—", parsed_json)

            except json.JSONDecodeError:
                progress.empty()
                st.error("LLM returned invalid JSON. Try again — sometimes the model adds extra text.")
                st.code(raw, language="text")
            except Exception as e:
                progress.empty()
                st.error(f"Generation failed: {e}")

    if "json_output" in st.session_state:
        data = st.session_state["json_output"]
        st.markdown("---")

        col_a, col_b = st.columns([1, 1])
        with col_a:
            st.markdown("**Formatted View**")
            st.markdown(f'<div class="hook-badge">HOOK</div>', unsafe_allow_html=True)
            st.info(data.get("hook", ""))

            st.markdown('<div class="output-card-label" style="color:#ff6b35;font-size:0.75rem;letter-spacing:2px;font-weight:600;text-transform:uppercase;margin-top:12px;">Problem Statement</div>', unsafe_allow_html=True)
            st.write(data.get("problem_statement", ""))

            st.markdown('<div class="output-card-label" style="color:#34d399;font-size:0.75rem;letter-spacing:2px;font-weight:600;text-transform:uppercase;margin-top:12px;">Solution Bullets</div>', unsafe_allow_html=True)
            for b in data.get("solution_bullets", []):
                st.markdown(f"• {b}")

            st.markdown('<div class="output-card-label" style="color:#ffd60a;font-size:0.75rem;letter-spacing:2px;font-weight:600;text-transform:uppercase;margin-top:12px;">CTA</div>', unsafe_allow_html=True)
            st.write(data.get("cta", ""))

            st.markdown('<div class="output-card-label" style="color:#a855f7;font-size:0.75rem;letter-spacing:2px;font-weight:600;text-transform:uppercase;margin-top:12px;">Hashtags</div>', unsafe_allow_html=True)
            st.write(" ".join(data.get("hashtags", [])))

            st.markdown('<div class="output-card-label" style="color:#06b6d4;font-size:0.75rem;letter-spacing:2px;font-weight:600;text-transform:uppercase;margin-top:12px;">Thumbnail Texts</div>', unsafe_allow_html=True)
            for t in data.get("thumbnail_texts", []):
                st.code(t, language=None)

        with col_b:
            st.markdown("**Raw JSON**")
            json_str = json.dumps(data, indent=2)
            st.code(json_str, language="json")
            render_export_button(json_str, f"reelforge_structured_{st.session_state.get('json_topic','')[:15].replace(' ','_')}.json")


# ─ Tab 3: Platform Specific ───────────────────────────────────────────────────
with tab3:
    st.markdown("### 📱 Platform Specific")
    st.caption("Tune the script for Reels vs Shorts pacing, character limits, and audience.")

    col_p1, col_p2 = st.columns([3, 1])
    with col_p1:
        topic_platform = st.text_input(
            "Topic",
            placeholder='e.g. "3 productivity hacks you\'re not using"',
            key="topic_platform",
            label_visibility="collapsed",
        )
    with col_p2:
        platform = st.selectbox("Platform", PLATFORMS, key="platform_select", label_visibility="collapsed")

    max_chars = MAX_CHARS_REELS if platform == "Instagram Reels" else MAX_CHARS_SHORTS

    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.caption(f"📏 Max chars: **{max_chars}**")
    with col_info2:
        st.caption(f"⏱ Target: **{'30-45s' if platform == 'Instagram Reels' else '45-60s'}**")

    gen_platform = st.button("Generate for Platform →", key="gen_platform")

    if gen_platform:
        if not topic_platform.strip():
            st.error("Enter a topic.")
        elif not st.session_state.get("api_key"):
            st.error("Add your API key in the sidebar.")
        else:
            progress = st.progress(0, text=f"Optimizing for {platform}…")
            try:
                progress.progress(30)
                prompt = build_platform_prompt(topic_platform.strip(), platform)
                progress.progress(60, text="Writing script…")
                raw = generate_content(prompt)
                progress.progress(85, text="Parsing…")
                parsed = parse_generic_output(raw)
                progress.progress(100)
                time.sleep(0.3)
                progress.empty()

                st.session_state["platform_output"] = parsed
                st.session_state["platform_topic"] = topic_platform.strip()
                st.session_state["platform_name"] = platform
                save_to_history(topic_platform.strip(), "Platform", platform, "—", parsed)

            except Exception as e:
                progress.empty()
                st.error(f"Generation failed: {e}")

    if "platform_output" in st.session_state:
        p = st.session_state["platform_output"]
        plat = st.session_state.get("platform_name", "")
        topic_lbl = st.session_state.get("platform_topic", "")

        st.markdown("---")
        st.markdown(f"**{plat} script for:** *{topic_lbl}*")

        st.markdown('<div class="hook-badge">HOOK</div>', unsafe_allow_html=True)
        st.code(p.get("hook", "—"), language=None)

        script_text = p.get("script", "")
        char_count = len(script_text)
        color = "#34d399" if char_count <= max_chars else "#ff2d55"
        status = "✓ Within limit" if char_count <= max_chars else "⚠ Over limit"

        st.markdown('<div class="output-card-label" style="color:#ff2d55;font-size:0.75rem;letter-spacing:2px;font-weight:600;text-transform:uppercase;margin-top:16px;">SCRIPT</div>', unsafe_allow_html=True)
        st.text_area("Script", script_text, height=220, key="platform_script_display", label_visibility="collapsed")
        st.markdown(f'<div class="char-counter" style="color:{color}">{char_count} / {max_chars} chars — {status}</div>', unsafe_allow_html=True)

        col_cta, col_tags = st.columns(2)
        with col_cta:
            st.markdown('<div class="output-card-label" style="color:#ff6b35;font-size:0.75rem;letter-spacing:2px;font-weight:600;text-transform:uppercase;margin-top:12px;">CTA</div>', unsafe_allow_html=True)
            st.code(p.get("cta", "—"), language=None)
        with col_tags:
            st.markdown('<div class="output-card-label" style="color:#a855f7;font-size:0.75rem;letter-spacing:2px;font-weight:600;text-transform:uppercase;margin-top:12px;">HASHTAGS</div>', unsafe_allow_html=True)
            st.write(p.get("hashtags", "—"))

        export_str = f"""PLATFORM: {plat}
TOPIC: {topic_lbl}
{'='*50}
HOOK: {p.get('hook','')}
{'='*50}
SCRIPT:
{p.get('script','')}
{'='*50}
CTA: {p.get('cta','')}
HASHTAGS: {p.get('hashtags','')}
"""
        render_export_button(export_str, f"reelforge_{plat.split()[0].lower()}_{topic_lbl[:15].replace(' ','_')}.txt")


# ─ Tab 4: Tone Selection ──────────────────────────────────────────────────────
with tab4:
    st.markdown("### 🎭 Tone Selection")
    st.caption("Same topic. Completely different energy. Pick your voice.")

    topic_tone = st.text_input(
        "Topic",
        placeholder='e.g. "Why you\'re still broke" or "How to study smarter"',
        key="topic_tone",
        label_visibility="collapsed",
    )

    st.markdown("**Choose Tone:**")
    tone_cols = st.columns(5)
    tone_icons = {"Educational": "🎓", "Hype": "🔥", "Storytelling": "📖", "Controversial": "💥", "Relatable": "🙋"}
    tone_selected = st.radio(
        "Tone",
        TONES,
        horizontal=True,
        key="tone_radio",
        label_visibility="collapsed",
    )

    tone_descriptions = {
        "Educational": "Clear steps, data-backed, credibility-first",
        "Hype": "High energy, bold language, motivational",
        "Storytelling": "Personal narrative, tension + resolution",
        "Controversial": "Hot take, challenges conventional wisdom",
        "Relatable": "Self-aware, human, humor-tinged",
    }
    st.caption(f"_{tone_descriptions.get(tone_selected, '')}_")

    gen_tone = st.button("Generate with Tone →", key="gen_tone")

    if gen_tone:
        if not topic_tone.strip():
            st.error("Enter a topic.")
        elif not st.session_state.get("api_key"):
            st.error("Add your API key in the sidebar.")
        else:
            progress = st.progress(0, text=f"Generating {tone_selected} content…")
            try:
                progress.progress(30)
                prompt = build_tone_prompt(topic_tone.strip(), tone_selected)
                progress.progress(60, text="Writing…")
                raw = generate_content(prompt)
                progress.progress(85, text="Parsing…")
                parsed = parse_generic_output(raw)
                progress.progress(100)
                time.sleep(0.3)
                progress.empty()

                st.session_state["tone_output"] = parsed
                st.session_state["tone_topic"] = topic_tone.strip()
                st.session_state["tone_selected"] = tone_selected
                save_to_history(topic_tone.strip(), "Tone", "Both", tone_selected, parsed)

            except Exception as e:
                progress.empty()
                st.error(f"Generation failed: {e}")

    if "tone_output" in st.session_state:
        p = st.session_state["tone_output"]
        tone_lbl = st.session_state.get("tone_selected", "")
        topic_lbl = st.session_state.get("tone_topic", "")

        st.markdown("---")
        st.markdown(f"**{tone_icons.get(tone_lbl,'')} {tone_lbl} script for:** *{topic_lbl}*")

        st.markdown('<div class="hook-badge">HOOK</div>', unsafe_allow_html=True)
        st.code(p.get("hook", "—"), language=None)

        script_text = p.get("script", "")
        char_count = len(script_text)
        color = "#34d399" if char_count <= MAX_CHARS_SHORTS else "#ff2d55"

        st.markdown('<div class="output-card-label" style="color:#ff2d55;font-size:0.75rem;letter-spacing:2px;font-weight:600;text-transform:uppercase;margin-top:16px;">SCRIPT</div>', unsafe_allow_html=True)
        st.text_area("Script", script_text, height=220, key="tone_script_display", label_visibility="collapsed")
        st.markdown(f'<div class="char-counter" style="color:{color}">{char_count} chars</div>', unsafe_allow_html=True)

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown('<div class="output-card-label" style="color:#ff6b35;font-size:0.75rem;letter-spacing:2px;font-weight:600;text-transform:uppercase;margin-top:12px;">CTA</div>', unsafe_allow_html=True)
            st.code(p.get("cta", "—"), language=None)
        with col_t2:
            t1 = p.get("thumbnail_text_1", p.get("thumbnail text 1", ""))
            t2 = p.get("thumbnail_text_2", p.get("thumbnail text 2", ""))
            if t1 or t2:
                st.markdown('<div class="output-card-label" style="color:#ffd60a;font-size:0.75rem;letter-spacing:2px;font-weight:600;text-transform:uppercase;margin-top:12px;">THUMBNAILS</div>', unsafe_allow_html=True)
                if t1:
                    st.code(t1, language=None)
                if t2:
                    st.code(t2, language=None)

        export_str = f"""TONE: {tone_lbl}
TOPIC: {topic_lbl}
{'='*50}
HOOK: {p.get('hook','')}
{'='*50}
SCRIPT:
{p.get('script','')}
{'='*50}
CTA: {p.get('cta','')}
"""
        render_export_button(export_str, f"reelforge_{tone_lbl.lower()}_{topic_lbl[:15].replace(' ','_')}.txt")
