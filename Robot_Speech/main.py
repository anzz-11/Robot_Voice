"""
Inker Robotics Chatbot — Raspberry Pi Entry Point
===================================================
Wake words  : hi, hello, hey, hey ibot, ibot
Sleep words : bye, goodbye, thank you, thanks
The mic stays open after wake until a sleep word is spoken.
"""

import time
import speech_recognition as sr
import pyttsx3
from core.keyword_search import search_dataset
from core.llama_engine import ask_llama

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────

WAKE_WORDS  = {"hi", "hello", "hey", "hey ibot", "ibot", "wake up"}
SLEEP_WORDS = {"bye", "goodbye", "thank you", "thanks", "see you", "that's all"}

MIC_TIMEOUT        = 5   # seconds to wait for speech to start
PHRASE_TIME_LIMIT  = 10  # max seconds per phrase


# ─────────────────────────────────────────
# TEXT-TO-SPEECH SETUP
# ─────────────────────────────────────────

def build_tts_engine() -> pyttsx3.Engine:
    """Configure pyttsx3 for a clear, natural robot voice."""
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")

    # Prefer a female voice; fall back to whatever is available
    preferred = next(
        (v for v in voices if "female" in v.name.lower()
         or "zira" in v.name.lower()
         or "hazel" in v.name.lower()),
        voices[0] if voices else None,
    )
    if preferred:
        engine.setProperty("voice", preferred.id)

    engine.setProperty("rate", 160)    # words per minute (slower = clearer on Pi)
    engine.setProperty("volume", 1.0)  # 0.0 – 1.0
    return engine


tts = build_tts_engine()


def speak(text: str) -> None:
    """Speak text aloud and print it to the terminal."""
    print(f"🤖 Bot: {text}")
    tts.say(text)
    tts.runAndWait()


# ─────────────────────────────────────────
# SPEECH-TO-TEXT
# ─────────────────────────────────────────

recognizer = sr.Recognizer()
recognizer.pause_threshold = 1.0   # seconds of silence before phrase ends
recognizer.energy_threshold = 300  # adjust for ambient noise on Pi


def listen(prompt_label: str = "Listening") -> str | None:
    """
    Capture one phrase from the microphone and return the transcript.
    Returns None on any recognition failure.
    """
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print(f"🎤 [{prompt_label}] ...")
        try:
            audio = recognizer.listen(
                source,
                timeout=MIC_TIMEOUT,
                phrase_time_limit=PHRASE_TIME_LIMIT,
            )
        except sr.WaitTimeoutError:
            return None

    try:
        text = recognizer.recognize_google(audio).lower().strip()
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"⚠️  Speech API error: {e}")
        return None


def is_wake_word(text: str) -> bool:
    return any(w in text for w in WAKE_WORDS)


def is_sleep_word(text: str) -> bool:
    return any(w in text for w in SLEEP_WORDS)


# ─────────────────────────────────────────
# CORE CHAT
# ─────────────────────────────────────────

def handle_query(query: str) -> str:
    """Search the dataset and ask Llama for an answer."""
    context = search_dataset(query)
    answer  = ask_llama(context, query)
    return answer


# ─────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────

def run() -> None:
    print("\n" + "=" * 50)
    print("  🤖  Inker Robotics Chatbot  —  Pi Mode")
    print("=" * 50)
    print(f"  Wake  words : {', '.join(sorted(WAKE_WORDS))}")
    print(f"  Sleep words : {', '.join(sorted(SLEEP_WORDS))}")
    print("=" * 50 + "\n")

    speak("Inker Robotics Chatbot is ready. Say hi or hello to wake me up.")

    while True:
        # ── SLEEPING: wait for wake word ──────────────
        print("💤 Sleeping — waiting for wake word...")
        raw = listen(prompt_label="Wake word")

        if not raw:
            continue  # silence or noise — keep waiting

        if not is_wake_word(raw):
            continue  # heard something, but not a wake word

        # ── AWAKE: greet and start conversation ───────
        print(f"\n✅ Wake word detected: '{raw}'")
        speak("Hey! I'm awake. How can I help you?")

        while True:
            query = listen(prompt_label="Your question")

            if query is None:
                speak("I didn't catch that. Could you say it again?")
                continue

            print(f"🗣  You said: {query}")

            # Check for sleep / farewell
            if is_sleep_word(query):
                speak("You're welcome! Going back to sleep. Say hi when you need me.")
                print()
                break  # back to outer sleep loop

            # Skip near-empty input
            if len(query.split()) < 2:
                speak("Could you please give me a bit more detail?")
                continue

            # Answer the question
            try:
                answer = handle_query(query)
                speak(answer)
            except Exception as e:
                print(f"⚠️  Error: {e}")
                speak("Sorry, I ran into a problem. Please try again.")


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
