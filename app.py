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

st.set_page_config(page_title="AgentWatch AI", layout="wide", page_icon="🤖")
st.markdown("""
    <style>
        .main {background-color: #f4f6f9;}
        h1, h2, h3 {color: #032D60;}
        .stButton>button {background-color: #00A1E0; color: white;}
    </style>
""", unsafe_allow_html=True)

st.title("🧠 AgentWatch AI – Veille Stratégique IA")
st.markdown("**Analyse continue des avancées technologiques IA dans la santé et la finance.**")

# 🔎 Arxiv
def search_arxiv(query="autonomous AI agents", max_results=5, days=7):
    base_url = "http://export.arxiv.org/api/query?"
    encoded_query = urllib.parse.quote(query)
    url = f"{base_url}search_query=all:{encoded_query}&start=0&max_results={max_results}&sortBy=lastUpdatedDate&sortOrder=descending"

    feed = feedparser.parse(url)
    cutoff = datetime.now() - pd.Timedelta(days=days)
    results = []

    for entry in feed.entries:
        published = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ")
        if published >= cutoff:
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
    return response.json().get("news_results", []) if response.status_code == 200 else []


def schedule_job():
    schedule.every(24).hours.do(update_tendances)
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=schedule_job, daemon=True).start()


# Lancer une 1re mise à jour au démarrage
def update_tendances():
    st.session_state["tendances"] = {"Santé": [], "Finance": []}

def mots_cles (): 
        "Santé": ["healthcare AI", "medical agents", "AI diagnosis", "AI patient care"],
        "Finance": ["AI investment", "AI in banking", "fraud detection AI", "autonomous financial agents"]

for secteur, keywords in mots_cles.items():
    st.header("📡 Tendances par secteur – Santé & Finance")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏥 Santé")
    for t in st.session_state["tendances"]["Santé"]:
        st.markdown(f"- {t}")

with col2:
    st.subheader("💰 Finance")
    for t in st.session_state["tendances"]["Finance"]:
        st.markdown(f"- {t}")

    for secteur, keywords in mots_cles.items():
        for kw in keywords:
            for result in search_arxiv(kw, max_results=1):
                st.session_state["tendances"][secteur].append(f"📚 {result['title']}")
            for article in get_google_news(kw, serpapi_key, max_results=1):
                st.session_state["tendances"][secteur].append(f"🗞️ {article['title']}")
    # Arxiv - Recherches scientifiques
    for secteur, keywords in zip(["Santé", "Finance"], [mots_cles_sante, mots_cles_finance]):
        for kw in keywords:
            results = search_arxiv(query=kw, max_results=1)
            for r in results:
                titre = r["title"]
                st.session_state["tendances"][secteur].append(f"📚 {titre}")

    # SerpAPI - Actualités récentes
    for secteur, keywords in zip(["Santé", "Finance"], [mots_cles_sante, mots_cles_finance]):
        for kw in keywords:
            news = get_google_news(kw, serpapi_key)
            for article in news[:1]:
                st.session_state["tendances"][secteur].append(f"🗞️ {article['title']}")

# Initialisation des tendances à la 1re ouverture
if "tendances" not in st.session_state:
    update_tendances()

# Met à jour au démarrage si non encore chargé
if "tendances" not in st.session_state:
    update_tendances()

st.set_page_config(page_title="AgentWatch AI", layout="wide", page_icon="🤖")
st.markdown("""
    <style>
        .main {background-color: #f4f6f9;}
        h1, h2, h3 {color: #032D60;}
        .stButton>button {background-color: #00A1E0; color: white;}
    </style>
""", unsafe_allow_html=True)

if st.sidebar.button("🔄 Mettre à jour les tendances maintenant"):
    update_tendances()
    st.sidebar.success("Tendances mises à jour !")

st.title("🧠 AgentWatch AI – Veille Stratégique IA")
st.markdown("**Analyse des avancées en agents IA autonomes dans la santé et la finance.**")

# 🔐 Charger les variables d'environnement
load_dotenv()
serpapi_key = os.getenv("SERPAPI_KEY")
notion_token = os.getenv("NOTION_TOKEN")
notion_db = os.getenv("NOTION_DB_ID")

    # Arxiv
for secteur, keywords in zip(["Santé", "Finance"], [mots_cles_sante, mots_cles_finance]):
    for kw in keywords: 
        results = search_arxiv(query=kw, max_results=1)
    for r in results:
                titre = r["title"]
st.session_state["tendances"][secteur].append(f"📚 {titre}")

    # Google News
for secteur, keywords in zip(["Santé", "Finance"], [mots_cles_sante, mots_cles_finance]):
    for kw in keywords:
            news = get_google_news(kw, serpapi_key)
    for article in news[:1]:
        st.session_state["tendances"][secteur].append(f"🗞️ {article['title']}")

