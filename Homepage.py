import streamlit as st
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "assets", "images", "Logo-Carmila-CMJN.jpg")

# Configure the page - THIS MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Carmila Dashboard",
    page_icon=logo_path,
    layout="wide"
)

# Custom CSS to incorporate Carmila's brand colors and improved styling
st.markdown("""
    <style>
        /* Main theme color - Carmila Red */
        :root {
            --carmila-red: #E4002B;
        }
        
        /* Title styling */
        .css-10trblm {
            color: var(--carmila-red) !important;
            font-size: 2.5em !important;
            font-weight: 700 !important;
            margin-bottom: 0.5em !important;
        }
        
        /* Subheader styling */
        .css-1fv8s86 {
            color: var(--carmila-red) !important;
            font-size: 1.8em !important;
            font-weight: 600 !important;
            margin-bottom: 1em !important;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: rgba(228, 0, 43, 0.05);
        }
        
        /* Button styling */
        .stButton>button {
            background-color: var(--carmila-red);
            color: white;
            border: none;
            padding: 0.5em 1em;
            border-radius: 5px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            background-color: #c0001f;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }

        /* Card styling */
        .card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
            border-left: 4px solid var(--carmila-red);
        }

        /* Feature box styling */
        .feature-box {
            padding: 1rem;
            background-color: rgba(228, 0, 43, 0.03);
            border-radius: 8px;
            margin-bottom: 1rem;
        }

        /* Divider styling */
        .divider {
            height: 3px;
            background: linear-gradient(90deg, var(--carmila-red) 0%, rgba(228, 0, 43, 0.1) 100%);
            margin: 2rem 0;
        }
    </style>
""", unsafe_allow_html=True)

# Header with logo and title
col1, col2 = st.columns([1, 4])
with col1:
    st.image(logo_path, width=150)
with col2:
    st.title("📊 Tableau de Bord Carmila")
    st.markdown("<p style='font-size: 1.2em; color: #666;'>Solutions d'analyse avancée pour optimiser la performance de vos centres commerciaux</p>", unsafe_allow_html=True)

# Divider
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# Introduction
st.markdown("""
<div class="card">
    <h2 style='color: #E4002B; margin-bottom: 1rem;'>Bienvenue sur la Plateforme d'Analyse Carmila</h2>
    <p style='font-size: 1.1em; line-height: 1.6;'>
        Notre tableau de bord interactif vous offre une vision complète et détaillée de la performance de vos centres commerciaux. 
        Explorez les données, découvrez des tendances et prenez des décisions éclairées basées sur des analyses en temps réel.
    </p>
</div>
""", unsafe_allow_html=True)

# Main Features Section
st.subheader("Fonctionnalités Principales")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3 style='color: #E4002B;'>📊 Analyse des Flux</h3>
        <ul style='list-style-type: none; padding-left: 0;'>
            <li>✓ Suivi en temps réel des entrées</li>
            <li>✓ Analyse des pics d'affluence</li>
            <li>✓ Comparaison entre centres</li>
            <li>✓ Prévisions de fréquentation</li>
        </ul>
    </div>
    
    <div class="feature-box">
        <h3 style='color: #E4002B;'>💰 Performance Commerciale</h3>
        <ul style='list-style-type: none; padding-left: 0;'>
            <li>✓ Suivi du chiffre d'affaires</li>
            <li>✓ Analyse par secteur d'activité</li>
            <li>✓ Indicateurs de performance clés</li>
            <li>✓ Tableaux de bord personnalisés</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h3 style='color: #E4002B;'>📈 Impact des Événements</h3>
        <ul style='list-style-type: none; padding-left: 0;'>
            <li>✓ Mesure de l'impact des animations</li>
            <li>✓ Analyse des périodes spéciales</li>
            <li>✓ Suivi des campagnes marketing</li>
            <li>✓ Recommandations d'optimisation</li>
        </ul>
    </div>
    
    <div class="feature-box">
        <h3 style='color: #E4002B;'>🎯 Objectifs et Prévisions</h3>
        <ul style='list-style-type: none; padding-left: 0;'>
            <li>✓ Définition d'objectifs personnalisés</li>
            <li>✓ Suivi des performances</li>
            <li>✓ Alertes et notifications</li>
            <li>✓ Rapports automatisés</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Call to Action
st.markdown("""
<div style='text-align: center; padding: 2rem; background-color: rgba(228, 0, 43, 0.03); border-radius: 10px; margin-top: 2rem;'>
    <h2 style='color: #E4002B; margin-bottom: 1rem;'>Commencez votre Analyse</h2>
    <p style='font-size: 1.1em; margin-bottom: 1.5rem;'>
        Sélectionnez une section dans le menu de gauche pour explorer les différentes analyses disponibles.
    </p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p> 2024 Carmila - Tous droits réservés</p>
</div>
""", unsafe_allow_html=True)