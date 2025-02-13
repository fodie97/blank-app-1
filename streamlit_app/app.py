import streamlit as st
import os
from pages import analysis_1, analysis_2, analysis_3  # ✅ Import correct

# 📌 Configuration de la page
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "Image Carmila", "Logo-Carmila-CMJN.jpg")

st.set_page_config(page_title="Carmila Dashboard", page_icon=logo_path, layout="wide")

# 📌 Initialisation de session_state pour la navigation
if "page" not in st.session_state:
    st.session_state.page = "Home"

# 📌 Sidebar Navigation
st.sidebar.title("Navigation")
if st.sidebar.button("🏠 Home"):
    st.session_state.page = "Home"
if st.sidebar.button("📊 Analysis Page 1"):
    st.session_state.page = "Analysis Page 1"
if st.sidebar.button("📈 Analysis Page 2"):
    st.session_state.page = "Analysis Page 2"
if st.sidebar.button("📉 Analysis Page 3"):
    st.session_state.page = "Analysis Page 3"

# 📌 Gestion des pages dynamiques
if st.session_state.page == "Home":
    st.title("Carmila Dashboard")
    st.subheader("Empowering your business with data-driven insights.")
    st.write("Bienvenue sur le tableau de bord Carmila.")

else:
    # 📌 Association des pages à leurs modules respectifs
    page_modules = {
        "Analysis Page 1": analysis_1,
        "Analysis Page 2": analysis_2,
        "Analysis Page 3": analysis_3
    }

    # 📌 Exécuter la fonction main() de la page sélectionnée
    if st.session_state.page in page_modules:
        page_modules[st.session_state.page].main()