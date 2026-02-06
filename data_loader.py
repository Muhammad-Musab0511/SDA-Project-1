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
