import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# 📌 Définition du chemin du dossier datasets
BASE_DIR = Path(__file__).parent.parent  # Remonte d'un niveau pour accéder au dossier parent
DATASET_DIR = BASE_DIR / "datasets"  # Vérifie l'existence du dossier

# 📌 Définition des fichiers attendus
FILES = {
    "CA_Commercants": DATASET_DIR / "2.CA_Commercants_Mensuels_par_activité.xlsx",
    "Surfaces_CC": DATASET_DIR / "3.Surfaces_CC.xlsx"
}

# ✅ Vérification et affichage des fichiers trouvés
if DATASET_DIR.exists():
    found_files = [f.name for f in DATASET_DIR.iterdir()]
    st.write("📂 Fichiers trouvés :", found_files)
else:
    st.error("🚨 Le dossier datasets n'existe pas ! Vérifie ton arborescence de projet.")
    st.stop()

# ✅ Vérification des fichiers manquants
missing_files = [name for name, path in FILES.items() if not path.exists()]
if missing_files:
    st.error(f"⚠️ Fichiers manquants : {', '.join(missing_files)}")
    st.stop()

# ✅ Chargement des fichiers avec cache Streamlit
@st.cache_data
def load_data():
    return {
        "ca_commercants": pd.read_excel(FILES["CA_Commercants"]),
        "surfaces_cc": pd.read_excel(FILES["Surfaces_CC"])
    }

data = load_data()

# ✅ Vérifie si les données sont bien chargées
ca_commercants = data["ca_commercants"]
surfaces_cc = data["surfaces_cc"]

# 📌 Conversion des colonnes pertinentes en int
columns_to_convert = [
    "GLA centre (hyper + galerie+ mail) GI",
    "GLA boutiques (hors mail - GI)",
    "Nombre places de parking (Assetbook)",
    "Nombre de boutiques (hors hyper)",
    "ALIMENTATION", "EQ DE LA PERSONNE", "EQ DE LA MAISON", "LOISIRS",
    "RESTAURATION", "SERVICES", "DIVERS"
]
for col in columns_to_convert:
    if col in surfaces_cc.columns:
        surfaces_cc[col] = surfaces_cc[col].fillna(0).astype(int)

# 📌 Sélection des centres commerciaux
unique_malls = sorted(ca_commercants["Nom ensemble immobilier"].unique())
selected_malls = st.multiselect("🏬 Sélectionnez un ou plusieurs centres commerciaux", unique_malls, default=unique_malls)

# 📆 Sélection de la plage de dates
ca_commercants["Mois"] = pd.to_datetime(ca_commercants["Mois"], format="%B %Y")
min_date, max_date = ca_commercants["Mois"].min(), ca_commercants["Mois"].max()
start_date, end_date = st.date_input("📅 Sélectionnez la plage de dates", [min_date, max_date])

# 📌 Filtrage des données
filtered_data = ca_commercants[
    (ca_commercants["Mois"] >= pd.Timestamp(start_date)) &
    (ca_commercants["Mois"] <= pd.Timestamp(end_date)) &
    (ca_commercants["Nom ensemble immobilier"].isin(selected_malls))
]

# ✅ Calcul du KPI
total_ca = filtered_data["CA Mensuel TTC N"].sum()
previous_period_data = ca_commercants[
    (ca_commercants["Mois"] >= pd.Timestamp(start_date) - (pd.Timestamp(end_date) - pd.Timestamp(start_date))) &
    (ca_commercants["Mois"] < pd.Timestamp(start_date)) &
    (ca_commercants["Nom ensemble immobilier"].isin(selected_malls))
]
previous_total_ca = previous_period_data["CA Mensuel TTC N"].sum()
variance = ((total_ca - previous_total_ca) / previous_total_ca) * 100 if previous_total_ca != 0 else 0

# 📌 Affichage du KPI
st.metric(label="💰 Chiffre d'Affaires Total et Variation vs Période Précédente", value=f"{total_ca:,.0f}€", delta=f"{variance:.2f}%")

# 📊 Comparaison des performances commerciales
performance_cc = filtered_data.groupby("Nom ensemble immobilier")["CA Mensuel TTC N"].mean().reset_index()
moyenne_globale = ca_commercants["CA Mensuel TTC N"].mean()

fig1 = px.bar(
    performance_cc, x="Nom ensemble immobilier", y="CA Mensuel TTC N", 
    title="📊 Comparaison des Performances Commerciales par Centre",
    labels={"Nom ensemble immobilier": "Centre Commercial", "CA Mensuel TTC N": "CA Mensuel Moyen (€)"},
    template="plotly_dark"
)
st.plotly_chart(fig1, use_container_width=True)

# 📊 🔄 **Ancienne Méthode : Évolution des ventes mensuelles**
monthly_sales = ca_commercants.groupby(['Nom ensemble immobilier', 'Mois'])['CA Mensuel TTC N'].mean().reset_index()

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

# 📊 Performances des familles d'enseignes
performance_familles = filtered_data.groupby(["Nom ensemble immobilier", "Famille enseigne"])["CA Mensuel TTC N"].mean().reset_index()
fig3 = px.bar(
    performance_familles, x="Nom ensemble immobilier", y="CA Mensuel TTC N", color="Famille enseigne", 
    title="🏢 Performances des Familles d’Enseignes par Centre",
    labels={"Nom ensemble immobilier": "Centre Commercial", "CA Mensuel TTC N": "CA Mensuel Moyen (€)"},
    template="plotly_dark", barmode="group"
)
st.plotly_chart(fig3, use_container_width=True)

# ✅ **Calcul et affichage du CA par m²**
if "CA Mensuel TTC N" in ca_commercants.columns and "Superficie (m²)" in ca_commercants.columns:
    ca_commercants["CA par m²"] = ca_commercants["CA Mensuel TTC N"] / ca_commercants["Superficie (m²)"]
    ca_commercants["CA par m²"].replace([float('inf'), -float('inf')], 0, inplace=True)
    ca_commercants["CA par m²"].fillna(0, inplace=True)

    ca_per_m2_mall = ca_commercants.groupby(["Nom ensemble immobilier", "Famille enseigne"])["CA par m²"].mean().reset_index()

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
else:
    st.error("⚠️ Les colonnes nécessaires au calcul du CA par m² ne sont pas disponibles.")
