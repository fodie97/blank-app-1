import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

# Configure the page - THIS MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Analyse des Flux",
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
    </style>
""", unsafe_allow_html=True)

# Add page header
st.markdown("""
    <div class="page-header">
        <h1 style='color: #E4002B; margin-bottom: 0.5rem;'>Analyse des Flux</h1>
        <p style='font-size: 1.2em; color: #666;'>Visualisez et analysez les tendances de fréquentation de vos centres commerciaux</p>
    </div>
""", unsafe_allow_html=True)

# Définition du chemin du dossier datasets
BASE_DIR = Path(__file__).parent.parent
DATASET_DIR = BASE_DIR / "datasets"

# Définition des fichiers attendus
FILES = {
    "Flux_Quotidien": DATASET_DIR / "Entr_es_Data_2023-2025.csv",
    "Temps_Visite": DATASET_DIR / "temps_visite_moyen.csv",
    "CA_Data": DATASET_DIR / "CA_per_entry_by_mall_and_month.csv"
}

# Vérification des fichiers manquants
if not DATASET_DIR.exists():
    st.error(" Le dossier datasets n'existe pas ! Vérifie ton arborescence de projet.")
    st.stop()

missing_files = [name for name, path in FILES.items() if not path.exists()]
if missing_files:
    st.error(f" Fichiers manquants : {', '.join(missing_files)}")
    st.stop()

@st.cache_data
def load_data():
    # Load flux data
    flux_df = pd.read_csv(FILES["Flux_Quotidien"])
    
    try:
        # Convert date and time
        flux_df['Jour'] = pd.to_datetime(flux_df['Jour'], format='%Y-%m-%d', errors='coerce')
        flux_df['heure'] = flux_df['heure'].str.split(' - ').str[0]
        flux_df['datetime'] = flux_df['Jour'] + pd.to_timedelta(flux_df['heure'].str.split(':').str[0].astype(int), unit='h')
        
        # Drop any rows with invalid dates
        flux_df = flux_df.dropna(subset=['Jour'])
        
        # Convert Site to category for better performance
        flux_df['Site'] = flux_df['Site'].astype('category')
        
        # Load temps_visite data
        temps_visite = pd.read_csv(FILES["Temps_Visite"])
        
        # Load CA data
        ca_data = pd.read_csv(FILES["CA_Data"])
        ca_data['Mois'] = pd.to_datetime(ca_data['Mois'])
        
        return {
            "flux_cc": flux_df,
            "temps_visite": temps_visite,
            "ca_data": ca_data
        }
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()

data = load_data()

# Vérifie si les données sont bien chargées
flux_cc = data["flux_cc"]
temps_visite = data["temps_visite"]
ca_data = data["ca_data"]

# Sidebar for granularity selection
with st.sidebar:
    st.write("## Options d'affichage")
    granularity = st.radio(
        "Choisir la granularité temporelle",
        ["Horaire", "Journalier", "Hebdomadaire", "Mensuel"],
        index=1  # Default to daily
    )

# Function to aggregate data based on granularity
def aggregate_data(df, gran):
    if gran == "Horaire":
        return df.groupby(['datetime', 'Site'])['Entrées'].sum().reset_index().rename(columns={'datetime': 'Jour'})
    elif gran == "Journalier":
        return df.groupby(['Jour', 'Site'])['Entrées'].sum().reset_index()
    elif gran == "Hebdomadaire":
        # Create week start date for each row
        df['WeekStart'] = df['Jour'].dt.to_period('W-MON').dt.start_time
        return df.groupby(['WeekStart', 'Site'])['Entrées'].sum().reset_index().rename(columns={'WeekStart': 'Jour'})
    else:  # Monthly
        df['MonthStart'] = df['Jour'].dt.to_period('M').dt.start_time
        return df.groupby(['MonthStart', 'Site'])['Entrées'].sum().reset_index().rename(columns={'MonthStart': 'Jour'})

# Aggregate data based on selected granularity
flux_cc_agg = aggregate_data(flux_cc, granularity)

# Liste des centres commerciaux
unique_malls = sorted(flux_cc_agg["Site"].unique())

# UI pour la sélection des filtres
st.title("📊 Visite des centres commerciaux")

# Sélection de la plage de dates
if granularity == "Horaire":
    min_date = flux_cc["datetime"].min()
    max_date = flux_cc["datetime"].max()
else:
    min_date = flux_cc["Jour"].min()
    max_date = flux_cc["Jour"].max()

start_date, end_date = st.date_input("📅 Sélectionnez la plage de dates", [min_date, max_date])

# Sélection des centres commerciaux
selected_malls = st.multiselect("🏬 Sélectionnez un ou plusieurs centres commerciaux", unique_malls, default=unique_malls[:1])

# Filtrage des données en fonction des choix utilisateur
filtered_flux = flux_cc_agg[
    (flux_cc_agg["Jour"].dt.date >= start_date) &
    (flux_cc_agg["Jour"].dt.date <= end_date) &
    (flux_cc_agg["Site"].isin(selected_malls))
]

# Calcul du KPI total sur la plage sélectionnée
total_flux = filtered_flux["Entrées"].sum()

# Calcul de la variation avec la période précédente
if granularity == "Horaire":
    previous_start = pd.Timestamp(start_date) - pd.Timedelta(hours=24)
    previous_end = pd.Timestamp(start_date)
elif granularity == "Journalier":
    date_diff = (end_date - start_date).days
    previous_start = pd.Timestamp(start_date) - pd.Timedelta(days=date_diff)
    previous_end = pd.Timestamp(start_date) - pd.Timedelta(days=1)
elif granularity == "Hebdomadaire":
    previous_start = pd.Timestamp(start_date) - pd.Timedelta(weeks=1)
    previous_end = pd.Timestamp(start_date)
else:  # Mensuel
    previous_start = pd.Timestamp(start_date) - pd.Timedelta(days=30)
    previous_end = pd.Timestamp(start_date)

previous_flux = flux_cc_agg[
    (flux_cc_agg["Jour"].dt.date >= previous_start.date()) &
    (flux_cc_agg["Jour"].dt.date <= previous_end.date()) &
    (flux_cc_agg["Site"].isin(selected_malls))
]["Entrées"].sum()

# Calcul du KPI total sur la plage sélectionnée
flux_variance = ((total_flux - previous_flux) / previous_flux * 100) if previous_flux != 0 else 0

# Transformation du dataset de temps de visite
temps_visite_long = temps_visite.melt(id_vars=["ID Mall", "Nom Centre"], var_name="Mois", value_name="Temps moyen de visite (min)")

# Correction des noms de mois pour datetime
mois_mapping = {
    "Janvier": "January", "Février": "February", "Mars": "March", "Avril": "April",
    "Mai": "May", "Juin": "June", "Juillet": "July", "Août": "August",
    "Septembre": "September", "Octobre": "October", "Novembre": "November", "Décembre": "December"
}
temps_visite_long["Mois"] = temps_visite_long["Mois"].replace(mois_mapping, regex=True)
temps_visite_long["Mois"] = pd.to_datetime(temps_visite_long["Mois"], format="%B %Y")

# Filtrage des données pour le temps de visite moyen
filtered_temps_visite = temps_visite_long[
    (temps_visite_long["Mois"] >= pd.Timestamp(start_date)) &
    (temps_visite_long["Mois"] <= pd.Timestamp(end_date)) &
    (temps_visite_long["Nom Centre"].isin(selected_malls))
]

# KPI Temps Moyen de Visite
current_avg_time = filtered_temps_visite["Temps moyen de visite (min)"].mean()
previous_avg_time = temps_visite_long[
    (temps_visite_long["Mois"] < pd.Timestamp(start_date)) &
    (temps_visite_long["Nom Centre"].isin(selected_malls))
]["Temps moyen de visite (min)"].mean()

# Calcul de la variation du temps moyen de visite
time_variance = ((current_avg_time - previous_avg_time) / previous_avg_time * 100) if previous_avg_time != 0 else 0

# Load event data
@st.cache_data
def load_event_data():
    events_file = "datasets/final_impact_evenements.csv"
    events_df = pd.read_csv(events_file)
    
    # Filter only positive impacts and calculate average impact per event
    positive_events = events_df[events_df['Impact'] > 0].copy()
    avg_impact = positive_events.groupby('Exceptionnel')['Impact'].mean().reset_index()
    avg_impact = avg_impact.sort_values('Impact', ascending=False)
    
    return avg_impact

# Load event data
event_data = load_event_data()

# After the granularity selector but before the graph
event_container = st.container()

with event_container:
    st.markdown("---")
    st.subheader("🎉 Simulation d'événements")

    # Initialize session state for events if it doesn't exist
    if 'planned_events' not in st.session_state:
        st.session_state.planned_events = []
    if 'show_error' not in st.session_state:
        st.session_state.show_error = False

    # Add "No event" option
    event_options = ['Aucun événement'] + event_data['Exceptionnel'].tolist()

    # Create columns for event selection and date
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        selected_event = st.selectbox(
            "Sélectionnez un événement à simuler",
            options=event_options,
            format_func=lambda x: x if x == 'Aucun événement' else f"{x} (Impact moyen: +{event_data[event_data['Exceptionnel'] == x]['Impact'].values[0]:.1f}%)",
            key="event_selector"
        )

    with col2:
        event_date = st.date_input(
            "Choisissez la date de l'événement (2025 uniquement)",
            min_value=pd.Timestamp('2025-01-01').date(),
            max_value=pd.Timestamp('2025-12-31').date(),
            value=pd.Timestamp('2025-01-01').date(),
            disabled=(selected_event == 'Aucun événement'),
            key="event_date"
        )

    def add_event():
        if selected_event != 'Aucun événement':
            impact = event_data[event_data['Exceptionnel'] == selected_event]['Impact'].values[0]
            # Calculate the end of the week for the event date
            event_date_ts = pd.Timestamp(event_date)
            end_of_week = event_date_ts + pd.Timedelta(days=(6 - event_date_ts.dayofweek))
            
            new_event = {
                'event': selected_event,
                'mall': selected_malls[0],  # Use the first selected mall
                'start_date': event_date,
                'end_date': end_of_week.date(),
                'impact': impact
            }
            # Check if event already exists on the same date
            date_exists = any(e['start_date'] == event_date for e in st.session_state.planned_events)
            if not date_exists:
                st.session_state.planned_events.append(new_event)
                st.session_state.show_error = False
            else:
                st.session_state.show_error = True

    with col3:
        if st.button("Ajouter", disabled=(selected_event == 'Aucun événement'), on_click=add_event):
            pass

    if st.session_state.show_error:
        st.error("Un événement existe déjà à cette date")

    # Show planned events
    if st.session_state.planned_events:
        st.markdown("### Événements planifiés")
        for idx, event in enumerate(st.session_state.planned_events):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{event['event']}** le {event['start_date']} (Impact: +{event['impact']:.1f}%)")
            with col2:
                def delete_event(index):
                    st.session_state.planned_events.pop(index)
                
                if st.button("Supprimer", key=f"delete_{idx}", on_click=delete_event, args=(idx,)):
                    pass

# Create a copy of the filtered data for simulation
simulated_data = filtered_flux.copy()

# Apply the impact of all planned events
for event in st.session_state.planned_events:
    # Calculate the end of the week for the event date
    event_date_ts = pd.Timestamp(event['start_date'])
    end_of_week = event_date_ts + pd.Timedelta(days=(6 - event_date_ts.dayofweek))
    
    # Apply impact from event date to end of the week
    mask = (simulated_data['Jour'].dt.date >= event['start_date']) & \
           (simulated_data['Jour'].dt.date <= event['end_date']) & \
           (simulated_data['Site'] == event['mall'])
    simulated_data.loc[mask, 'Entrées'] = simulated_data.loc[mask, 'Entrées'] * (1 + event['impact']/100)

# Function to calculate CA
def calculate_ca(entries_df, ca_per_entry_df):
    try:
        entries_df = entries_df.copy()
        
        # Use a fixed CA per entry (average from the data)
        ca_per_entry = 0.6  # Average CA per entry in euros
        
        # Calculate CA directly from entries
        entries_df['CA'] = entries_df['Entrées'] * ca_per_entry
        
        return entries_df
    except Exception as e:
        st.error(f"Erreur lors du calcul du CA : {str(e)}")
        return entries_df.assign(CA=0)

# Add CA box under the graph
def display_ca_box():
    # Calculate base CA (without events)
    base_ca = calculate_ca(filtered_flux, ca_data)
    base_total = base_ca['CA'].sum()
    
    # Calculate CA with events impact
    event_impact_total = 0
    if st.session_state.planned_events:
        for event in st.session_state.planned_events:
            event_mask = (
                (base_ca['Jour'].dt.date >= event['start_date']) &
                (base_ca['Jour'].dt.date <= event['end_date']) &
                (base_ca['Site'] == event['mall'])
            )
            
            # Calculate additional CA from the event
            affected_entries = base_ca[event_mask]
            event_impact = (affected_entries['CA'] * (event['impact']/100)).sum()
            event_impact_total += event_impact
    
    # Total CA with events is base CA plus the impact
    total_with_events = base_total + event_impact_total
    
    # Format numbers
    base_formatted = f"{base_total:,.2f} €"
    total_formatted = f"{total_with_events:,.2f} €"
    
    # Create the box with the information
    st.markdown("""
    <div class="metric-container">
        <div style="display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 20px; text-align: center;">
            <div>
                <div style="font-size: 16px; margin-bottom: 8px;">CA Base</div>
                <div style="font-size: 20px; font-weight: bold;">{}</div>
            </div>
            <div style="color: #28a745; font-size: 24px;">➜</div>
            <div>
                <div style="font-size: 16px; margin-bottom: 8px;">CA avec Événements</div>
                <div style="font-size: 20px; font-weight: bold;">{}</div>
            </div>
        </div>
    </div>
    """.format(base_formatted, total_formatted), unsafe_allow_html=True)

# Function to plot the flux data
def plot_flux(df, simulated_df, gran, events=None):
    if df.empty:
        st.warning("Aucune donnée à afficher pour la sélection actuelle.")
        return None
        
    fig = go.Figure()
    
    # Color palette for better visibility
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    prediction_date = pd.Timestamp('2025-01-01')
    
    for idx, site in enumerate(df["Site"].unique()):
        site_data = df[df["Site"] == site]
        simulated_site_data = simulated_df[simulated_df["Site"] == site]
        
        # Split data into historical and predicted
        historical_data = site_data[site_data["Jour"] < prediction_date]
        predicted_data = simulated_site_data[simulated_site_data["Jour"] >= prediction_date]
        
        # Plot historical data with solid line
        if not historical_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=historical_data["Jour"],
                    y=historical_data["Entrées"],
                    name=f"{site} (historique)",
                    mode="lines",
                    line=dict(
                        color=colors[idx % len(colors)],
                        width=2
                    ),
                    hovertemplate="<b>%{x}</b><br>" +
                                "Entrées: %{y:,.0f}<br>" +
                                f"Site: {site}<extra></extra>"
                )
            )
        
        # Plot predicted data
        if not predicted_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=predicted_data["Jour"],
                    y=predicted_data["Entrées"],
                    name=f"{site} (prévision)",
                    mode="lines",
                    line=dict(
                        color=colors[idx % len(colors)],
                        width=2,
                        dash='dot'
                    ),
                    hovertemplate="<b>%{x}</b><br>" +
                                "Entrées (prévision): %{y:,.0f}<br>" +
                                f"Site: {site}<extra></extra>"
                )
            )
            
            # Add markers for each event's impact
            if events:
                for event in events:
                    event_date_ts = pd.Timestamp(event['start_date'])
                    end_of_week = event_date_ts + pd.Timedelta(days=(6 - event_date_ts.dayofweek))
                    
                    impacted_data = predicted_data[
                        (predicted_data["Jour"].dt.date >= event['start_date']) & 
                        (predicted_data["Jour"].dt.date <= event['end_date'])
                    ]
                    
                    if not impacted_data.empty:
                        fig.add_trace(
                            go.Scatter(
                                x=impacted_data["Jour"],
                                y=impacted_data["Entrées"],
                                name=f"{site} ({event['event']})",
                                mode="markers",
                                marker=dict(
                                    symbol='circle',
                                    size=8,
                                    color='red',
                                    line=dict(width=1, color='darkred')
                                ),
                                hovertemplate="<b>%{x}</b><br>" +
                                            "Entrées (avec impact): %{y:,.0f}<br>" +
                                            f"Site: {site}<br>" +
                                            f"Événement: {event['event']}<br>" +
                                            f"Impact: +{event['impact']:.1f}%<extra></extra>"
                            )
                        )

    title_prefix = {
        "Horaire": "par heure",
        "Journalier": "par jour",
        "Hebdomadaire": "par semaine",
        "Mensuel": "par mois"
    }
    
    fig.update_layout(
        title={
            'text': f"Évolution du Flux de Visiteurs ({title_prefix[gran]})",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },
        xaxis_title="Date",
        yaxis_title="Nombre d'entrées",
        height=700,
        template="plotly_white",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.05,
            bgcolor="rgba(255, 255, 255, 0.8)"
        ),
        margin=dict(l=50, r=50, t=80, b=50),
        hovermode='x unified',
        uirevision="true",
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray',
            showline=True,
            linewidth=2,
            linecolor='Black'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray',
            showline=True,
            linewidth=2,
            linecolor='Black',
            tickformat=",d"
        )
    )
    
    # Add vertical lines and annotations
    shapes = [
        dict(
            type='line',
            x0=prediction_date,
            x1=prediction_date,
            y0=0,
            y1=1,
            yref='paper',
            line=dict(
                color='gray',
                width=2,
                dash='dash'
            )
        )
    ]
    
    annotations = [
        dict(
            x=prediction_date,
            y=1,
            yref='paper',
            text="Début des prévisions",
            showarrow=False,
            textangle=-90,
            yshift=0,
            font=dict(size=12)
        )
    ]
    
    # Add event annotation if selected
    if events:
        for event in events:
            annotations.append(
                dict(
                    x=event['start_date'],
                    y=1,
                    yref='paper',
                    text=f" {event['event']} (+{event['impact']:.1f}%)",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor='red',
                    ax=0,
                    ay=-40
                )
            )
    
    fig.update_layout(shapes=shapes, annotations=annotations)
    fig.update_xaxes(rangeslider_visible=True)
    
    return fig

# Show the plot
fig = plot_flux(filtered_flux, simulated_data, granularity, events=st.session_state.planned_events)
st.plotly_chart(fig, use_container_width=True, config={
    'displayModeBar': True,
    'displaylogo': False
})

# Display the CA box
display_ca_box()

# Show impact summary if an event is selected
if st.session_state.planned_events:
    st.info(f"""
    **Impact simulé des événements**
    """)

# Affichage des KPIs
st.metric(
    label="Total Flux",
    value=f"{total_flux:,.0f}",
    delta=f"{flux_variance:.1f}%"
)

st.metric(
    label="Temps Moyen de Visite (min)",
    value=f"{current_avg_time:.1f}" if not pd.isna(current_avg_time) else "N/A",
    delta=f"{time_variance:.1f}%" if not pd.isna(time_variance) else None
)