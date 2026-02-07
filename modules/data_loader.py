import pandas as pd

def load_dataset(path):
    try:
        df = pd.read_csv(path)

        # Remove unused columns
        df = df.drop(columns=["Country Code", "Indicator Name", "Indicator Code"])

        # Rename Continent -> Region (project requirement)
        df = df.rename(columns={"Continent": "Region"})

        # Convert wide years into rows
        df = df.melt(
            id_vars=["Country Name", "Region"],
            var_name="Year",
            value_name="Value"
        )

        # Clean data
        df = df.dropna()

        df["Year"] = df["Year"].astype(int)
        df["Value"] = df["Value"].astype(float)

        return df

    except FileNotFoundError:
        raise Exception("CSV file not found")
    except Exception as e:
        raise Exception(f"Data loading error: {e}")
