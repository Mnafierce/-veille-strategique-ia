import streamlit as st
from datetime import datetime
import feedparser
import pdfkit
import os
import requests
import urllib.parse
from dotenv import load_dotenv
import plotly.express as px

# 🔐 Load env
load_dotenv()
serpapi_key = os.getenv("SERPAPI_KEY")

st.set_page_config(page_title="AgentWatch IA", layout="wide", page_icon="🧠")

# 💼 STYLE VISUEL PRO
st.markdown("""
    <style>
        .main {background-color: #f4f6f9;}
        h1, h2, h3, h4 {color: #032D60;}
        .stButton > button {background-color: #00A1E0; color: white;}
    </style>
""", unsafe_allow_html=True)

# 📡 Simulation de cache de données (refresh toutes les 2h)
@st.cache_data(ttl=7200)
def search_arxiv(query="autonomous AI agents", max_results=5):
    base_url = "http://export.arxiv.org/api/query?"
    encoded_query = urllib.parse.quote(query)
    query_url = f"search_query=all:{encoded_query}&start=0&max_results={max_results}&sortBy=lastUpdatedDate&sortOrder=descending"
    feed = feedparser.parse(base_url + query_url)
    results = []
    for entry in feed.entries:
        results.append({
            "title": entry.title,
            "summary": entry.summary,
            "link": entry.link,
            "published": entry.published
        })
    return results

def get_google_news(query, api_key, max_results=5):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "tbm": "nws",
        "api_key": api_key,
        "num": max_results
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("news_results", [])
    return []

def get_insights_data(secteur, pays, entreprise):
    data = {
        "Santé": [
            "Pfizer investit dans des agents IA pour le suivi post-opératoire.",
            "Mayo Clinic pilote un programme IA pour le tri des patients chroniques."
        ],
        "Finance": [
            "JP Morgan lance un assistant IA pour la gestion de portefeuille.",
            "Goldman Sachs utilise des IA pour la détection de fraude en temps réel."
        ],
        "Éducation": [
            "Coursera explore l'usage d'agents IA pour le tutorat personnalisé.",
            "EdTech startups lèvent 200M$ pour intégrer IA dans l’apprentissage adaptatif."
        ],
        "Retail": [
            "Amazon expérimente des agents IA autonomes dans la gestion de stock.",
            "Zara intègre un agent IA de prédiction de tendances de mode."
        ]
    }

    pays_note = f"📍 Activités IA repérées en **{pays}**" if pays != "Tous" else ""
    entreprise_note = f"🔎 Focus sur **{entreprise}**" if entreprise != "Toutes" else ""

    return data.get(secteur, []), pays_note, entreprise_note

# 🎛️ FILTRES
st.sidebar.header("🎛️ Filtres")
secteurs = ["Tous", "Santé", "Finance", "Éducation", "Retail"]
pays = ["Tous", "Canada", "États-Unis", "France", "Allemagne"]
entreprises = ["Toutes", "Pfizer", "JP Morgan", "Mayo Clinic", "OpenAI", "Amazon", "Coursera", "Zara"]

selected_secteur = st.sidebar.selectbox("Secteur d'activité", secteurs)
selected_pays = st.sidebar.selectbox("Pays", pays)
selected_entreprise = st.sidebar.selectbox("Entreprise", entreprises)
search_keyword = st.sidebar.text_input("🔍 Mot-clé libre", "autonomous AI agents")

# 📊 Bouton principal
generate = st.button("📊 Générer le rapport")

# 📈 Indicateurs
st.header("📈 Indicateurs stratégiques")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💰 Investissements IA", "620M$", "+14%")
with col2:
    st.metric("🤖 Agents autonomes", "42 projets", "+7 ce mois")
with col3:
    st.metric("🌍 Pays impliqués", "5+", "")

df = {
    "Mois": ["Jan", "Fév", "Mars", "Avr"],
    "Santé": [10, 12, 15, 18],
    "Finance": [8, 9, 14, 17]
}
fig = px.line(df, x="Mois", y=["Santé", "Finance"], title="Évolution des projets IA")
st.plotly_chart(fig, use_container_width=True)

# RAPPORT
if generate:
    st.success("✅ Rapport généré avec succès !")

    st.header("🧠 Résultats stratégiques")
    arxiv_query = f"{search_keyword} {selected_entreprise} {selected_secteur}"
    articles = search_arxiv(arxiv_query)

    if articles:
        with st.expander("🔬 Recherches Arxiv"):
            for article in articles:
                st.markdown(f"### [{article['title']}]({article['link']})")
                st.caption(f"📅 {article['published']}")
                st.markdown(article['summary'][:400] + "...")
                st.markdown("---")

    if selected_entreprise != "Toutes":
        with st.expander("🗞️ Google News – Actualités récentes"):
            if not serpapi_key:
                st.error("Clé API SerpAPI manquante.")
            else:
                news = get_google_news(f"{selected_entreprise} {search_keyword}", serpapi_key)
                if news:
                    for n in news:
                        st.markdown(f"### [{n['title']}]({n['link']})")
                        st.caption(f"🕒 {n.get('date', 'Date non précisée')}")
                        st.markdown(n.get("snippet", "..."))
                        st.markdown("---")
                else:
                    st.warning("Aucune actualité trouvée.")

    st.subheader("📄 Synthèse par secteur")
    if selected_entreprise == "Toutes":
        for ent in entreprises[1:]:
            st.markdown(f"### 🔹 {ent}")
            insights, _, _ = get_insights_data(selected_secteur, selected_pays, ent)
            for i in insights:
                st.markdown(f"- {i}")
            st.markdown("---")
    else:
        insights, note_pays, note_entreprise = get_insights_data(selected_secteur, selected_pays, selected_entreprise)
        for i in insights:
            st.markdown(f"- {i}")
        st.markdown(note_pays)
        st.markdown(note_entreprise)

    st.markdown(f"🕒 Rapport généré le : **{datetime.now().strftime('%d %B %Y')}**")

    # 📤 PDF EXPORT
    if st.button("📥 Télécharger ce rapport en PDF"):
        insights_html = "".join(f"<li>{i}</li>" for i in insights)
        html = f"""
        <html><head><meta charset='UTF-8'></head><body>
        <h1>Rapport IA – {selected_entreprise}</h1>
        <p><strong>Secteur :</strong> {selected_secteur}</p>
        <p><strong>Pays :</strong> {selected_pays}</p>
        <p><strong>Date :</strong> {datetime.now().strftime('%d %B %Y')}</p>
        <h2>🧠 Informations clés</h2>
        <ul>{insights_html}</ul>
        <p>{note_pays}</p><p>{note_entreprise}</p>
        </body></html>
        """
        pdfkit.from_string(html, "rapport_ia.pdf")
        with open("rapport_ia.pdf", "rb") as f:
            st.download_button("📄 Télécharger le PDF", f, file_name="rapport_ia.pdf")




