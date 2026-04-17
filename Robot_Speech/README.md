# 🤖 Robotics Voice

A voice-first AI chatbot built for Raspberry Pi. It uses a **wake-word system** so the microphone stays silent until called — just like a smart speaker. Powered by a local **Ollama / LLaMA** model, so it works fully offline.

---

## How It Works

```
[Sleeping]  ──── "Hi / Hello / Hey iBot" ────►  [Awake]
                                                      │
                                         listens for questions
                                                      │
                                  ◄──── "Bye / Thank you" ────  [Sleeping]
```

- **Wake words** → `hi`, `hello`, `hey`, `hey ibot`, `ibot`, `wake up`
- **Sleep words** → `bye`, `goodbye`, `thank you`, `thanks`, `see you`, `that's all`
- Once awake, the microphone stays **continuously open** — no button pressing needed.
- The bot speaks its answers aloud using text-to-speech.

---

## Project Structure

```
inker-robotics-chatbot/
│
├── main.py                  ← Raspberry Pi entry point (wake word + voice loop)
├── requirements.txt
│
├── core/
│   ├── keyword_search.py    ← Searches your dataset for relevant context
│   └── llama_engine.py      ← Sends context + query to the local LLaMA model
│
└── voice/
    ├── speech_to_text.py    ← (legacy helper — logic now in main.py)
    └── text_to_speech.py    ← (legacy helper — logic now in main.py)
```

> `f.py` and `n.py` are the optional **Flask web UI** versions (text + browser-based voice).  
> `i.py` is an older interactive terminal version. You can keep them for reference.

---

## Setup

### 1 — System packages (Raspberry Pi / Debian)

```bash
sudo apt update
sudo apt install -y portaudio19-dev python3-pyaudio espeak
```

### 2 — Python dependencies

```bash
pip install -r requirements.txt
```

### 3 — Install and start Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a lightweight model (good for Pi 4/5)
ollama pull llama3.2:1b

# Ollama starts automatically; verify it's running:
ollama list
```

### 4 — Run the chatbot

```bash
python main.py
```

---

## Usage

| You say | What happens |
|---|---|
| `"Hello"` | Bot wakes up and greets you |
| `"What is Inker Robotics?"` | Bot searches its dataset and answers |
| `"Tell me about the robot arm"` | Bot answers from local knowledge |
| `"Thank you"` / `"Bye"` | Bot goes back to sleep |

---

## Configuration

At the top of `main.py` you can tweak:

| Variable | Default | Description |
|---|---|---|
| `WAKE_WORDS` | `hi, hello, hey, ibot…` | Words that wake the bot |
| `SLEEP_WORDS` | `bye, thank you…` | Words that send it back to sleep |
| `MIC_TIMEOUT` | `5` sec | How long to wait for speech to start |
| `PHRASE_TIME_LIMIT` | `10` sec | Max length of a single phrase |

TTS voice rate and volume are set inside `build_tts_engine()`.

---

## Optional: Flask Web UI

Two web UI versions are included for use on a monitor/kiosk:

```bash
# Minimal wake-word web UI
python n.py

# Full-featured animated web UI
python f.py
```

Then open `http://<pi-ip>:5000` in a browser.

---

## Requirements

- Python 3.10+
- Raspberry Pi 4 or 5 recommended (3B+ works but is slower)
- USB microphone or Pi-compatible audio HAT
- Speaker connected via 3.5 mm jack or HDMI
- Internet connection for first-time Ollama model download only

---

## Troubleshooting

**Mic not detected**
```bash
arecord -l          # list capture devices
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

**No audio output**
```bash
# Force audio to 3.5mm jack
raspi-config  →  System Options → Audio → Headphones
```

**`PyAudio` install fails**
```bash
sudo apt install -y python3-pyaudio
# or
pip install pipwin && pipwin install pyaudio   # Windows only
```

**Ollama not responding**
```bash
systemctl status ollama
ollama serve   # start manually if needed
```

---

## License

MIT — free to use and modify.
