import itertools
import os
import shutil

import geopandas as gpd
import matplotlib.pyplot as plt
import nivapy3 as nivapy
import numpy as np
import pandas as pd
import requests
import teotil3 as teo

TEO3_PARS = [
    "totn_kg",
    "din_kg",
    "ton_kg",
    "totp_kg",
    "tdp_kg",
    "tpp_kg",
    "toc_kg",
    "ss_kg",
]
WW_PARS = ["totn", "totp", "bof5", "kof", "ss"]
TEO3_BASE_DIR = r"/home/jovyan/shared/common/teotil3"


def get_vassom_regines(vassom_list, eng, year):
    """ """
    reg_gdf = teo.io.get_regine_geodataframe(eng, year)
    reg_gdf["vassom_int"] = reg_gdf["vassom"].astype(int)
    reg_gdf = reg_gdf.query("vassom_int in @vassom_list")
    del reg_gdf["vassom_int"]

    return reg_gdf


def get_supporting_db_tables(eng):
    """ """
    par_df = pd.read_sql("SELECT * FROM teotil3.output_param_definitions", eng)
    conv_df = pd.read_sql("SELECT * FROM teotil3.input_output_param_conversion", eng)

    return (par_df, conv_df)


def read_raw_agri_scen_data(year, scen, data_fold, loss_type):
    """Modified from teo.preprocessing.read_raw_agri_data.

    Reads the raw agricultural data for the specified scenario from a
    NIBIO template. Templates must be named "Leveranse_{year}.xlsx" and
    have a worksheet named 'scen'.

    Args
        year: Int. Year of interest.
        scen: Str. Scenario of interest. Also name of worksheet to read in
            the Excel file.
        data_fold: Str. Path to folder containing templates.
        loss_type: Str. 'annual' or 'risk' The loss type for the
            agricultural model.

    Returns
        Dataframe of agricultural data.

    Raises
        ValueError if estimated losses are nagative.
        ValueError if column names cannot be parsed correctly.
    """
    pars = ["totn", "din", "ton", "totp", "tdp", "tpp", "ss", "toc"]
    srcs = ["agriculture", "agriculture_background"]
    valid_cols = ["regine"] + [
        f"{src}_{par}_kg" for src, par in itertools.product(srcs, pars)
    ]
    xl_path = os.path.join(data_fold, f"Leveranse_{year}.xlsx")
    df = pd.read_excel(xl_path, sheet_name=scen, header=[0, 1])
    df.columns = df.columns.map("_".join).str.replace(" ", "")
    names_dict = teo.preprocessing.get_agri_names_dict(loss_type)
    df.rename(columns=names_dict, inplace=True)
    teo.preprocessing.convert_agri_units(df)
    teo.preprocessing.calculate_derived_agri_parameters(df)

    numeric_cols = df.select_dtypes(include=np.number)
    if numeric_cols.lt(0).any().any():
        raise ValueError(
            f"The template for {year} contains negative losses for {numeric_cols.columns.tolist()}."
        )

    if set(valid_cols) != set(df.columns):
        raise ValueError("Template contains invalid columns.")

    df = df[valid_cols]
    df.columns = [
        col.replace("agriculture_background", "agriculture-background")
        for col in df.columns
    ]

    return df


def apply_agri_scenario(orig_df, agri_scen_df):
    """Replace original agricultural losses with those from an agricultural
    scenario.

    Args
        orig_df: DataFrame. Original TEOTIL3 input data.
        agri_scen_df: DataFrame. Agircultural scenario data returned by
            'read_raw_agri_scen_data'

    Returns
        DataFrame.
    """
    agri_cols = [col for col in agri_scen_df.drop(columns="regine").columns]
    non_agri_df = orig_df.drop(columns=agri_cols).copy()
    df = pd.merge(non_agri_df, agri_scen_df, how="left", on="regine")
    df.fillna({col: 0 for col in agri_cols}, inplace=True)

    return df


def copy_industry_data(scen_data_fold, year):
    """ """
    scen_ann_data_fold = os.path.join(scen_data_fold, str(year))
    src = os.path.join(
        TEO3_BASE_DIR, "point_data", str(year), f"industry_{year}_raw.xlsx"
    )
    dst = os.path.join(scen_ann_data_fold, f"industry_{year}_raw.xlsx")
    shutil.copy2(src, dst)


def copy_metals_data(scen_data_fold, year):
    """ """
    scen_ann_data_fold = os.path.join(scen_data_fold, str(year))

    # Read original metals data and remove 'type' col
    metals_xl_path = os.path.join(
        TEO3_BASE_DIR, "point_data", str(year), f"metals_{year}_raw.xlsx"
    )
    metals_df = pd.read_excel(metals_xl_path).drop(columns="type")

    # Read the modified types from scenario data
    ww_xl_path = os.path.join(scen_ann_data_fold, f"large_wastewater_{year}_raw.xlsx")
    ww_df = pd.read_excel(ww_xl_path)[["anlegg_nr", "year", "type"]]

    # Join updated site types from scenario
    metals_df = pd.merge(metals_df, ww_df, how="left", on=["anlegg_nr", "year"])

    # Save
    dst_xl_path = os.path.join(scen_ann_data_fold, f"metals_{year}_raw.xlsx")
    metals_df.to_excel(dst_xl_path)


