import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

# Configure the page
st.set_page_config(
    page_title="Performance des Centres",
    layout="wide"
)

st.title("💰 Performance des Centres")
st.write("Page en construction...")

# Définition des chemins
BASE_DIR = Path(__file__).parent.parent
DATASET_DIR = BASE_DIR / "datasets"

FILES = {
    "CA_Commercants": DATASET_DIR / "2.CA_Commercants_Mensuels_par_activité.xlsx",
    "Surfaces_CC": DATASET_DIR / "3.Surfaces_CC.xlsx"
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
        
    return {
        "ca_commercants": pd.read_excel(FILES["CA_Commercants"]),
        "surfaces_cc": pd.read_excel(FILES["Surfaces_CC"])
    }

# Chargement des données
data = load_data()
ca_commercants = data["ca_commercants"]
surfaces_cc = data["surfaces_cc"]

# ==============================
# 📌 2. Ajout des KPIs dynamiques
# ==============================
st.title("📊 Analyse des Centres Commerciaux")

# 📆 Sélection de la plage de dates
ca_commercants["Mois"] = pd.to_datetime(ca_commercants["Mois"], format="%B %Y")
min_date, max_date = ca_commercants["Mois"].min(), ca_commercants["Mois"].max()
start_date, end_date = st.sidebar.date_input("📅 Sélectionnez la plage de dates", [min_date, max_date])

# Filtrage des données sur la période sélectionnée
filtered_data = ca_commercants[
    (ca_commercants["Mois"] >= pd.Timestamp(start_date)) &
    (ca_commercants["Mois"] <= pd.Timestamp(end_date))
]

# 📌 Calcul des KPIs dynamiques
total_revenue = filtered_data["CA Mensuel TTC N"].sum()
avg_revenue_per_center = filtered_data.groupby("Nom ensemble immobilier")["CA Mensuel TTC N"].mean().mean()
total_malls = filtered_data["Nom ensemble immobilier"].nunique()

# 📌 Comparaison avec la période précédente
previous_period_data = ca_commercants[
    (ca_commercants["Mois"] >= pd.Timestamp(start_date) - (pd.Timestamp(end_date) - pd.Timestamp(start_date))) &
    (ca_commercants["Mois"] < pd.Timestamp(start_date))
]

previous_total_revenue = previous_period_data["CA Mensuel TTC N"].sum() if not previous_period_data.empty else 0
previous_avg_revenue_per_center = previous_period_data.groupby("Nom ensemble immobilier")["CA Mensuel TTC N"].mean().mean() if not previous_period_data.empty else 0

# ✅ Gestion des valeurs NaN et division par zéro
ca_variation = ((total_revenue - previous_total_revenue) / previous_total_revenue * 100) if previous_total_revenue != 0 else 0
avg_revenue_variation = ((avg_revenue_per_center - previous_avg_revenue_per_center) / previous_avg_revenue_per_center * 100) if previous_avg_revenue_per_center != 0 else 0

# 📌 Affichage des KPIs
col1, col2 = st.columns(2)
col1.metric(label="💰 CA Total", value=f"{total_revenue:,.0f} €", delta=f"{ca_variation:.2f}%")
col2.metric(label="🏪 CA moyen par centre", value=f"{avg_revenue_per_center:,.0f} €", delta=f"{avg_revenue_variation:.2f}%")

# ==============================
# 📌 3. Ajout des filtres dynamiques améliorés
# ==============================
st.sidebar.header("🎯 Filtres")

selected_malls = st.sidebar.multiselect(
    "🏬 Sélectionner un ou plusieurs centres commerciaux", 
    filtered_data["Nom ensemble immobilier"].unique(), 
    default=filtered_data["Nom ensemble immobilier"].unique()
)

selected_families = st.sidebar.multiselect(
    "🏬 Sélectionner une ou plusieurs familles d’enseignes", 
    filtered_data["Famille enseigne"].unique(), 
    default=filtered_data["Famille enseigne"].unique()
)

# Appliquer les filtres sélectionnés
filtered_data = filtered_data[
    (filtered_data["Nom ensemble immobilier"].isin(selected_malls)) &
    (filtered_data["Famille enseigne"].isin(selected_families))
]

# ==============================
# 📌 4. Graphiques dynamiques avec Plotly
# ==============================
st.subheader("📊 Visualisations")

with st.container():
    # 📊 1. Performance des Centres Commerciaux
    fig1 = px.bar(
        filtered_data.groupby("Nom ensemble immobilier")["CA Mensuel TTC N"].mean().reset_index(),
        x="Nom ensemble immobilier",
        y="CA Mensuel TTC N",
        title="🏬 Performance des Centres Commerciaux",
        labels={"Nom ensemble immobilier": "Centre Commercial", "CA Mensuel TTC N": "CA Mensuel Moyen (€)"},
        template="plotly_dark",
        text_auto=True
    )
    st.plotly_chart(fig1, use_container_width=True)

    # 📊 2. Évolution des ventes mensuelles
    monthly_sales = filtered_data.groupby(['Nom ensemble immobilier', 'Mois'])['CA Mensuel TTC N'].mean().reset_index()
    fig2 = px.line(
        monthly_sales,
        x="Mois",
        y="CA Mensuel TTC N",
        color="Nom ensemble immobilier",
        title="📈 Évolution des Ventes Mensuelles par Centre",
        labels={'Mois': 'Date', 'CA Mensuel TTC N': 'CA Mensuel Moyen'},
        template="plotly_dark",
        markers=True
    )
    st.plotly_chart(fig2, use_container_width=True)

    # 📊 3. Performances des familles d'enseignes
    performance_familles = filtered_data.groupby(["Nom ensemble immobilier", "Famille enseigne"])["CA Mensuel TTC N"].mean().reset_index()
    fig3 = px.bar(
        performance_familles, 
        x="Nom ensemble immobilier", 
        y="CA Mensuel TTC N", 
        color="Famille enseigne", 
        title="🏢 Performances des Familles d’Enseignes par Centre",
        labels={"Nom ensemble immobilier": "Centre Commercial", "CA Mensuel TTC N": "CA Mensuel Moyen (€)"},
        template="plotly_dark", 
        barmode="group"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ✅ 4. Chiffre d'Affaires par M²
    if "CA Mensuel TTC N" in filtered_data.columns and "Superficie (m²)" in filtered_data.columns:
        filtered_data["CA par m²"] = filtered_data["CA Mensuel TTC N"] / filtered_data["Superficie (m²)"]
        filtered_data["CA par m²"].replace([float('inf'), -float('inf')], 0, inplace=True)
        filtered_data["CA par m²"].fillna(0, inplace=True)

        ca_per_m2_mall = filtered_data.groupby(["Nom ensemble immobilier", "Famille enseigne"])["CA par m²"].mean().reset_index()
        fig4 = px.bar(
            ca_per_m2_mall,
            x="Nom ensemble immobilier",
            y="CA par m²",
            color="Famille enseigne",
            title="🏆 Chiffre d'Affaires par Mètre Carré par Mall et Catégorie",
            labels={"Nom ensemble immobilier": "Centre Commercial", "CA par m²": "CA par m² (€)"},
            barmode="group",
            template="plotly_dark",
            text_auto=True
        )
        st.plotly_chart(fig4, use_container_width=True)