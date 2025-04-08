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
notion_token = os.getenv("NOTION_TOKEN")
notion_db = os.getenv("NOTION_DB_ID")

#Bloc schedule
def schedule_job():
    schedule.every(24).hours.do(update_tendances) 
    while True:
        schedule.run_pending()
        time.sleep(1)

# 🔁 Lancer le thread de mise à jour automatique
threading.Thread(target=schedule_job, daemon=True).start()

# Lancer une 1re mise à jour au démarrage
update_tendances()

st.set_page_config(page_title="AgentWatch AI", layout="wide", page_icon="🤖")
st.markdown("""
    <style>
        .main {background-color: #f4f6f9;}
        h1, h2, h3 {color: #032D60;}
        .stButton>button {background-color: #00A1E0; color: white;}
    </style>
""", unsafe_allow_html=True)

st.title("🧠 AgentWatch AI – Veille Stratégique IA")
st.markdown("**Analyse des avancées en agents IA autonomes dans la santé et la finance.**")

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

# 🔁 Mise à jour automatique des tendances (tâche planifiée)
tendances_ia = {"sante": [], "finance": [], "last_update": ""}

def update_tendances():
    global tendances_ia
    keywords_sante = "healthcare AI agent OR autonomous medical agent OR diagnostic AI OR patient AI"
    keywords_finance = "finance AI agent OR investment AI OR fraud detection AI OR autonomous finance agent"

    tendances_ia["sante"] = search_arxiv(query=keywords_sante, max_results=3) + get_google_news(keywords_sante, serpapi_key, max_results=2)
    tendances_ia["finance"] = search_arxiv(query=keywords_finance, max_results=3) + get_google_news(keywords_finance, serpapi_key, max_results=2)
    tendances_ia["last_update"] = datetime.now().strftime("%d %B %Y – %H:%M")

# Filtre utilisateur (sidebar)
generate = st.sidebar.button("📊 Générer le rapport stratégique")
st.sidebar.markdown(f"📅 **Dernière mise à jour :** {datetime.now().strftime('%d %B %Y')}")
st.sidebar.header("🎛️ Filtres")

secteurs = ["Santé", "Finance"]
pays = ["Tous", "Canada", "États-Unis", "France", "Allemagne"]
entreprises = ["Toutes", "Pfizer", "JP Morgan", "Mayo Clinic", "OpenAI", "Amazon"]

selected_secteur = st.sidebar.selectbox("📂 Secteur", secteurs)
selected_pays = st.sidebar.selectbox("🌍 Pays", pays)
selected_entreprise = st.sidebar.selectbox("🏢 Entreprise", entreprises)
search_keyword = st.sidebar.text_input("🔍 Recherche libre", value="autonomous AI agents")
update = st.sidebar.button("🔄 Mettre à jour les infos")

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
    # Requête limitée aux 7 derniers jours (environ)
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
    response = requests.get("https://serpapi.com/search", params={
        "engine": "google", "q": query, "tbm": "nws", "api_key": api_key, "num": max_results
    })
    return response.json().get("news_results", []) if response.status_code == 200 else []


# 🔍 analyse_salesforce
def analyse_salesforce(secteur, pays, entreprise, insights, articles, news):
    st.markdown("### 🧠 Recommandation stratégique Salesforce")
    recommandations = []

   # 📡 Tendances dynamiques affichées à l'écran
st.header("📡 Tendances par secteur – Santé & Finance")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏥 Santé")
    for item in tendances_ia["sante"]:
        titre = item.get("title") or item.get("title", "Sans titre")
        lien = item.get("link") or "#"
        st.markdown(f"📌 [{titre}]({lien})")

with col2:
    st.subheader("💰 Finance")
    for item in tendances_ia["finance"]:
        titre = item.get("title") or item.get("title", "Sans titre")
        lien = item.get("link") or "#"
        st.markdown(f"📌 [{titre}]({lien})")

st.caption(f"⏱ Données actualisées le : {tendances_ia['last_update']}")

    # 🔬 Analyse des publications scientifiques (Arxiv)
