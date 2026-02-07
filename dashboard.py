import json
from modules.data_loader import load_dataset
from modules.data_processor import filter_dataset, compute_statistic
from modules.visualizer import (
    region_bar_chart,
    region_pie_chart,
    yearly_histogram,
    yearly_scatter
)

def run_dashboard():

    config = json.load(open("config.json"))

    region = config["region"]
    year = config["year"]
    operation = config["operation"]

    df = load_dataset("data/gdp_data.csv")

    filtered = filter_dataset(df, region, year)

    result = compute_statistic(filtered, operation)

    print("=========== GDP DASHBOARD ===========")
    print("Region:", region)
    print("Year:", year)
    print("Operation:", operation)
    print("Result:", result)

    region_bar_chart(filtered, region, year)
    region_pie_chart(filtered, region, year)
    yearly_histogram(df, year)
    yearly_scatter(df, year)