if "tendances" not in st.session_state:
    update_tendances()

# Filtre utilisateur (sidebar)
st.sidebar.header("🎛️ Filtres")
generate = st.sidebar.button("📊 Générer le rapport stratégique")
if st.sidebar.button("🔄 Mettre à jour les tendances maintenant"):
    update_tendances()
    st.sidebar.success("✅ Tendances actualisées")

secteurs = ["Santé", "Finance"]
pays = ["Tous", "Canada", "États-Unis", "France", "Allemagne"]
entreprises = ["Toutes", "Pfizer", "JP Morgan", "Mayo Clinic", "OpenAI", "Amazon"]

selected_secteur = st.sidebar.selectbox("📂 Secteur", secteurs)
selected_pays = st.sidebar.selectbox("🌍 Pays", pays)
selected_entreprise = st.sidebar.selectbox("🏢 Entreprise", entreprises)
search_keyword = st.sidebar.text_input("🔍 Recherche libre", value="autonomous AI agents")

st.sidebar.markdown(f"📅 **Dernière mise à jour :** {datetime.now().strftime('%d %B %Y')}")

update = st.sidebar.button("🔄 Mettre à jour les infos")


   # 📡 Tendances dynamiques affichées à l'écran
st.header("📡 Tendances par secteur – Santé & Finance")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏥 Santé")
    for item in tendances["sante"]:
        titre = item.get("title") or item.get("title", "Sans titre")
        lien = item.get("link") or "#"
        st.markdown(f"📌 [{titre}]({lien})")

with col2:
    st.subheader("💰 Finance")
    for item in tendances["finance"]:
        titre = item.get("title") or item.get("title", "Sans titre")
        lien = item.get("link") or "#"
        st.markdown(f"📌 [{titre}]({lien})")

st.caption(f"⏱ Données actualisées le : {tendances['last_update']}")

# 🧠 Recommandation stratégique Salesforce
def analyse_salesforce(secteur, entreprise, insights, articles, news):
    st.markdown("### 🧠 Recommandation stratégique Salesforce")
    recommandations = []

    for insight in insights:
        if secteur == "Santé" and ("suivi" in insight.lower() or "tri" in insight.lower()):
            recommandations.append("Déployer un agent IA dans Salesforce HealthCloud.")
        if secteur == "Finance" and "portefeuille" in insight.lower():
            recommandations.append("Intégrer un assistant IA dans Financial Services Cloud.")
        if "fraude" in insight_lower:
            recommandations.append("Utiliser Einstein GPT pour la détection intelligente de fraude.")

    for article in articles:
        s = article["summary"].lower()
        if secteur == "Santé" and "diagnostic" in s:
            recommandations.append("Créer un outil IA pour l’aide au diagnostic dans Salesforce.")
        if secteur == "Finance" and ("forecast" in s or "risk" in s):
            recommandations.append("Ajouter un modèle prédictif de risque dans Financial Cloud.")
        elif secteur == "Finance":
            if "risk" in summary or "forecast" in summary:
                recommandations.append("Intégrer une IA de prévision de risque dans Financial Services Cloud.")
            if "autonomous agent" in summary:
                recommandations.append("Explorer les agents autonomes pour l’automatisation des processus de scoring.")
    
    for n in news:
        snip = n.get("snippet", "").lower()
        if secteur == "Santé" and "ai" in snip and "patient" in snip:
            recommandations.append("Développer un agent conversationnel patient dans HealthCloud.")
        if secteur == "Finance" and "investment" in snip:
            recommandations.append("Ajouter une IA de scoring d'investissement dans Salesforce.")

    if not recommandations:
        recommandations.append("Explorer des cas d’intégration IA récents dans Salesforce.")

    for reco in recommandations:
        st.info(f"💡 {reco}")

    for article in news:
        snippet = article.get("snippet", "").lower()
        if secteur == "Santé" and "ai" in snippet and "patient" in snippet:
            recommandations.append("Développer un agent conversationnel IA pour le suivi patient dans HealthCloud.")
        elif secteur == "Finance" and "investment" in snippet:
            recommandations.append("Étendre Salesforce avec une IA d’analyse des comportements d’investissement.")

    # 🧭 Fallback
    if not recommandations:
        recommandations.append("🧭 Explorer les dernières intégrations IA dans l’environnement Salesforce pour ce secteur.")