def apply_wastewater_scenario(
    df,
    reg_gdf,
    scen_data_fold,
    year,
    eng,
    scen,
):
    """ """
    par_df, conv_df = get_supporting_db_tables(eng)

    copy_industry_data(scen_data_fold, year)
    copy_metals_data(scen_data_fold, year)

    # Process modified raw data
    scen_ann_data_fold = os.path.join(scen_data_fold, str(year))
    loc_gdf, ww_df = teo.preprocessing.read_large_wastewater_and_industry_data(
        scen_ann_data_fold, year, eng
    )

    # Assign to regines
    loc_df = gpd.sjoin(
        loc_gdf,
        reg_gdf[["regine", "geometry"]],
        how="inner",
        predicate="within",
    )[["site_id", "sector", "regine"]]

    # Convert units and aggregate
    ww_df = pd.merge(ww_df, conv_df, how="left", on="in_par_id")
    ww_df = pd.merge(ww_df, par_df, how="left", on="out_par_id")
    ww_df = pd.merge(ww_df, loc_df, how="left", on="site_id")
    ww_df = ww_df.query("sector == 'Large wastewater'").dropna(subset="regine")

    # Tidy
    ww_df["name"] = ww_df["name"] + "_" + ww_df["unit"]
    ww_df["value"] = ww_df["value"] * ww_df["factor"]
    ww_df = (
        ww_df[["regine", "name", "value"]]
        .groupby(["regine", "name"])
        .sum()
        .reset_index()
        .pivot(index="regine", columns="name", values="value")
    )
    cols = [f"large-wastewater_{col.lower()}" for col in ww_df.columns]
    ww_df.columns = cols
    ww_df.columns.name = ""
    cols = [
        f"large-wastewater_{col}"
        for col in TEO3_PARS
        if f"large-wastewater_{col}" in ww_df.columns
    ]
    ww_df = ww_df[cols].copy()
    ww_df = ww_df.round(1)
    ww_df.reset_index(inplace=True)

    # Replace original wastewater discharges with scenario values
    drop_cols = [col for col in ww_df.columns if col != "regine"]
    df.drop(columns=drop_cols, inplace=True)
    df = pd.merge(df, ww_df, how="left", on="regine")
    for col in drop_cols:
        df[col] = df[col].fillna(0)

    # Save modified model input file
    scen_csv = os.path.join(
        scen_data_fold,
        f"oslomod_teotil3_input_data_{scen.lower()}_{year}.csv",
    )
    df.to_csv(scen_csv, index=False)


def read_raw_wastewater_data(year):
    """ """
    # Read raw wastewater data
    ww_xls = os.path.join(
        TEO3_BASE_DIR, "point_data", str(year), f"large_wastewater_{year}_raw.xlsx"
    )
    df = pd.read_excel(ww_xls)
    assert df["anlegg_nr"].is_unique

    # Patch gaps in capacity info
    df["current_capacity"] = df["current_capacity"].fillna(df["design_capacity"])
    assert df["current_capacity"].isna().sum() == 0

    return df


def validate_percentage(value):
    """ """
    if not (0 <= value <= 100):
        raise ValueError(f"Value {value} is out of range. Must be between 0 and 100.")
    if 0 < value < 1:
        print(
            f"WARNING: Value {value} is low. Be sure to specify percentages, not fractions."
        )


def estimate_overflows(df, scen_dict):
    """ """
    overflow_dict = scen_dict.get("overflow")
    if overflow_dict:
        for cap, pct in overflow_dict.items():
            validate_percentage(pct)

            # Get sites within specified capacity interval
            min_cap, max_cap = map(lambda x: int(float(x)), cap.split("-"))
            site_list = (
                df.query("@min_cap <= current_capacity < @max_cap")["anlegg_nr"]
                .unique()
                .tolist()
            )

            # Estimate overflows
            for par in WW_PARS:
                df["overflow"] = pct * df[f"{par}_in_tonnes"] / 100
                df["overflow"] = df["overflow"].fillna(0)
                df.loc[~df["anlegg_nr"].isin(site_list), "overflow"] = 0
                df[f"{par}_out_tonnes"] = df[f"{par}_out_tonnes"] + df["overflow"]
                del df["overflow"]

    return df


