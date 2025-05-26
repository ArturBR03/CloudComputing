import streamlit as st
import pandas as pd
import plotly.express as px



try:
    df = pd.read_csv("world_data.csv")
except FileNotFoundError:
    print("no csv file found")


df = df.dropna(subset=["country", "year", "gdp"]).sort_values("year")
df["year"] = df["year"].astype(int)


with st.sidebar:
    st.title("BIP Selector/Filter")
    countries = sorted(df["country"].unique())
    selected_country = st.selectbox("Land wählen", countries)

    min_year = df["year"].min()
    max_year = df["year"].max()
    selected_years = st.slider(
        "Zeitraum wählen",
        min_value=min_year,
        max_value=max_year,
        value=(max_year - 10, max_year))



filtered_df = df[
    (df["country"] == selected_country) &
    (df["year"].between(selected_years[0], selected_years[1]))
].sort_values("year")


st.title(f"BIP-Entwicklung in {selected_country}")
st.subheader(f"Jahresauswahl: {selected_years[0]} - {selected_years[1]}")

if not filtered_df.empty:
    latest_data = filtered_df.iloc[-1]
    st.metric(
        label=f"Letztes BIP ({latest_data['year']})",
        value=f"{latest_data['gdp']/1e12:,.2f} Bio USD",
        delta=f"{(latest_data['gdp'] - filtered_df.iloc[-2]['gdp'])/1e9:+.1f} Mrd USD" if len(filtered_df) > 1 else "N/A"
    )

    fig = px.line(
        filtered_df,
        x="year",
        y="gdp",
        labels={"gdp": "BIP in USD", "year": "Jahr"},
        title=f"BIP-Entwicklung für {selected_country}",
        template="plotly_dark",
        markers=True
    )
    
    fig.update_layout(
        hovermode="x unified",
        yaxis_tickprefix="$",
        yaxis_tickformat=",.0f"
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("No data found")