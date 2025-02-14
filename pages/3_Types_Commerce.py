import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Configure the page - THIS MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Types de Commerce",
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

        /* Control panel styling */
        .control-panel {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            margin-bottom: 1rem;
            border: 1px solid rgba(228, 0, 43, 0.1);
        }

        /* Metric container styling */
        .metric-container {
            background-color: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            margin-bottom: 1rem;
            border-top: 3px solid var(--carmila-red);
        }

        /* Plot styling */
        .plot-container {
            background-color: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            margin-top: 1rem;
            border: 1px solid rgba(228, 0, 43, 0.1);
        }

        /* Select box styling */
        .stSelectbox {
            color: #2c3e50;
        }

        /* Slider styling */
        .stSlider {
            color: var(--carmila-red);
        }

        /* Header styling */
        .page-header {
            margin-bottom: 2rem;
            padding: 1rem;
            background: linear-gradient(90deg, rgba(228, 0, 43, 0.05) 0%, rgba(255, 255, 255, 0) 100%);
            border-radius: 10px;
        }

        /* Divider styling */
        .divider {
            height: 3px;
            background: linear-gradient(90deg, var(--carmila-red) 0%, rgba(228, 0, 43, 0.1) 100%);
            margin: 2rem 0;
        }

        /* Chart container styling */
        .chart-container {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            margin-bottom: 1rem;
            border: 1px solid rgba(228, 0, 43, 0.1);
        }

        /* KPI card styling */
        .kpi-card {
            background-color: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            margin-bottom: 1rem;
            border-top: 3px solid var(--carmila-red);
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Add page header
st.markdown("""
    <div class="page-header">
        <h1 style='color: #E4002B; margin-bottom: 0.5rem;'>Types de Commerce</h1>
        <p style='font-size: 1.2em; color: #666;'>Analysez la répartition et la performance des différents types de commerce</p>
    </div>
""", unsafe_allow_html=True)

# Définition des chemins
BASE_DIR = Path(__file__).parent.parent
DATASET_DIR = BASE_DIR / "datasets"

FILES = {
    "CA_Commercants": DATASET_DIR / "2.CA_Commercants_Mensuels_par_activité.xlsx"
}

@st.cache_data(show_spinner="Chargement des données...")
def load_data():
    if not DATASET_DIR.exists():
        st.error("🚨 Le dossier datasets n'existe pas !")
        st.stop()
        
    missing_files = [name for name, path in FILES.items() if not path.exists()]
    if missing_files:
        st.error(f"⚠️ Fichiers manquants : {', '.join(missing_files)}")
        st.stop()
        
    return pd.read_excel(FILES["CA_Commercants"])

# Chargement des données
df = load_data()

# ==============================
# 📌 2. Sélection de la Plage de Dates (Barre Latérale)
# ==============================
st.sidebar.header("🎯 Filtres")

df["Mois"] = pd.to_datetime(df["Mois"], format="%B %Y")
min_date, max_date = df["Mois"].min(), df["Mois"].max()
start_date, end_date = st.sidebar.date_input("📅 Sélectionnez la plage de dates", [min_date, max_date])

# 📌 Filtrage des données en fonction des dates sélectionnées
filtered_df = df[(df["Mois"] >= pd.Timestamp(start_date)) & (df["Mois"] <= pd.Timestamp(end_date))]

# 📌 Données de la période précédente pour comparer
previous_start = pd.Timestamp(start_date) - (pd.Timestamp(end_date) - pd.Timestamp(start_date))
previous_end = pd.Timestamp(start_date)
previous_period_df = df[(df["Mois"] >= previous_start) & (df["Mois"] < previous_end)]

# ==============================
# 📌 3. Calcul des KPIs Dynamiques avec Vérification
# ==============================

# 💰 CA Total et Variation
total_revenue = filtered_df["CA Mensuel TTC N"].sum()
previous_total_revenue = previous_period_df["CA Mensuel TTC N"].sum()

# 📌 Gestion du cas où il n'y a pas de données dans la période précédente
if previous_total_revenue != 0:
    ca_variation = ((total_revenue - previous_total_revenue) / previous_total_revenue) * 100
else:
    ca_variation = 0  # Évite une division par zéro

# 📌 CA Moyen par Famille de Magasin et Variation
if not filtered_df.empty:
    avg_revenue_per_family = filtered_df.groupby("Famille enseigne")["CA Mensuel TTC N"].mean().mean()
else:
    avg_revenue_per_family = 0

if not previous_period_df.empty:
    previous_avg_revenue_per_family = previous_period_df.groupby("Famille enseigne")["CA Mensuel TTC N"].mean().mean()
else:
    previous_avg_revenue_per_family = 0

# 📌 Gestion du cas où il n'y a pas de données dans la période précédente
if previous_avg_revenue_per_family != 0:
    ca_family_variation = ((avg_revenue_per_family - previous_avg_revenue_per_family) / previous_avg_revenue_per_family) * 100
else:
    ca_family_variation = 0

# 📌 Affichage des KPIs avec Vérification
st.title("📊 Analyse des Performances des Centres Commerciaux")

col1, col2 = st.columns(2)
col1.metric(label="💰 CA Total", value=f"{total_revenue:,.0f} €", delta=f"{ca_variation:.2f}%")
col2.metric(label="🏪 CA Moyen par Famille de Magasin", value=f"{avg_revenue_per_family:,.0f} €", delta=f"{ca_family_variation:.2f}%")

# ==============================
# 📌 4. Ajout des Filtres Dynamiques (Barre Latérale)
# ==============================
selected_malls = st.sidebar.multiselect(
    "🏬 Sélectionner un ou plusieurs centres commerciaux", 
    filtered_df["Nom ensemble immobilier"].unique(), 
    default=filtered_df["Nom ensemble immobilier"].unique()
)

selected_families = st.sidebar.multiselect(
    "🏬 Sélectionner une ou plusieurs familles d’enseignes", 
    filtered_df["Famille enseigne"].unique(), 
    default=filtered_df["Famille enseigne"].unique()
)

# 📌 Appliquer les filtres
filtered_df = filtered_df[
    (filtered_df["Nom ensemble immobilier"].isin(selected_malls)) &
    (filtered_df["Famille enseigne"].isin(selected_families))
]

# ==============================
# 📌 5. Graphiques Dynamiques avec Plotly
# ==============================
st.subheader("📊 Visualisations")

# 📊 1. Répartition des Catégories de Magasins
fig1 = px.bar(
    filtered_df.groupby(["Nom ensemble immobilier", "Famille enseigne"])["CA Mensuel TTC N"].mean().reset_index(),
    x="Nom ensemble immobilier",
    y="CA Mensuel TTC N",
    color="Famille enseigne",
    title="📊 Répartition des Catégories de Magasins",
    labels={"Nom ensemble immobilier": "Centre Commercial", "CA Mensuel TTC N": "CA Mensuel Moyen (€)"},
    template="plotly_dark",
    barmode="stack"
)
st.plotly_chart(fig1, use_container_width=True)

# 🏆 2. Meilleures Familles d’Enseignes
fig2 = px.bar(
    filtered_df.groupby("Famille enseigne")["CA Mensuel TTC N"].mean().reset_index().sort_values(by="CA Mensuel TTC N", ascending=False).head(10),
    x="Famille enseigne",
    y="CA Mensuel TTC N",
    title="🏆 Top 10 des Familles d’Enseignes les Plus Performantes",
    labels={"Famille enseigne": "Famille Enseigne", "CA Mensuel TTC N": "CA Mensuel Moyen (€)"},
    template="plotly_dark",
    text_auto=True
)
fig2.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig2, use_container_width=True)

