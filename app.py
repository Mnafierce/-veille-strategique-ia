import streamlit as st 
from datetime import datetime
import feedparser
import pdfkit
import os
import requests
import urllib.parse
import plotly.express as px
import pandas as pd
import schedule
import threading
import time
from dotenv import load_dotenv
from notion_client import Client


# 🔐 Charger la clé API depuis .env
load_dotenv()
serpapi_key = os.getenv("SERPAPI_KEY")

# 🎨 Thème Salesforce
st.set_page_config(page_title="AgentWatch AI", layout="wide", page_icon="🤖")
st.markdown("""
    <style>
        .main {background-color: #f4f6f9;}
        h1, h2, h3 {color: #032D60;}
        .stButton>button {background-color: #00A1E0; color: white;}
    </style>
""", unsafe_allow_html=True)

# 🌐 Configuration Streamlit
st.title("🧠 AgentWatch AI – Veille Stratégique IA")
st.markdown("**Analyse des avancées en agents IA autonomes dans les secteurs stratégiques.**")

# 🔐 Charger les variables d'environnement
load_dotenv()
serpapi_key = os.getenv("SERPAPI_KEY")
notion_token = os.getenv("NOTION_TOKEN")
notion_db = os.getenv("NOTION_DB_ID")

# ⏱ Rafraîchissement automatique
def schedule_job():
    schedule.every(2).hours.do(lambda: print("🔁 Données mises à jour."))
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=schedule_job, daemon=True).start()

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

# 🔄 Sections dynamiques
if update:

    # 📰 Recherches scientifiques (Arxiv)
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

    # 📄 Rapport Stratégique
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

    # 📤 Export PDF (option mono-entreprise uniquement)
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

# 🔄 Sections dynamiques après clic sur le bouton
if update:

    # 📰 Recherches scientifiques (Arxiv)
    st.header("📰 Recherches scientifiques (Arxiv)")
    query = f"{selected_entreprise} {selected_secteur} autonomous agents"
    articles = search_arxiv(query=query)

if update:
    st.header("📰 Recherches scientifiques (Arxiv)")
    query = f"{selected_entreprise} {selected_secteur} autonomous agents"
    articles = search_arxiv(query)

    if articles:
        for article in articles:
            st.markdown(f"### [{article['title']}]({article['link']})")
            st.markdown(f"📅 {article['published']}")
            st.markdown(article['summary'][:400] + "...")
            st.markdown("---")
    else:
        st.warning("Aucun article scientifique trouvé pour ces filtres.")


# 🧠 Recommandation stratégique Salesforce
def analyse_salesforce(secteur, entreprise, insights):
    reco = {
        "Santé": "Créer un agent Salesforce HealthCloud pour suivi post-chirurgical.",
        "Finance": "Déployer un assistant IA Einstein pour scoring de portefeuille.",
        "Retail": "Connecter IA de prévision de tendance à Salesforce Commerce Cloud.",
        "Éducation": "Intégrer un chatbot IA dans Salesforce Education Cloud."
    }
    st.markdown("### 🧠 Recommandation stratégique Salesforce")
    st.info(f"""
**Secteur :** {secteur} | **Entreprise :** {entreprise}  
**Insight détecté :** {insights[0] if insights else "N/A"}  
**Recommandation :** {reco.get(secteur, "Explorer les cas IA applicables au CRM.")}  
    """)

# 📊 Visualisations dynamiques
def afficher_graphiques_secteur():
    st.subheader("📈 Statistiques par secteur")
    df = pd.DataFrame({
        "Mois": ["Jan", "Fév", "Mars", "Avr"],
        "Santé": [10, 14, 18, 22],
        "Finance": [8, 10, 14, 19]
    })
    fig = px.line(df, x="Mois", y=["Santé", "Finance"], title="Évolution des projets IA", markers=True)
    st.plotly_chart(fig, use_container_width=True)

    pie = px.pie(
        names=["Agent diagnostic", "NLP", "Support client", "Investissement", "Prévision"], 
        values=[20, 25, 15, 30, 10],
        title="Répartition des types d’agents IA observés"
    )
    st.plotly_chart(pie, use_container_width=True)

# 📌 Plan d’action stratégique
    def afficher_plan_action(secteur, entreprise):
        st.subheader("📌 Plan d’action stratégique")
        actions = {
            "Santé": [
                "✅ Analyser les parcours patients et intégrer un agent IA de suivi",
                "✅ Créer un partenariat avec une startup MedTech IA",
                "✅ Déployer un pilote sur un cas d’usage clinique ciblé"
            ],
            "Finance": [
                "✅ Intégrer un assistant IA dans l’espace client Salesforce",
                "✅ Automatiser la détection de risque avec des agents LLM",
                "✅ Évaluer l’impact réglementaire des IA autonomes"
            ],
            "Retail": [
                "✅ Déployer un agent IA prédictif sur les tendances d’achat",
                "✅ Analyser les comportements clients pour la personnalisation",
                "✅ Former les équipes CRM aux outils augmentés IA"
            ],
            "Éducation": [
                "✅ Lancer un chatbot IA pour suivi étudiant",
                "✅ Partenariat EdTech pour apprentissage personnalisé",
                "✅ Suivi des progrès en temps réel pour les enseignants"
            ]
    }
    for action in actions.get(secteur, ["⚠️ Analyse IA stratégique en cours."]):
        st.markdown(action)

