import streamlit as st

st.set_page_config(page_title="AgentWatch IA", layout="wide")

st.title("🧠 AgentWatch AI – Prototype de veille stratégique")
st.markdown("Suivi simple des tendances sur les agents IA autonomes")

st.header("🔍 Tendances simulées (contenu démo)")
st.markdown("""
- **OpenAI** lance une nouvelle version d’agents autonomes spécialisés pour l’e-commerce.
- **Anthropic** collabore avec le secteur bancaire pour des agents de conformité automatisée.
- **Meta** propose des agents IA capables de discuter entre eux sur WhatsApp Business.
- **CB Insights** rapporte une hausse de 78% des investissements en agents IA au Q1 2025.
""")

st.header("📊 Analyse rapide")
st.write("L’écosystème des agents IA se structure autour de 3 axes :")
st.markdown("""
1. **Interopérabilité des agents** (standards d’échange)
2. **Conformité réglementaire** (GDPR, responsabilité)
3. **Cas d’usage concrets** (finance, santé, retail)
""")

st.sidebar.title("🎯 Bientôt ici : Générateur de recommandations IA")
st.sidebar.write("Quand vous aurez une clé OpenAI, ce module s'activera automatiquement.")