# 📌 3. Meilleures Sous-Familles de Magasins
fig3 = px.bar(
    filtered_df.groupby("Sous-famille enseigne")["CA Mensuel TTC N"].mean().reset_index().sort_values(by="CA Mensuel TTC N", ascending=False),
    x="Sous-famille enseigne",
    y="CA Mensuel TTC N",
    title="📌 Sous-Familles de Magasins Générant le Plus de CA",
    labels={"Sous-famille enseigne": "Sous-Famille", "CA Mensuel TTC N": "CA Mensuel Moyen (€)"},
    template="plotly_dark",
    text_auto=True
)
st.plotly_chart(fig3, use_container_width=True)

# 💰 4. Relation entre CA Moyen et Surface Moyenne
ca_surface_par_famille = filtered_df.groupby("Famille enseigne").agg(
    {"CA Mensuel TTC N": "mean", "Superficie (m²)": "mean"}
).reset_index()
ca_surface_par_famille.rename(
    columns={"CA Mensuel TTC N": "CA Mensuel Moyen", "Superficie (m²)": "Surface Moyenne (m²)"}, inplace=True
)

fig4 = px.scatter(
    ca_surface_par_famille,
    x="Surface Moyenne (m²)",
    y="CA Mensuel Moyen",
    text="Famille enseigne",
    title="💰 Relation entre Surface Moyenne et CA Moyen par Famille d’Enseignes",
    labels={"Surface Moyenne (m²)": "Surface Moyenne (m²)", "CA Mensuel Moyen": "CA Mensuel Moyen (€)"},
    template="plotly_dark",
    size_max=50
)
st.plotly_chart(fig4, use_container_width=True)