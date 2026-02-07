import json
import os
from modules.data_loader import load_dataset
from modules.data_processor import filter_dataset, compute_statistic
from modules.visualizer import (
    region_bar_chart,
    region_pie_chart,
    yearly_histogram,
    yearly_scatter
)

def run_dashboard():

    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    config = json.load(open(config_path, "r", encoding="utf-8"))

    region = config["region"]
    year = config["year"]
    operation = config["operation"]

    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "gdp_with_continent_filled.csv")
    df = load_dataset(data_path)

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