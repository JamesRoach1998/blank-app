import pandas as pd
import streamlit as st

# Load your Shakes Unified Tactemes CSV
file_path = 'shakes_unified_tactemes_310.csv'
shakes_df = pd.read_csv(file_path)

# Define buzz durations for each rhythm symbol
rhythm_to_buzz = {
    "s": 100,
    "ŝ": 130,
    "S": 180,
    "m": 150,
    "ḿ": 170
}

def pattern_to_durations(pattern):
    tokens = pattern.split('-')
    durations = []
    for token in tokens:
        if token in rhythm_to_buzz:
            durations.append((token, rhythm_to_buzz[token]))
    return durations

def text_to_moras(text):
    text = text.lower().replace(".", "").replace(",", "")
    words = text.split()
    moras = []
    for word in words:
        i = 0
        while i < len(word):
            mora = word[i:i+2]
            moras.append(mora)
            i += 2
    return moras

def moras_to_patterns(moras, df):
    pattern_list = []
    for mora in moras:
        match = df[df['Romaji'] == mora]
        if not match.empty:
            pattern = match.iloc[0]['Rhythmic Pattern']
            durations = pattern_to_durations(pattern)
            pattern_list.append((mora, durations))
        else:
            pattern_list.append((mora, [("pause", 100)]))
    return pattern_list

# Streamlit UI
st.title("Shakes MVP: Text to Vibration Pattern")

text_input = st.text_input("Enter text to translate into Shakes:")

if st.button("Translate"):
    if text_input.strip():
        moras = text_to_moras(text_input)
        st.subheader("Detected Moras")
        st.write(moras)

        shake_patterns = moras_to_patterns(moras, shakes_df)

        st.subheader("Shakes Vibration Patterns")
        for mora, pattern in shake_patterns:
            pattern_str = ", ".join([f"{buzz} ({dur}ms)" for buzz, dur in pattern])
            st.write(f"**{mora}** → {pattern_str}")
    else:
        st.warning("Please enter some text.")
