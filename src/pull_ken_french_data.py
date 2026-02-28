""" """

import io
import warnings
import zipfile
from pathlib import Path

import pandas as pd
import pandas_datareader.data as web
import requests

from settings import config

DATA_DIR = config("DATA_DIR")
START_TRAIN_DATE = config("START_TRAIN_DATE")
CURRENT_DATE = config("CURRENT_DATE")

FAMAFRENCH_URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"


def _download_famafrench_direct(dataset_name, start_date, end_date):
    """
    Fallback method to download Fama-French data directly when pandas_datareader fails.
    This handles datasets that trigger parsing bugs in pandas_datareader.
    """
    # Convert dates to strings if they are Timestamp objects
    start_date = str(start_date)
    end_date = str(end_date)

    url = f"{FAMAFRENCH_URL}{dataset_name}_CSV.zip"
    response = requests.get(url)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        # Find the CSV file in the zip
        csv_files = [
            f for f in zf.namelist() if f.endswith(".CSV") or f.endswith(".csv")
        ]
        if not csv_files:
            raise ValueError(f"No CSV file found in {dataset_name}_CSV.zip")

        with zf.open(csv_files[0]) as csv_file:
            raw_content = csv_file.read().decode("utf-8")

    # Parse the file to extract tables and description
    lines = raw_content.strip().split("\n")
    tables = {}
    current_table = []
    table_idx = 0
    description_lines = []
    in_description = True

    for line in lines:
        stripped = line.strip()
        # Detect table headers (lines with commas that look like data)
        if "," in stripped and not stripped.startswith(" "):
            in_description = False
            # Check if this is a new table (empty line before it or first data)
            if (
                current_table
                and stripped
                and not stripped.replace(",", "")
                .replace("-", "")
                .replace(".", "")
                .replace(" ", "")
                .isdigit()
            ):
                # Save previous table if it has data
                if len(current_table) > 1:
                    tables[table_idx] = current_table
                    table_idx += 1
                current_table = []
            current_table.append(stripped)
        elif in_description:
            description_lines.append(line)
        elif stripped == "" and current_table:
            # Empty line might signal end of table
            if len(current_table) > 1:
                tables[table_idx] = current_table
                table_idx += 1
            current_table = []
        elif current_table:
            current_table.append(stripped)

    # Don't forget the last table
    if current_table and len(current_table) > 1:
        tables[table_idx] = current_table

    # Convert tables to DataFrames
    result = {}
    result["DESCR"] = "\n".join(description_lines).strip()

    for idx, table_lines in tables.items():
        try:
            df = pd.read_csv(
                io.StringIO("\n".join(table_lines)),
                index_col=0,
                na_values=["-99.99", "-999"],
            )
            # Filter by date range if index looks like dates
            if df.index.dtype == "int64" or str(df.index.dtype).startswith("int"):
                # Try to parse as YYYYMM format
                start_ym = (
                    int(start_date[:4]) * 100 + int(start_date[5:7])
                    if "-" in start_date
                    else int(start_date[:6])
                )
                end_ym = (
                    int(end_date[:4]) * 100 + int(end_date[5:7])
                    if "-" in end_date
                    else int(end_date[:6])
                )
                df = df[(df.index >= start_ym) & (df.index <= end_ym)]
                # Convert index from YYYYMM to datetime and add as 'Date' column
                # to match pandas_datareader format
                df = df.reset_index()
                df.columns = ["Date"] + list(df.columns[1:])
                df["Date"] = pd.to_datetime(df["Date"].astype(str), format="%Y%m")
            result[idx] = df
        except Exception:
            continue

    return result


