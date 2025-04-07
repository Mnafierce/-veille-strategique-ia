import streamlit as st
from datetime import datetime
import feedparser
import pdfkit
from dotenv import load_dotenv
import os
import requests
import urllib.parse

# 🔐 Charger les variables d'environnement
load_dotenv()
serpapi_key = os.getenv("SERPAPI_KEY")

# 🔎 Google News via SerpAPI
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
    else:
        return []

# 🔎 Arxiv
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

# 🔍 Données simulées
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

# 🌐 Streamlit config
st.set_page_config(page_title="AgentWatch IA", layout="wide")
st.title("🧠 AgentWatch AI – Veille Stratégique IA")
st.markdown("**Analyse des avancées en agents IA autonomes dans les secteurs stratégiques.**")

# 🎛️ Filtres
st.sidebar.markdown(f"📅 **Dernière mise à jour :** {datetime.now().strftime('%d %B %Y')}")
st.sidebar.header("🎛️ Filtres")

secteurs = ["Tous", "Santé", "Finance", "Éducation", "Retail"]
pays = ["Tous", "Canada", "États-Unis", "France", "Allemagne"]
entreprises = ["Toutes", "Pfizer", "JP Morgan", "Mayo Clinic", "OpenAI", "Amazon", "Coursera", "Zara"]

selected_secteur = st.sidebar.selectbox("Secteur d'activité", secteurs)
selected_pays = st.sidebar.selectbox("Pays", pays)
selected_entreprise = st.sidebar.selectbox("Entreprise", entreprises)
search_keyword = st.sidebar.text_input("🔍 Recherche libre (mot-clé)", value="autonomous AI agents")

st.sidebar.markdown(f"🧠 Vous suivez : **{selected_secteur}** - **{selected_pays}** - **{selected_entreprise}**")
st.sidebar.markdown("---")
update = st.sidebar.button("🔄 Mettre à jour les infos")

# 📡 Tendances générales statiques
st.header("📡 Tendances par secteur")
col1, col2 = st.columns(2)
with col1:
    st.subheader("🏥 Santé")
    st.markdown("""
    - 🧬 **Mayo Clinic** utilise des agents IA pour le tri des patients.
    - 🩺 **Pfizer** teste un agent IA autonome pour le suivi post-traitement.
    - 🧠 Étude Arxiv : "Autonomous Medical Agents 2025".
    """)
with col2:
    st.subheader("💰 Finance")
    st.markdown("""
    - 🏦 **Goldman Sachs** implémente un agent IA pour le monitoring des risques.
    - 💸 **JP Morgan** développe un assistant IA pour l’investissement personnalisé.
    - 📈 CB Insights : +62% d'investissements IA en finance au Q1 2025.
    """)

# 🔄 Requête dynamique
if update:

    # 📰 Arxiv
    st.header("📰 Recherches scientifiques (Arxiv)")
    arxiv_query = f"{search_keyword} {selected_entreprise} {selected_secteur}"
    articles = search_arxiv(query=arxiv_query)

    if articles:
        for article in articles:
            st.markdown(f"### [{article['title']}]({article['link']})")
            st.markdown(f"📅 {article['published']}")
            st.markdown(article['summary'][:400] + "...")
            st.markdown("---")
    else:
        st.warning("Aucun article scientifique trouvé.")

    # 🗞️ Google News
    if selected_entreprise != "Toutes":
        st.header("🗞️ Actualités Google News – Entreprise sélectionnée")

        if not serpapi_key:
            st.error("❌ Clé API SerpAPI manquante. Veuillez configurer dans les secrets.")
        else:
            news_query = f"{selected_entreprise} {search_keyword}"
            news = get_google_news(news_query, serpapi_key)

            if news:
                for n in news:
                    st.markdown(f"### [{n['title']}]({n['link']})")
                    st.markdown(f"🕒 {n.get('date', 'Date non précisée')}")
                    st.markdown(n.get("snippet", "Pas de description disponible."))
                    st.markdown("---")
            else:
                st.warning("Aucune actualité trouvée ou quota atteint.")

    # 📄 Rapport stratégique
    st.header("📄 Rapport Stratégique")
    if selected_entreprise == "Toutes":
        st.subheader("📊 Rapport multi-entreprise")
        for ent in entreprises[1:]:
            st.markdown(f"### 🔹 {ent}")
            insights, _, _ = get_insights_data(selected_secteur, selected_pays, ent)
            if insights:
                for i in insights:
                    st.markdown(f"- {i}")
            else:
                st.markdown("_Aucune donnée disponible._")
            st.markdown("---")
    else:
        insights, note_pays, note_entreprise = get_insights_data(selected_secteur, selected_pays, selected_entreprise)
        st.markdown(f"### 📌 Rapport – {selected_entreprise}")
        if insights:
            for i in insights:
                st.markdown(f"- {i}")
        else:
            st.warning("Aucune donnée disponible.")
        if note_pays:
            st.markdown(note_pays)
        if note_entreprise:
            st.markdown(note_entreprise)

    st.markdown(f"🕒 Rapport généré le : **{datetime.now().strftime('%d %B %Y')}**")

    # 📤 Export PDF (mono-entreprise uniquement)
    if selected_entreprise != "Toutes":
        if st.button("📤 Exporter ce rapport en PDF"):
            st.success("Export en cours...")
            insights_html = "".join(f"<li>{i}</li>" for i in insights)
            html = f"""
            <html><head><meta charset='UTF-8'></head><body>
            <h1>Rapport de veille stratégique IA</h1>
            <hr>
            <p><strong>Secteur :</strong> {selected_secteur}</p>
            <p><strong>Pays :</strong> {selected_pays}</p>
            <p><strong>Entreprise :</strong> {selected_entreprise}</p>
            <p><strong>Date :</strong> {datetime.now().strftime('%d %B %Y')}</p>
            <h2>🧠 Informations clés :</h2>
            <ul>{insights_html}</ul>
            <p>{note_pays}</p>
            <p>{note_entreprise}</p>
            </body></html>
            """
            with st.spinner("Génération du fichier PDF..."):
                pdfkit.from_string(html, "rapport_ia.pdf")
                with open("rapport_ia.pdf", "rb") as f:
                    st.download_button("📥 Télécharger le PDF", f, file_name="rapport_ia.pdf")


