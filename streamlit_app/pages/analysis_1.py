from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# 📌 Définition du chemin du dossier datasets
BASE_DIR = Path(__file__).parent.parent  # Remonte d'un niveau pour accéder au dossier parent
DATASET_DIR = BASE_DIR / "datasets"  # Assure-toi que ce dossier existe

# 📌 Définition des fichiers attendus
FILES = {
    "Flux_Quotidien": DATASET_DIR / "1.Flux_CC_Quotidien_heure_par_heure.xlsx",
    "Temps_Visite": DATASET_DIR / "temps_visite_moyen.csv"  # Mets ici le bon fichier
}

# ✅ Vérification et affichage des fichiers trouvés dans le dossier datasets
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

# ✅ Chargement des fichiers
@st.cache_data
def load_data():
    return {
        "flux_cc": pd.read_excel(FILES["Flux_Quotidien"]),
        "temps_visite": pd.read_csv(FILES["Temps_Visite"])
    }

data = load_data()

# ✅ Vérifie si les données sont bien chargées
flux_cc = data["flux_cc"]
temps_visite = data["temps_visite"]

# 📌 Transformation des dates
flux_cc["Jour"] = pd.to_datetime(flux_cc["Jour"])

# 📌 Transformation du dataset de temps de visite
temps_visite_long = temps_visite.melt(id_vars=["ID Mall", "Nom Centre"], var_name="Mois", value_name="Temps moyen de visite (min)")

# 📆 Correction des noms de mois pour datetime
mois_mapping = {
    "Janvier": "January", "Février": "February", "Mars": "March", "Avril": "April",
    "Mai": "May", "Juin": "June", "Juillet": "July", "Août": "August",
    "Septembre": "September", "Octobre": "October", "Novembre": "November", "Décembre": "December"
}
temps_visite_long["Mois"] = temps_visite_long["Mois"].replace(mois_mapping, regex=True)
temps_visite_long["Mois"] = pd.to_datetime(temps_visite_long["Mois"], format="%B %Y")

# 📌 Liste des centres commerciaux
unique_malls = sorted(flux_cc["Site"].unique())

# 📌 UI pour la sélection des filtres
st.title("📊 Visite des centres commerciaux")

# 📆 Sélection de la plage de dates
min_date = flux_cc["Jour"].min()
max_date = flux_cc["Jour"].max()
start_date, end_date = st.date_input("📅 Sélectionnez la plage de dates", [min_date, max_date])

# 🏢 Sélection des centres commerciaux
selected_malls = st.multiselect("🏬 Sélectionnez un ou plusieurs centres commerciaux", unique_malls, default=unique_malls)

# 📌 Filtrage des données en fonction des choix utilisateur
filtered_flux = flux_cc[
    (flux_cc["Jour"] >= pd.Timestamp(start_date)) &
    (flux_cc["Jour"] <= pd.Timestamp(end_date)) &
    (flux_cc["Site"].isin(selected_malls))
]

# 📌 Filtrage des données pour le temps de visite moyen
filtered_temps_visite = temps_visite_long[
    (temps_visite_long["Mois"] >= pd.Timestamp(start_date)) &
    (temps_visite_long["Mois"] <= pd.Timestamp(end_date)) &
    (temps_visite_long["Nom Centre"].isin(selected_malls))
]

# ✅ Calcul du KPI total sur la plage sélectionnée
total_flux = filtered_flux["Entrées"].sum()

# ✅ Calcul de la variation avec la période précédente
previous_period_flux = flux_cc[
    (flux_cc["Jour"] >= pd.Timestamp(start_date) - (pd.Timestamp(end_date) - pd.Timestamp(start_date))) &
    (flux_cc["Jour"] < pd.Timestamp(start_date)) &
    (flux_cc["Site"].isin(selected_malls))
]["Entrées"].sum()

# 📌 Calcul de la variation du flux
flux_variance = ((total_flux - previous_period_flux) / previous_period_flux) * 100 if previous_period_flux != 0 else 0

# 📌 KPI Temps Moyen de Visite
current_avg_time = filtered_temps_visite["Temps moyen de visite (min)"].mean()
previous_avg_time = temps_visite_long[
    (temps_visite_long["Mois"] < pd.Timestamp(start_date)) &
    (temps_visite_long["Nom Centre"].isin(selected_malls))
]["Temps moyen de visite (min)"].mean()

# 📌 Calcul de la variation du temps moyen de visite
time_variance = ((current_avg_time - previous_avg_time) / previous_avg_time) * 100 if previous_avg_time != 0 else 0

# 📌 Affichage des KPIs
st.metric(label="📊 Total Flux et Variation vs Période Précédente", value=f"{total_flux:,.0f}", delta=f"{flux_variance:.2f}%")
st.metric(label="⏳ Temps Moyen de Visite (min)", value=f"{current_avg_time:.1f}" if not pd.isna(current_avg_time) else "0", delta=f"{time_variance:.2f}%" if not pd.isna(time_variance) else "0%")

# 📊 Création du graphique
def plot_flux(df):
    fig = go.Figure()

    for mall in selected_malls:
        df_mall = df[df["Site"] == mall]
        df_grouped = df_mall.groupby("Jour")["Entrées"].sum().reset_index()

        fig.add_trace(go.Scatter(
            x=df_grouped["Jour"],
            y=df_grouped["Entrées"],
            mode="lines+markers",
            name=mall,
            hovertemplate="Date: %{x}<br>Entrées: %{y}<extra></extra>"
        ))

    fig.update_layout(
        title="📈 Évolution des flux par jour et par centre commercial",
        xaxis_title="Date",
        yaxis_title="Nombre d'Entrées",
        xaxis=dict(rangeslider=dict(visible=True), type="date"),
        hovermode="x unified",
        template="plotly_dark"
    )
    return fig

# 📌 Affichage du graphique
st.plotly_chart(plot_flux(filtered_flux), use_container_width=True)