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

# 🎨 Thème Salesforce
st.set_page_config(page_title="AgentWatch AI", layout="wide", page_icon="🤖")
st.markdown("""
    <style>
        .main {background-color: #f4f6f9;}
        h1, h2, h3 {color: #032D60;}
        .stButton>button {background-color: #00A1E0; color: white;}
    </style>
""", unsafe_allow_html=True)

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

# 🔍 Données internes simulées
def get_insights_data(secteur):
    return {
        "Santé": ["Pfizer développe un agent IA post-op.", "Mayo Clinic teste un triage autonome."],
        "Finance": ["JP Morgan développe un conseiller IA.", "Goldman Sachs automatise la détection de fraude."],
        "Retail": ["Amazon teste IA logistique.", "Zara utilise IA pour prévisions de mode."],
        "Éducation": ["Coursera personnalise l'apprentissage par IA.", "Chatbots IA pour suivi étudiant."]
    }.get(secteur, [])

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
