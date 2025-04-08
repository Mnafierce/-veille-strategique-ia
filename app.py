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
from dotenv import load_dotenv
from notion_client import Client

# 🔐 Charger les variables d'environnement
load_dotenv()
serpapi_key = os.getenv("SERPAPI_KEY")
notion_token = os.getenv("NOTION_TOKEN")
notion_db = os.getenv("NOTION_DB_ID")

# 🎨 Thème Salesforce
st.set_page_config(page_title="AgentWatch AI", layout="wide", page_icon="🤖")
st.markdown("""
    <style>
        .main {background-color: #f4f6f9;}
        h1, h2, h3 {color: #032D60;}
        .stButton>button {background-color: #00A1E0; color: white;}
    </style>
""", unsafe_allow_html=True)

# ⏱ Rafraîchissement automatique
import time  # à ajouter en haut

def schedule_job():
    schedule.every(2).hours.do(lambda: print("🔁 Données mises à jour."))
    while True:
        schedule.run_pending()
        time.sleep(1)  # <== essentiel pour éviter le blocage CPU


threading.Thread(target=schedule_job, daemon=True).start()

# 🔍 Recherche Arxiv
def search_arxiv(query="autonomous AI agents", max_results=5):
    base_url = "http://export.arxiv.org/api/query?"
    encoded_query = urllib.parse.quote(query)
    query_url = f"search_query=all:{encoded_query}&start=0&max_results={max_results}&sortBy=lastUpdatedDate&sortOrder=descending"
    feed = feedparser.parse(base_url + query_url)
    return [{
        "title": e.title,
        "summary": e.summary,
        "link": e.link,
        "published": e.published
    } for e in feed.entries]

# 🔬 PubMed API
def search_pubmed(query="AI agents healthcare", max_results=3):
    ids = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params={
        "db": "pubmed", "term": query, "retmode": "json", "retmax": max_results
    }).json().get("esearchresult", {}).get("idlist", [])
    articles = []
    for pmid in ids:
        r = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi", params={
            "db": "pubmed", "id": pmid, "retmode": "json"
        }).json()
        doc = r["result"].get(pmid, {})
        articles.append({
            "title": doc.get("title"),
            "source": doc.get("source"),
            "link": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        })
    return articles

# 📰 Google News via SerpAPI
def get_google_news(query, api_key, max_results=5):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "tbm": "nws",
        "api_key": api_key,
        "num": max_results
    }
    r = requests.get(url, params=params)
    return r.json().get("news_results", []) if r.status_code == 200 else []

# 🎛️ Interface - Filtres
st.title("🧠 AgentWatch AI – Veille Stratégique")
st.markdown("**Analyse des opportunités d'agents IA externes dans la santé, la finance et la technologie.**")

secteurs = ["Tous", "Santé", "Finance", "Éducation", "Retail"]
pays = ["Tous", "Canada", "États-Unis", "France", "Allemagne"]
entreprises = ["Toutes", "Pfizer", "JP Morgan", "Mayo Clinic", "OpenAI", "Amazon", "Coursera", "Zara"]

# Score IA simulé par entreprise (sur 100)
score_ia = {
    "Pfizer": 82,
    "JP Morgan": 91,
    "Mayo Clinic": 88,
    "OpenAI": 99,
    "Amazon": 95,
    "Coursera": 76,
    "Zara": 68
}

# ⬇️ Sélections
col1, col2, col3 = st.columns(3)
selected_secteur = col1.selectbox("📂 Secteur", secteurs)
selected_pays = col2.selectbox("🌍 Pays", pays)
selected_entreprise = col3.selectbox("🏢 Entreprise", entreprises)

search_keyword = st.text_input("🔍 Recherche libre", value="autonomous AI agents")
generate = st.button("📊 Générer le rapport stratégique")

# 🔍 Données internes simulées
def get_insights_data(secteur):
    return {
        "Santé": ["Pfizer développe un agent IA post-op.", "Mayo Clinic teste un triage autonome."],
        "Finance": ["JP Morgan développe un conseiller IA.", "Goldman Sachs automatise la détection de fraude."],
        "Retail": ["Amazon teste IA logistique.", "Zara utilise IA pour prévisions de mode."]
    }.get(secteur, [])

# 🧠 Recommandation stratégique Salesforce
def analyse_salesforce(secteur, entreprise, insights):
    reco = {
        "Santé": "Créer un agent Salesforce HealthCloud pour suivi post-chirurgical.",
        "Finance": "Déployer un assistant IA Einstein pour scoring de portefeuille.",
        "Retail": "Connecter IA de prévision de tendance à Salesforce Commerce Cloud."
    }
    st.markdown("### 🧠 Recommandation stratégique Salesforce")
    st.info(f"""
**Secteur :** {secteur} | **Entreprise :** {entreprise}  
**Insight détecté :** {insights[0] if insights else "N/A"}  
**Recommandation :** {reco.get(secteur, "Explorer les cas IA applicables au CRM.")}  
    """)

