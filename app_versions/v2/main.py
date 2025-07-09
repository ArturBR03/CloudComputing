import streamlit as st
import pandas as pd
import plotly.express as px


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
    selected_countries = st.multiselect("Länder wählen", countries, default=[countries[0]])

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
    show_table = st.checkbox("Tabelle anzeigen", value=True)

# Daten filtern
filtered_df = df[
    (df["country"].isin(selected_countries)) &
    (df["year"].between(selected_years[0], selected_years[1]))
].sort_values(["country", "year"])

# Titel
st.title("BIP-Analyse")
st.subheader(f"Zeitraum: {selected_years[0]} - {selected_years[1]}")

if not filtered_df.empty:
    if len(selected_countries) == 1:
        country_df = filtered_df[filtered_df["country"] == selected_countries[0]]
        latest = country_df.iloc[-1]
        delta = (
            f"{(latest['gdp'] - country_df.iloc[-2]['gdp'])/1e9:+.1f} Mrd USD"
            if len(country_df) > 1 else "N/A"
        )

        st.metric(
            label=f"Letztes verfügbares BIP ({latest['year']}, {latest['country']})",
            value=f"{latest['gdp']/1e12:,.2f} Bio USD",
            delta=delta,
        )

        avg_gdp = country_df["gdp"].mean()
        st.info(f"Durchschnittliches BIP im gewählten Zeitraum: {avg_gdp/1e12:.2f} Bio USD")

    # Diagramm erzeugen
    common_args = dict(
        data_frame=filtered_df,
        x="year",
        y="gdp",
        color="country" if len(selected_countries) > 1 else None,
        template="plotly_dark",
        title="BIP Entwicklung",
    )

    if plot_type == "Linie":
        fig = px.line(**common_args, markers=True)
        if len(selected_countries) == 1:
            fig.update_traces(line=dict(color=color_choice))

    elif plot_type == "Balken":
        fig = px.bar(**common_args,
                     color_discrete_sequence=[color_choice] if len(selected_countries) == 1 else px.colors.qualitative.Set2)

    else:  # Punkte
        fig = px.scatter(**common_args,
                         color_discrete_sequence=[color_choice] if len(selected_countries) == 1 else px.colors.qualitative.Set1)

    fig.update_layout(
        yaxis_tickprefix="$",
        yaxis_tickformat=",.0f",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Download-Button
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 CSV herunterladen",
        data=csv,
        file_name="gefilterte_bip_daten.csv",
        mime="text/csv"
    )

else:
    st.warning("Keine Daten für die gewählten Filter gefunden.")
