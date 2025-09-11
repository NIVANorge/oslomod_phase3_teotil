import altair as alt
import pandas as pd

COLOUR_DICT = {
    "Akvakultur": "royalblue",
    "Jordbruk": "sienna",
    "Kommunalt avløp": "red",
    "Spredt avløp": "orange",
    "Industri": "darkgrey",
    "Bebygd": "gold",
    "Bakgrunn": "limegreen",
}


def load_data(path):
    return pd.read_csv(path)


def filter_data(df, område, parameter):
    return df[(df["Område"] == område) & (df["Parameter"] == parameter)]


def plot_stacked_bar(df):
    df = df.copy()
    df["Verdi_rundet"] = df["Verdi (tonn)"].round(3)
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x="Scenario:N",
            y="Verdi (tonn):Q",
            color=alt.Color(
                "Kilde:N",
                scale=alt.Scale(
                    domain=list(COLOUR_DICT.keys()), range=list(COLOUR_DICT.values())
                ),
            ),
            tooltip=[
                "Scenario",
                "Kilde",
                alt.Tooltip("Verdi_rundet:Q", title="Verdi (tonn)"),
            ],
        )
        .properties(
            title="Gjennomsnittlig årlig tilførsel per kilde (2017–2019)", height=400
        )
    )

    return chart


def plot_baseline_contribution(df):
    baseline_df = df[df["Scenario"] == "Baseline"]
    total = baseline_df.groupby("Område")["Verdi (tonn)"].transform("sum")
    baseline_df = baseline_df.copy()
    baseline_df["Prosent"] = (baseline_df["Verdi (tonn)"] / total) * 100
    baseline_df["Prosent_rundet"] = baseline_df["Prosent"].round(1)

    chart = (
        alt.Chart(baseline_df)
        .mark_bar()
        .encode(
            y=alt.Y("Kilde:N", sort="-x"),
            x="Prosent:Q",
            tooltip=["Kilde", alt.Tooltip("Prosent_rundet:Q", title="Andel (%)")],
        )
        .properties(title="Baseline kildefordeling (2017 - 2019)", height=400)
    )

    return chart


def plot_percentage_change_contributions(df):
    # Baseline totals by source
    baseline_df = (
        df[df["Scenario"] == "Baseline"]
        .groupby("Kilde")["Verdi (tonn)"]
        .sum()
        .reset_index()
    )
    total_baseline = df[df["Scenario"] == "Baseline"]["Verdi (tonn)"].sum()

    # Totals per scenario and per source
    scenario_df = (
        df[df["Scenario"] != "Baseline"]
        .groupby(["Scenario", "Kilde"])["Verdi (tonn)"]
        .sum()
        .reset_index()
    )
    total_scenario = (
        df[df["Scenario"] != "Baseline"]
        .groupby("Scenario")["Verdi (tonn)"]
        .sum()
        .reset_index()
    )
    total_scenario = total_scenario.rename(
        columns={"Verdi (tonn)": "TotalScenarioVerdi"}
    )

    # Merge
    merged = pd.merge(scenario_df, baseline_df, on="Kilde", suffixes=("", "_baseline"))
    merged = pd.merge(merged, total_scenario, on="Scenario")

    # Calculate percentage change per source
    merged["KildeEndring"] = merged["Verdi (tonn)"] - merged["Verdi (tonn)_baseline"]
    merged["KildeEndringProsent"] = (merged["KildeEndring"] / total_baseline) * 100
    merged["KildeEndringProsent_rundet"] = merged["KildeEndringProsent"].round(1)

    chart = (
        alt.Chart(merged)
        .mark_bar()
        .encode(
            y=alt.Y("Scenario:N", title="Scenario"),
            x=alt.X("KildeEndringProsent_rundet:Q", title="Total Prosentvis Endring"),
            color=alt.Color(
                "Kilde:N",
                scale=alt.Scale(
                    domain=list(COLOUR_DICT.keys()), range=list(COLOUR_DICT.values())
                ),
            ),
            tooltip=[
                "Scenario",
                "Kilde",
                alt.Tooltip("KildeEndringProsent_rundet:Q", title="Endring (%)"),
            ],
        )
        .properties(
            title="Prosentvis endring fra baseline (bidrag per kilde)", height=250
        )
    )

    return chart