# 📊 Visualisations par secteur
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

# 📌 Définition du plan d’action stratégique
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
            "✅ Evaluer l’impact réglementaire des IA autonomes"
        ],
        "Retail": [
            "✅ Déployer un agent IA prédictif sur les tendances d’achat",
            "✅ Analyser les comportements clients pour la personnalisation",
            "✅ Former les équipes CRM aux outils augmentés IA"
        ],
        "Éducation": [
            "✅ Lancer un chatbot IA pour suivi étudiant",
            "✅ Partenariat EdTech pour apprentissage personnalisé",
            "✅ Suivi des progrès en temps réel pour les profs"
        ]
    }
    for action in actions.get(secteur, ["⚠️ Analyse IA stratégique en cours."]):
        st.markdown(action)

# 📌 Plan d’action stratégique
if st.button("📌 Voir le plan d’action stratégique"):
    afficher_plan_action(selected_secteur, selected_entreprise)


# 📤 PDF Export
def export_pdf(secteur, entreprise, insights):
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
        
def export_pdf(secteur, entreprise, insights):
    try:
        html = f""" ... """
        pdfkit.from_string(html, "rapport_ia.pdf")
        with open("rapport_ia.pdf", "rb") as f:
            st.download_button("📥 Télécharger le rapport PDF", f, file_name="rapport_ia.pdf")
    except OSError:
        st.error("❌ wkhtmltopdf non trouvé. Veuillez l’installer ou le configurer.")


# 🗃️ Enregistrement dans Notion
def enregistrer_dans_notion(titre, contenu, secteur, entreprise):
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
    if not notion_token or not notion_db:
    st.warning("⚠️ Configuration Notion manquante.")
    return


# ▶️ Logique principale déclenchée par le bouton
if generate:
    st.success("✅ Rapport généré avec succès")
    st.markdown("---")

    if selected_entreprise != "Toutes":
        score = score_ia.get(selected_entreprise)
        if score:
            st.subheader("🧮 Score de maturité IA")
            st.metric(label="Niveau technologique estimé", value=f"{score}/100")
            st.progress(score / 100)

    # 🔎 Récupération des données
    arxiv_query = f"{search_keyword} {selected_entreprise} {selected_secteur}"
    articles = search_arxiv(arxiv_query)
    pubmed = search_pubmed(f"{search_keyword} {selected_secteur}")
    news = get_google_news(f"{selected_entreprise} {search_keyword}", serpapi_key) if selected_entreprise != "Toutes" else []

    # 📚 Affichage des résultats
    st.subheader("📚 Études scientifiques – Arxiv")
    if articles:
        for a in articles:
            st.markdown(f"**[{a['title']}]({a['link']})**\n> {a['published']}\n\n{a['summary'][:300]}...")
    else:
        st.info("Aucune publication Arxiv trouvée.")

    st.subheader("🧬 Recherches médicales – PubMed")
    if pubmed:
        for p in pubmed:
            st.markdown(f"🔗 [{p['title']}]({p['link']}) – _{p['source']}_")
    else:
        st.info("Aucune donnée PubMed trouvée.")

    if news:
        st.subheader("🗞️ Actualités – Google News")
        for n in news:
            st.markdown(f"**[{n['title']}]({n['link']})**\n> {n.get('snippet', '...')}")

    # 📌 Analyse stratégique
    st.subheader("📌 Synthèse stratégique")
    insights = get_insights_data(selected_secteur)
    if insights:
        for i in insights:
            st.markdown(f"- {i}")
    else:
        st.warning("Aucun insight détecté.")

    # 🧠 Analyse Salesforce
    analyse_salesforce(selected_secteur, selected_entreprise, insights)

    # 📈 Graphiques
    afficher_graphiques_secteur()

    # 📌 Plan d'action
    afficher_plan_action(selected_secteur, selected_entreprise)

    # 📤 Boutons PDF & Notion
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("📥 Télécharger le rapport en PDF"):
            export_pdf(selected_secteur, selected_entreprise, insights)
        
        if insights:
    with col1:
        if st.button("📥 Télécharger le rapport en PDF"):
            export_pdf(selected_secteur, selected_entreprise, insights)


    with col2:
        if st.button("🗃 Enregistrer dans Notion"):
            contenu = f"Insights : {' | '.join(insights)}"
            enregistrer_dans_notion("Rapport IA", contenu, selected_secteur, selected_entreprise)
            st.success("Rapport enregistré dans Notion ✅")

st.markdown("---")
st.markdown("🧠 *Propulsé par AgentWatch AI — Salesforce Strategy Pilot v1.0*")

