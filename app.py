
import streamlit as st
import pandas as pd
from PIL import Image
import plotly.graph_objects as go

st.set_page_config(page_title="FitKompas", layout="wide")

# ---- INLOG ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 FitKompas Toegang")
    wachtwoord = st.text_input("Voer toegangscode in:", type="password")
    if wachtwoord == "viveactive":
        st.session_state.logged_in = True
        st.experimental_rerun()
    else:
        st.stop()

# ---- STYLING ----
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
.stButton>button {
    background-color: #2e7d32;
    color: white;
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

# ---- HEADER ----
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

# ---- VRAGEN TONEN ----
if st.session_state.q_index < total_questions:
    with st.container():
        st.markdown(f"### Vraag {st.session_state.q_index + 1} van {total_questions}")
        vraag = df.iloc[st.session_state.q_index]
        st.markdown(f"**{int(vraag['# vraag'])}. {vraag['vraag']}**")
        st.markdown(f"**Thema:** {vraag['thema']}")

        opties = [
            "Helemaal niet mee eens",
            "Mee oneens",
            "Neutraal",
            "Mee eens",
            "Helemaal mee eens"
        ]

        antwoord = st.radio("Selecteer jouw mening:", opties, horizontal=True, key=f"vraag_{st.session_state.q_index}")

        if st.button("Volgende", key=f"volgende_btn_{st.session_state.q_index}"):
            if len(st.session_state.answers) == st.session_state.q_index:
                st.session_state.answers.append(opties.index(antwoord) + 1)
            st.session_state.q_index += 1
else:
    st.success("✅ Je hebt alle vragen beantwoord!")
    df["antwoord"] = st.session_state.answers

    # ---- SCORE ANALYSE ----
    x_score = df[df["x_as"].notna()]["antwoord"].sum()
    y_score = df[df["y_as"].notna()]["antwoord"].sum()
    max_x = len(df[df["x_as"].notna()]) * 5
    max_y = len(df[df["y_as"].notna()]) * 5
    x_norm = round((x_score / max_x) * 100)
    y_norm = round((y_score / max_y) * 100)

    st.subheader("📊 Jouw positie in het FitKompas")
    if x_norm < 50 and y_norm < 50:
        kwadrant = "Niet actief & niet gemotiveerd"
        uitleg = "Je hebt zowel een lage actief-score als een lage motivatie-score. Zet kleine stappen richting verandering."
        kleur = "#ffcccc"
    elif x_norm < 50 and y_norm >= 50:
        kwadrant = "Niet actief & wél gemotiveerd"
        uitleg = "Je motivatie is aanwezig, maar je gedrag blijft achter. Zet concrete actiepunten om je motivatie te benutten."
        kleur = "#fff3cd"
    elif x_norm >= 50 and y_norm < 50:
        kwadrant = "Wél actief & niet gemotiveerd"
        uitleg = "Je doet al veel, maar voelt weinig motivatie. Onderzoek wat jou zou kunnen inspireren om dit vast te houden."
        kleur = "#ffe0b2"
    else:
        kwadrant = "Wél actief & wél gemotiveerd"
        uitleg = "Je bent goed op weg! Je gedrag en motivatie versterken elkaar. Houd dit vol en inspireer anderen."
        kleur = "#d4edda"

    st.markdown(f"**Kwadrant:** {kwadrant}")
    st.info(uitleg)

    # ---- PLOT ----
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=0, x1=50, y1=50, fillcolor="#ffcccc", opacity=0.4)
    fig.add_shape(type="rect", x0=0, y0=50, x1=50, y1=100, fillcolor="#fff3cd", opacity=0.4)
    fig.add_shape(type="rect", x0=50, y0=0, x1=100, y1=50, fillcolor="#ffe0b2", opacity=0.4)
    fig.add_shape(type="rect", x0=50, y0=50, x1=100, y1=100, fillcolor="#d4edda", opacity=0.4)
    fig.add_shape(type="line", x0=50, y0=0, x1=50, y1=100, line=dict(color="black", dash="dash"))
    fig.add_shape(type="line", x0=0, y0=50, x1=100, y1=50, line=dict(color="black", dash="dash"))
    fig.add_trace(go.Scatter(x=[x_norm], y=[y_norm], mode='markers+text', marker=dict(size=12, color='black'), text=["Jij"], textposition="top center"))
    fig.update_layout(xaxis=dict(range=[0,100], title="Actief"), yaxis=dict(range=[0,100], title="Gemotiveerd"), height=400, showlegend=False)
    st.plotly_chart(fig)

    # ---- THEMA SCORE ----
    st.subheader("📚 Gemiddelde score per thema")
    thema_scores = df.groupby("thema")["antwoord"].mean().sort_values(ascending=False)
    for thema, score in thema_scores.items():
        st.markdown(f"**{thema}**: {round(score, 1)} / 5")

    # ---- RESET ----
    if st.button("Opnieuw starten"):
        st.session_state.q_index = 0
        st.session_state.answers = []
        st.experimental_rerun()