# 📄 Rapport Stratégique
    st.header("📄 Rapport Stratégique")

if selected_entreprise == "Toutes":
    st.subheader("📊 Rapport multi-entreprise")

    for ent in entreprises[1:]:  # on saute "Toutes"
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


# 📤 Export PDF sécurisé
def export_pdf(secteur, entreprise, insights):
    try:
        html = f"""
        <html><head><meta charset='UTF-8'></head><body>
        <h1>Rapport Stratégique IA</h1>
        <p><strong>Secteur :</strong> {secteur}</p>
        <p><strong>Entreprise :</strong> {entreprise}</p>
        <p><strong>Date :</strong> {datetime.now().strftime('%d %B %Y')}</p>
        <ul>{''.join(f"<li>{i}</li>" for i in insights)}</ul>
        </body></html>
        """
        pdfkit.from_string(html, "rapport_ia.pdf")
        with open("rapport_ia.pdf", "rb") as f:
            st.download_button("📥 Télécharger le rapport PDF", f, file_name="rapport_ia.pdf")
    except OSError:
        st.error("❌ wkhtmltopdf non trouvé. Veuillez l’installer ou le configurer.")

# 🗃️ Enregistrement dans Notion
def enregistrer_dans_notion(titre, contenu, secteur, entreprise):
    if not notion_token or not notion_db:
        st.warning("⚠️ Configuration Notion manquante.")
        return

    notion = Client(auth=notion_token)
    notion.pages.create(
        parent={"database_id": notion_db},
        properties={
            "Nom": {"title": [{"text": {"content": titre}}]},
            "Secteur": {"rich_text": [{"text": {"content": secteur}}]},
            "Entreprise": {"rich_text": [{"text": {"content": entreprise}}]},
            "Date": {"date": {"start": datetime.now().isoformat()}}
        },
        children=[{
            "object": "block", "type": "paragraph",
            "paragraph": {"text": [{"type": "text", "text": {"content": contenu}}]}
        }]
    )

# 🎛️ Interface - Filtres utilisateurs
st.sidebar.header("🎛️ Filtres de veille stratégique")
secteurs = ["Tous", "Santé", "Finance", "Éducation", "Retail"]
pays = ["Tous", "Canada", "États-Unis", "France", "Allemagne"]
entreprises = ["Toutes", "Pfizer", "JP Morgan", "Mayo Clinic", "OpenAI", "Amazon", "Coursera", "Zara"]

selected_secteur = st.sidebar.selectbox("📂 Secteur", secteurs)
selected_pays = st.sidebar.selectbox("🌍 Pays", pays)
selected_entreprise = st.sidebar.selectbox("🏢 Entreprise", entreprises)
search_keyword = st.sidebar.text_input("🔍 Recherche libre", value="autonomous AI agents")

generate = st.sidebar.button("📊 Générer le rapport stratégique")

# ▶️ Lancement du rapport stratégique
if generate:
    st.success("✅ Rapport généré avec succès")
    st.markdown("---")

    if selected_entreprise != "Toutes":
        score_ia = {
            "Pfizer": 82,
            "JP Morgan": 91,
            "Mayo Clinic": 88,
            "OpenAI": 99,
            "Amazon": 95,
            "Coursera": 76,
            "Zara": 68
        }
        score = score_ia.get(selected_entreprise)
        if score:
            st.subheader("🧮 Score de maturité IA")
            st.metric(label="Niveau technologique estimé", value=f"{score}/100")
            st.progress(score / 100)

    st.subheader("📌 Synthèse stratégique")
    insights = get_insights_data(selected_secteur)
    if insights:
        for i in insights:
            st.markdown(f"- {i}")
    else:
        st.warning("Aucun insight détecté.")

    analyse_salesforce(selected_secteur, selected_entreprise, insights)
    afficher_graphiques_secteur()
    afficher_plan_action(selected_secteur, selected_entreprise)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Télécharger le rapport en PDF"):
            export_pdf(selected_secteur, selected_entreprise, insights)

    with col2:
        if st.button("🗃 Enregistrer dans Notion"):
            contenu = f"Insights : {' | '.join(insights)}"
            enregistrer_dans_notion("Rapport IA", contenu, selected_secteur, selected_entreprise)
            st.success("Rapport enregistré dans Notion ✅")

# ✅ Footer
st.markdown("---")
st.markdown("🧠 *Propulsé par AgentWatch AI — Salesforce Strategy Pilot v1.0*")