def upgrade_sites_by_capacity(df, scen_dict):
    """ """
    upgrade_dict = scen_dict.get("upgrade_by_capacity")
    if upgrade_dict:
        for cap, eff_dict in upgrade_dict.items():
            # Get sites within specified capacity interval
            min_cap, max_cap = map(lambda x: int(float(x)), cap.split("-"))
            site_list = (
                df.query("@min_cap <= current_capacity < @max_cap")["anlegg_nr"]
                .unique()
                .tolist()
            )

            # Upgrade matching plants to specified type
            new_type = eff_dict.get("type")
            if new_type:
                validate_site_type(new_type)
                df.loc[df["anlegg_nr"].isin(site_list), "type"] = new_type

            # Update efficiencies for specified pars
            upgrade_pars = [par for par in eff_dict.keys() if par != "type"]
            assert set(upgrade_pars).issubset(set(WW_PARS))
            for par in upgrade_pars:
                new_eff = eff_dict[par]
                validate_percentage(new_eff)

                # Calculate true renseeffekt
                df["eff_true"] = (
                    100
                    * (df[f"{par}_in_tonnes"] - df[f"{par}_out_tonnes"])
                    / df[f"{par}_in_tonnes"]
                )

                # Update values where the true efficiency is below the new value
                df["eff_new"] = new_eff
                df["eff_new"] = df[["eff_true", "eff_new"]].max(axis=1)
                assert df["eff_new"].between(0, 100).all()

                # Calculate outflows with the new efficiency
                df["out_new"] = df[f"{par}_in_tonnes"] * (1 - df["eff_new"] / 100)

                # Update values for specified sites
                df.loc[df["anlegg_nr"].isin(site_list), f"{par}_out_tonnes"] = df.loc[
                    df["anlegg_nr"].isin(site_list), "out_new"
                ]

                df = df.drop(columns=["eff_true", "eff_new", "out_new"])

    return df


def upgrade_sites_by_id(df, scen_dict):
    """ """
    upgrade_dict = scen_dict.get("upgrade_by_id")
    if upgrade_dict:
        site_list = upgrade_dict.get("id_list")
        if site_list is None:
            raise ValueError("'upgrade_by_id' requires a list of site IDs.")

        # Upgrade plants to specified type
        new_type = upgrade_dict.get("type")
        if new_type:
            validate_site_type(new_type)
            df.loc[df["anlegg_nr"].isin(site_list), "type"] = new_type

        # Update efficiencies for specified pars
        upgrade_pars = [
            par for par in upgrade_dict.keys() if par not in ("type", "id_list")
        ]
        assert set(upgrade_pars).issubset(set(WW_PARS))
        for par in upgrade_pars:
            new_eff = upgrade_dict[par]
            validate_percentage(new_eff)

            # Calculate true renseeffekt
            df["eff_true"] = (
                100
                * (df[f"{par}_in_tonnes"] - df[f"{par}_out_tonnes"])
                / df[f"{par}_in_tonnes"]
            )

            # Update values where the true efficiency is below the new value
            df["eff_new"] = new_eff
            df["eff_new"] = df[["eff_true", "eff_new"]].max(axis=1)
            assert df["eff_new"].between(0, 100).all()

            # Calculate outflows with the new efficiency
            df["out_new"] = df[f"{par}_in_tonnes"] * (1 - df["eff_new"] / 100)

            # Update values for specified sites
            df.loc[df["anlegg_nr"].isin(site_list), f"{par}_out_tonnes"] = df.loc[
                df["anlegg_nr"].isin(site_list), "out_new"
            ]

            df = df.drop(columns=["eff_true", "eff_new", "out_new"])

    return df


def validate_site_type(site_type):
    """ """
    url = r"https://raw.githubusercontent.com/NIVANorge/teotil3/refs/heads/main/data/point_source_treatment_types.csv"
    df = pd.read_csv(url).query("sector == 'Large wastewater'")
    valid_list = df["type"].unique().tolist()
    if site_type not in valid_list:
        raise ValueError(
            f"Site type '{site_type}' is not a valid type for large wastewater in TEOTIL3."
        )


def get_ww_data_for_vassoms_and_years(
    vassom_list,
    year_list,
    eng,
    par_list=[
        "totn_kg",
        "din_kg",
        "ton_kg",
        "totp_kg",
        "tdp_kg",
        "tpp_kg",
        "toc_kg",
        "ss_kg",
    ],
):
    """ """
    df_list = []
    for year in year_list:
        site_df = teo.io.get_raw_annual_point_data(
            eng,
            year,
            "large wastewater",
            par_list=par_list,
        )[["site_id", "regine", "year"]]

        # Filter to vassoms of interest
        site_df["vassom"] = (
            site_df["regine"].str.split(".", n=1, expand=True)[0].astype(int)
        )
        site_df = (
            site_df.query("vassom in @vassom_list")
            .reset_index(drop=True)
            .rename(columns={"site_id": "anlegg_nr"})
        )

        # Read annual raw data
        xl_path = os.path.join(
            TEO3_BASE_DIR, "point_data", str(year), f"large_wastewater_{year}_raw.xlsx"
        )
        ww_df = pd.read_excel(xl_path)

        df = pd.merge(site_df, ww_df, how="inner", on=["anlegg_nr", "year"])

        df_list.append(df)

    df = pd.concat(df_list, axis="rows")

    return df