# 📡 Tendances dynamiques (mise à jour auto + manuelle)
if update or generate:
    st.header("📡 Tendances IA – Actualisation intelligente Santé & Finance")

    keywords_sante = "healthcare AI agent OR autonomous medical agent OR diagnostic AI OR patient AI"
    keywords_finance = "finance AI agent OR investment AI OR fraud detection AI OR autonomous finance agent"


    # Recherches dynamiques
    articles_sante = search_arxiv(query=keywords_sante, max_results=3)
    articles_finance = search_arxiv(query=keywords_finance, max_results=3)
    news_sante = get_google_news(keywords_sante, serpapi_key, max_results=2)
    news_finance = get_google_news(keywords_finance, serpapi_key, max_results=2)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏥 Santé")
        if articles_sante:
            for a in articles_sante:
                st.markdown(f"📘 [{a['title']}]({a['link']}) — *{a['published'][:10]}*")
        if news_sante:
            for n in news_sante:
                st.markdown(f"🗞️ [{n['title']}]({n['link']})")

    with col2:
        st.subheader("💰 Finance")
        if articles_finance:
            for a in articles_finance:
                st.markdown(f"📘 [{a['title']}]({a['link']}) — *{a['published'][:10]}*")
        if news_finance:
            for n in news_finance:
                st.markdown(f"🗞️ [{n['title']}]({n['link']})")

    st.caption(f"⏱ Données mises à jour le {datetime.now().strftime('%d %B %Y – %H:%M')}")


# 🔄 Sections dynamiques
if update:
    # Avant : analyse_salesforce(...)
    analyse_salesforce(selected_secteur, selected_entreprise, insights, articles, news)
    arxiv_query = f"{search_keyword} {selected_entreprise} {selected_secteur}"
    articles = search_arxiv(arxiv_query)
    news = get_google_news(f"{selected_entreprise} {search_keyword}", serpapi_key)

    st.header("📚 Études scientifiques (Arxiv)")
    if articles:
        for article in articles:
                st.markdown(f"### [{article['title']}]({article['link']})")
                st.markdown(f"📅 {article['published']}")
                st.markdown(article['summary'][:400] + "...")
    else:
        st.info("Aucune étude Arxiv trouvée.")

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
         st.header("🗞️ Actualités Google News")
    if news:
        for item in news:
            st.markdown(f"### [{item['title']}]({item['link']})")
            st.markdown(item.get("snippet", "Pas de description"))
    else:
        st.warning("Pas d’actualités récentes.")

    insights, note_pays, note_entreprise = get_insights_data(selected_secteur, selected_pays, selected_entreprise)

    # 📄 Rapport Stratégique
    st.header("📄 Rapport Stratégique")
    for i in insights:
        st.markdown(f"- {i}")
    if note_pays: st.markdown(note_pays)
    if note_entreprise: st.markdown(note_entreprise)

    analyse_salesforce(selected_secteur, selected_entreprise, insights, articles, news)

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

def fetch_research_and_news(sector_keywords):
    articles = search_arxiv(query=sector_keywords, max_results=3)
    news = get_google_news(sector_keywords, serpapi_key, max_results=2)
    return articles, news


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
def get_insights_data(secteur, pays, entreprise):
    data = {
        "Santé": [
            "Pfizer investit dans des agents IA pour le suivi post-opératoire.",
            "Mayo Clinic pilote un programme IA pour le tri des patients chroniques."
        ],
        "Finance": [
            "JP Morgan lance un assistant IA pour la gestion de portefeuille.",
            "Goldman Sachs utilise des IA pour la détection de fraude en temps réel."
        ]
    }

    pays_note = f"📍 Activités IA repérées en **{pays}**" if pays != "Tous" else ""
    entreprise_note = f"🔎 Focus sur **{entreprise}**" if entreprise != "Toutes" else ""
    return data.get(secteur, []), pays_note, entreprise_note

# ⬅️ Cette ligne est essentielle pour initialiser insights avant de l'utiliser
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
        st.error("❌ wkhtmltopdf non trouvé.")


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

# ▶️ Lancement du rapport stratégique
if generate:
    st.success("✅ Rapport généré avec succès")
    insights, note_pays, note_entreprise = get_insights_data(selected_secteur, selected_pays, selected_entreprise)
    articles, news = fetch_research_and_news(search_keyword)

    st.subheader("📌 Rapport stratégique – Synthèse")
    for i in insights:
        st.markdown(f"- {i}")
    if note_pays: st.markdown(note_pays)
    if note_entreprise: st.markdown(note_entreprise)

    analyse_salesforce(selected_secteur, selected_entreprise, insights, articles, news)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📤 Export PDF"):
            export_pdf(selected_secteur, selected_entreprise, insights)
    with col2:
        if st.button("🗃 Enregistrer dans Notion"):
            contenu = " | ".join(insights)
            enregistrer_dans_notion("Rapport IA", contenu, selected_secteur, selected_entreprise)
            st.success("Rapport enregistré dans Notion ✅")

# ✅ Footer
st.markdown("---")
st.markdown("🧠 *Propulsé par AgentWatch AI — Salesforce Strategy Pilot v1.0*")
