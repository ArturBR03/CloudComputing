import streamlit as st
import pandas as pd
import plotly.express as px
from helper_functions import write_gdp_csv


try:
    df = pd.read_csv("world_data.csv")
except FileNotFoundError:
    st.error("CSV-Datei wurde nicht gefunden.")
    st.stop()

# Daten bereinigen
df = df.dropna(subset=["country", "year", "gdp"]).sort_values("year")
df["year"] = df["year"].astype(int)

# Sidebar für Filter
with st.sidebar:
    st.title("BIP Visualisierung – Erweiterte Version")
    
    countries = sorted(df["country"].unique())
    selected_country = st.selectbox("Land wählen", countries)

    min_year = df["year"].min()
    max_year = df["year"].max()
    selected_years = st.slider(
        "Zeitraum wählen",
        min_value=min_year,
        max_value=max_year,
        value=(max_year - 10, max_year),
    )


    plot_type = st.radio("Diagrammtyp", ["Linie", "Balken", "Punkte"])

    color_choice = st.color_picker("Diagrammfarbe wählen", "#1f77b4")

# Daten filtern
filtered_df = df[
    (df["country"] == selected_country)
    & (df["year"].between(selected_years[0], selected_years[1]))
].sort_values("year")

# Titel
st.title(f"BIP-Analyse: {selected_country}")
st.subheader(f"Zeitraum: {selected_years[0]} - {selected_years[1]}")

if not filtered_df.empty:
    latest = filtered_df.iloc[-1]
    delta = (
        f"{(latest['gdp'] - filtered_df.iloc[-2]['gdp'])/1e9:+.1f} Mrd USD"
        if len(filtered_df) > 1 else "N/A"
    )

    st.metric(
        label=f"Letztes verfügbares BIP ({latest['year']})",
        value=f"{latest['gdp']/1e12:,.2f} Bio USD",
        delta=delta,
    )

    # Durchschnittswert
    avg_gdp = filtered_df["gdp"].mean()
    st.info(f"Durchschnittliches BIP im gewählten Zeitraum: {avg_gdp/1e12:.2f} Bio USD")

    # Diagramm
    if plot_type == "Linie":
        fig = px.line(
            filtered_df, x="year", y="gdp",
            title="BIP Entwicklung",
            template="plotly_dark",
            markers=True
        )
        fig.update_traces(line=dict(color=color_choice))

    elif plot_type == "Balken":
        fig = px.bar(
            filtered_df, x="year", y="gdp",
            title="BIP Entwicklung",
            template="plotly_dark",
            color_discrete_sequence=[color_choice]  # Wichtig!
        )

    else:  # Punkte
        fig = px.scatter(
            filtered_df, x="year", y="gdp",
            title="BIP Entwicklung",
            template="plotly_dark",
            color_discrete_sequence=[color_choice]  # Wichtig!
        )

    fig.update_layout(
        yaxis_tickprefix="$", yaxis_tickformat=",.0f",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Keine Daten für die gewählten Filter gefunden.")