def pull_ken_french_excel(
    dataset_name="Portfolios_Formed_on_INV",
    data_dir=DATA_DIR,
    log=True,
    start_date=START_TRAIN_DATE,
    end_date=CURRENT_DATE,
):
    data_dir = Path(data_dir)
    # Suppress the specific FutureWarning about date_parser
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=FutureWarning,
            message="The argument 'date_parser' is deprecated",
        )
        try:
            data = web.DataReader(
                dataset_name,
                "famafrench",
                start=start_date,
                end=end_date,
            )
        except pd.errors.ParserError:
            # Fallback for datasets that trigger parsing bugs in pandas_datareader
            data = _download_famafrench_direct(dataset_name, start_date, end_date)
        excel_path = (
            data_dir / f"{dataset_name.replace('/', '_')}.xlsx"
        )  # Ensure the name is file-path friendly

        with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
            # Write the description to the first sheet
            if "DESCR" in data:
                description_df = pd.DataFrame([data["DESCR"]], columns=["Description"])
                description_df.to_excel(writer, sheet_name="Description", index=False)

            # Write each table in the data to subsequent sheets
            for table_key, df in data.items():
                if table_key == "DESCR":
                    continue  # Skip the description since it's already handled
                sheet_name = str(table_key)  # Naming sheets by their table_key
                # Use index=False if the DataFrame has a 'Date' column (from our fallback)
                # to avoid writing the RangeIndex as a column
                has_date_col = "Date" in df.columns
                df.to_excel(
                    writer, sheet_name=sheet_name[:31], index=not has_date_col
                )  # Sheet name limited to 31 characters
    if log:
        print(f"Excel file saved to {excel_path}")
    return excel_path


def load_returns(dataset_name, weighting="value-weighted", data_dir=DATA_DIR):
    data_dir = Path(data_dir)
    excel_path = data_dir / f"{dataset_name.replace('/', '_')}.xlsx"
    if weighting == "value-weighted":
        sheet_name = "0"
    elif weighting == "equal-weighted":
        sheet_name = "1"
    else:
        raise ValueError(f"Invalid weighting: {weighting}")
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    return df


def load_sheet(dataset_name, sheet_name: str = "0", data_dir=DATA_DIR):
    """For example, for dataset_name = 'Portfolios_Formed_on_INV', the full data
    is the description and the 7 tables of returns and properties.

    Portfolios Formed on INV
    ------------------------

    This file was created by CMPT_EP_CFP_OP_INV_NI_AC_RETS using the 202412 CRSP
    database. It contains value- and equal-weighted returns for portfolios
    formed on INV. The portfolios are constructed at the end of June. INV,
    investment, is the change in total assets from the fiscal year ending in
    year t-2 to the fiscal year ending in t-1, divided by t-2 total assets.
    Annual returns are from January to December. Missing data are indicated by
    -99.99 or -999. The break points include utilities and include financials.
    The portfolios include utilities and include financials. Copyright 2024
    Eugene F. Fama and Kenneth R. French

    0 : Value Weight Returns -- Monthly (696 rows x 18 cols)
    1 : Equal Weight Returns -- Monthly (696 rows x 18 cols)
    2 : Value Weight Returns -- Annual from January to December (58 rows x 18 cols)
    3 : Equal Weight Returns -- Annual from January to December (58 rows x 18 cols)
    4 : Number of Firms in Portfolios (696 rows x 18 cols)
    5 : Average Firm Size (696 rows x 18 cols)
    6 : Value Weight Average of Natural Log of INV (58 rows x 18 cols)
    """
    if isinstance(sheet_name, int):
        sheet_name = str(sheet_name)

    data_dir = Path(data_dir)
    excel_path = data_dir / f"{dataset_name.replace('/', '_')}.xlsx"
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    if sheet_name == "Description":
        return df.iloc[0, 0]
    return df


if __name__ == "__main__":
    datasets = [
        "F-F_Research_Data_Factors",
        "6_Portfolios_2x3",
        "25_Portfolios_5x5",
        "100_Portfolios_10x10"
    ]
    for ds in datasets:
        print(f"Pulling {ds}...")
        pull_ken_french_excel(dataset_name=ds)