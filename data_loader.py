import pandas as pd

def load_dataset(path):
    try:
        df = pd.read_csv(path)

        df = df.dropna()

        df["Year"] = df["Year"].astype(int)
        df["Value"] = df["Value"].astype(float)

        return df

    except FileNotFoundError:
        raise Exception("CSV file not found")
    except Exception as e:
        raise Exception(f"Data loading error: {e}")


def clean_data(df):
    try:
        # Drop rows with missing critical values
        df = df.dropna(subset=["Country name", "Region", "Year", "Value"])

        # Convert data types safely
        df["Year"] = df["Year"].astype(int)
        df["Value"] = df["Value"].astype(float)

        # Strip whitespace from string columns
        string_columns = ["Country name", "Region"]
        df[string_columns] = df[string_columns].apply(
            lambda col: col.str.strip()
        )

        return df

    except Exception as e:
        raise Exception(f"Data cleaning error: {e}")