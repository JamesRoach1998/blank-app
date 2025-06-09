import streamlit as st
import pandas as pd
import numpy as np
import sounddevice as sd
import speech_recognition as sr
import tempfile

# Load your cleaned core mora dataset
@st.cache_data
def load_moras():
    df = pd.read_csv("shakes_core_moras.csv")
    return {
        row["Romaji"]: row["Rhythmic Pattern"]
        for _, row in df.iterrows()
    }

# Map rhythm symbols to vibration duration in ms
rhythm_to_duration = {
    "s": 100,
    "ŝ": 130,
    "m": 150,
    "ḿ": 170,
    "S": 180,
    "Ś": 200
}

def text_to_moras(text):
    text = text.lower().replace(".", "").replace(",", "")
    return [text[i:i+2] for i in range(0, len(text), 2)]

def pattern_to_sequence(pattern):
    parts = pattern.split("-")
    return [(tone, rhythm_to_duration.get(tone, 100)) for tone in parts]

def play_pattern(sequence):
    fs = 44100  # Sample rate
    for tone, duration in sequence:
        if tone in rhythm_to_duration:
            t = duration / 1000
            f = 70  # frequency for buzz simulation
            samples = (np.sin(2 * np.pi * np.arange(fs * t) * f / fs)).astype(np.float32)
            sd.play(samples, samplerate=fs)
            sd.wait()
        else:
            sd.stop()
            sd.sleep(int(duration))

# Speech to text using microphone
@st.cache_resource
def get_recognizer():
    return sr.Recognizer()

def recognize_speech():
    r = get_recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = r.listen(source)
        try:
            return r.recognize_google(audio)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return "[API unavailable]"

# Streamlit UI
st.set_page_config(page_title="Shakes Translator", layout="centered")
st.title("🧠 Shakes Language Translator")

mora_map = load_moras()

# Chat-like container
st.write("### Type or speak below:")

col1, col2 = st.columns([4, 1])
with col1:
    user_input = st.text_input("Your message", placeholder="Type here or use mic...")
with col2:
    if st.button("🎙️"):
        user_input = recognize_speech()
        st.session_state["transcript"] = user_input

if "transcript" in st.session_state and not user_input:
    user_input = st.session_state["transcript"]
    st.text_input("Your message", value=user_input, key="final_input")

if user_input:
    moras = text_to_moras(user_input)
    st.markdown("---")
    st.write("#### Shakes Output")
    for mora in moras:
        pattern = mora_map.get(mora)
        if pattern:
            st.write(f"`{mora}` → {pattern}")
            sequence = pattern_to_sequence(pattern)
            if st.button(f"▶️ Play `{mora}`"):
                play_pattern(sequence)
        else:
            st.warning(f"No pattern found for '{mora}'")
