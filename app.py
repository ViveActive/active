
import streamlit as st
import pandas as pd
from PIL import Image

st.set_page_config(page_title="FitKompas", layout="wide")

st.markdown("""
<style>
body {
    background-color: #f8f9fa;
    font-family: 'Roboto', sans-serif;
    color: #343a40;
}
.header {
    text-align: center;
    padding: 2rem 0;
}
.header h1 {
    font-size: 3rem;
    color: #2e7d32;
    margin-bottom: 0.5rem;
}
.header p {
    font-size: 1.2rem;
    color: #6c757d;
}
.question-container {
    background-color: #ffffff;
    border-radius: 8px;
    padding: 2rem;
    margin: 2rem auto;
    max-width: 800px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.stButton>button {
    background-color: #2e7d32;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    border-radius: 4px;
}
div[data-baseweb="radio"] > div > label {
    border: 1px solid #2e7d32;
    border-radius: 0;
    padding: 10px 15px;
    margin: 5px;
    min-width: 150px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h1>FitKompas Vragenlijst</h1><p>Ontdek jouw fitheid en motivatie</p></div>', unsafe_allow_html=True)

logo = Image.open("logo.png")
st.image(logo, width=150)

@st.cache_data
def load_data():
    df = pd.read_excel("vragenlijst.xlsx")
    df = df.dropna(subset=["Unnamed: 1"])
    df = df.rename(columns={
        "Unnamed: 1": "vraag",
        "x-as": "x_as",
        "y-as": "y_as",
        "Unnamed: 4": "richting",
        "Unnamed: 6": "thema",
        "# vraag": "# vraag"
    })
    df = df[df['vraag'].notna() & (df['vraag'] != '')]
    df.reset_index(drop=True, inplace=True)
    return df

df = load_data()
total_questions = len(df)

if 'q_index' not in st.session_state:
    st.session_state.q_index = 0
if 'answers' not in st.session_state:
    st.session_state.answers = []

if st.session_state.q_index < total_questions:
    with st.container():
        st.markdown(f"### Vraag {st.session_state.q_index + 1} van {total_questions}")
        question = df.iloc[st.session_state.q_index]
        st.markdown(f"**{int(question['# vraag'])}. {question['vraag']}**")
        st.markdown(f"**Thema:** {question['thema']}")

        options = [
            "Helemaal niet mee eens",
            "Mee oneens",
            "Neutraal",
            "Mee eens",
            "Helemaal mee eens"
        ]

        antwoord = st.radio("Selecteer jouw mening:", options, horizontal=True, key=f"vraag_{st.session_state.q_index}")

        if st.button("Volgende", key=f"volgende_btn_{st.session_state.q_index}"):
            if len(st.session_state.answers) == st.session_state.q_index:
                st.session_state.answers.append(antwoord)
            st.session_state.q_index += 1
else:
    st.success("Je hebt alle vragen beantwoord!")
    st.markdown("### Jouw antwoorden:")
    for i, ans in enumerate(st.session_state.answers):
        st.markdown(f"**Vraag {i+1}:** {ans}")

    if st.button("Opnieuw beginnen", key="opnieuw_btn"):
        st.session_state.q_index = 0
        st.session_state.answers = []
