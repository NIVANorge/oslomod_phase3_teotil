import altair as alt
import pandas as pd
import streamlit as st
from utils import (
    filter_data,
    load_data,
    plot_baseline_contribution,
    plot_percentage_change_contributions,
    plot_stacked_bar,
)

# Load data
df = load_data("./data/results_summary.csv")

# Sidebar filters
st.sidebar.header("Filter Data")
selected_område = st.sidebar.selectbox("Velg område", sorted(df["Område"].unique()))
selected_parameter = st.sidebar.selectbox(
    "Velg parameter", sorted(df["Parameter"].unique())
)

# Filtered data
filtered_df = filter_data(df, selected_område, selected_parameter)

# Main content
st.title("OsloMod scenario data")

with st.expander("ℹ️ Detaljer om scenariene (klikk for å åpne)"):
    with open("./data/scenario_info_nor.md", "r", encoding="utf-8") as f:
        st.markdown(f.read())

st.altair_chart(plot_stacked_bar(filtered_df), use_container_width=True)
st.altair_chart(plot_baseline_contribution(filtered_df), use_container_width=True)
st.altair_chart(
    plot_percentage_change_contributions(filtered_df), use_container_width=True
)