for article in articles:
        summary = article.get("summary", "").lower()

        if secteur == "Santé":
            if "diagnostic" in summary:
                recommandations.append("🧠 Créer un module IA d’aide au diagnostic dans Salesforce HealthCloud.")
            if "predictive model" in summary or "prediction" in summary:
                recommandations.append("📈 Utiliser un modèle prédictif connecté à Salesforce pour anticiper les risques médicaux.")

        elif secteur == "Finance":
            if "risk" in summary or "forecast" in summary:
                recommandations.append("📊 Intégrer une IA de prévision de risque dans Financial Services Cloud.")
            if "autonomous agent" in summary:
                recommandations.append("🤖 Étudier l’intégration d’agents autonomes dans les processus de scoring.")

    # 🗞️ Analyse optionnelle des actualités
for article in news:
        snippet = article.get("snippet", "").lower()

        if secteur == "Santé" and "ai" in snippet and "patient" in snippet:
            recommandations.append("💬 Développer un agent conversationnel IA pour le suivi patient dans HealthCloud.")
        elif secteur == "Finance" and "investment" in snippet:
            recommandations.append("📉 Étendre Salesforce avec une IA d’analyse des comportements d’investissement.")

    # Fallback
    if not recommandations:
        recommandations.append("🧭 Explorer les dernières intégrations IA dans l’environnement Salesforce pour ce secteur.")

    # Affichage
    for reco in recommandations:
        st.info(f"💡 {reco}")
    
# 🔎 Analyse des études Arxiv
    for article in articles:
        summary = article["summary"].lower()
        if secteur == "Santé":
            if "diagnostic" in summary:
                recommandations.append("Créer un outil d’aide au diagnostic connecté à Salesforce HealthCloud.")
            if "predictive model" in summary:
                recommandations.append("Intégrer un modèle prédictif de pathologie dans Salesforce.")
        elif secteur == "Finance":
            if "forecast" in summary or "risk" in summary:
                recommandations.append("Déployer une IA de prévision des risques dans Salesforce Financial Cloud.")
            if "autonomous agent" in summary:
                recommandations.append("Étudier l'intégration d'agents autonomes dans les processus de scoring.")


# 🧠 Synthèse ou fallback
    if not recommandations:
        recommandations.append("Explorer des cas d’intégration IA récents dans l’environnement Salesforce.")

    for reco in recommandations:
        st.info(f"💡 {reco}")


# 📡 Tendances dynamiques (recherches automatisées)
st.header("📡 Tendances IA en Santé & Finance – Dernières 24h")

keywords_sante = "healthcare AI agent OR autonomous medical agent OR diagnostic AI OR patient AI"
keywords_finance = "finance AI agent OR investment AI OR fraud detection AI OR autonomous finance agent"

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

# Requête Arxiv + News par secteur
articles_sante = search_arxiv(query=keywords_sante, max_results=3)
articles_finance = search_arxiv(query=keywords_finance, max_results=3)
news_sante = get_google_news(keywords_sante, serpapi_key, max_results=2)
news_finance = get_google_news(keywords_finance, serpapi_key, max_results=2)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏥 Santé – Recherches et News")
    if articles_sante:
        for a in articles_sante:
            st.markdown(f"📘 [{a['title']}]({a['link']}) — *{a['published'][:10]}*")
    if news_sante:
        for n in news_sante:
            st.markdown(f"🗞️ [{n['title']}]({n['link']})")

with col2:
    st.subheader("💰 Finance – Recherches et News")
    if articles_finance:
        for a in articles_finance:
            st.markdown(f"📘 [{a['title']}]({a['link']}) — *{a['published'][:10]}*")
    if news_finance:
        for n in news_finance:
            st.markdown(f"🗞️ [{n['title']}]({n['link']})")

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


# 🧠 Recommandation stratégique Salesforce
def analyse_salesforce(secteur, entreprise, insights, articles, news):
    st.markdown("### 🧠 Recommandation stratégique Salesforce")
    recommandations = []

    for insight in insights:
        if secteur == "Santé" and ("suivi" in insight.lower() or "tri" in insight.lower()):
            recommandations.append("Déployer un agent IA dans Salesforce HealthCloud.")
        if secteur == "Finance" and "portefeuille" in insight.lower():
            recommandations.append("Intégrer un assistant IA dans Financial Services Cloud.")

    for article in articles:
        s = article["summary"].lower()
        if secteur == "Santé" and "diagnostic" in s:
            recommandations.append("Créer un outil IA pour l’aide au diagnostic dans Salesforce.")
        if secteur == "Finance" and ("forecast" in s or "risk" in s):
            recommandations.append("Ajouter un modèle prédictif de risque dans Financial Cloud.")

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


# ▶️ Lancement du rapport stratégique
if generate:
    st.success("✅ Rapport généré avec succès")
    ...
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
