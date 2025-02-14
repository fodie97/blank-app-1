import streamlit as st
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "assets", "images", "Logo-Carmila-CMJN.jpg")

# Configure the page
st.set_page_config(
    page_title="Carmila Dashboard",
    page_icon=logo_path,
    layout="wide"
)

st.title("📊 Carmila Dashboard")
st.subheader("Empowering your business with data-driven insights")

# Description du projet
st.markdown("""
### Bienvenue sur le tableau de bord Carmila

Ce dashboard vous permet d'analyser les performances des centres commerciaux Carmila à travers différentes métriques :

- 📊 **Analyse des flux de visiteurs**
  - Suivi des entrées quotidiennes
  - Temps de visite moyen
  - Comparaison entre centres

- 💰 **Performance des centres**
  - Chiffre d'affaires par centre
  - Évolution mensuelle
  - Analyse des surfaces

- 📈 **Types de commerce**
  - Performance par catégorie
  - Répartition des activités
  - Tendances par secteur
""")