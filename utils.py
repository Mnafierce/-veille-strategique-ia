import streamlit as st
from datetime import datetime
import plotly.express as px
from notion_client import Client
import urllib.parse
import feedparser
import pandas as pd
import plotly.express as px

# 🔍 Requête Arxiv
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

# 📄 Données d’analyse pour le rapport
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

# 🗃️ Enregistrement dans Notion
def enregistrer_dans_notion(titre, contenu, secteur, pays, entreprise):
    notion_token = st.secrets.get("NOTION_TOKEN")
    notion_db = st.secrets.get("NOTION_DB_ID")

    if not notion_token or not notion_db:
        st.warning("⚠️ Clé API ou ID Notion manquant.")
        return

    notion = Client(auth=notion_token)
    notion.pages.create(
        parent={"database_id": notion_db},
        properties={
            "Nom": {"title": [{"text": {"content": titre}}]},
            "Secteur": {"rich_text": [{"text": {"content": secteur}}]},
            "Pays": {"rich_text": [{"text": {"content": pays}}]},
            "Entreprise": {"rich_text": [{"text": {"content": entreprise}}]},
            "Date": {"date": {"start": datetime.now().isoformat()}}
        },
        children=[{
            "object": "block", "type": "paragraph",
            "paragraph": {"text": [{"type": "text", "text": {"content": contenu}}]}
        }]
    )