from __future__ import annotations

from typing import Any

import pandas as pd

from .contracts import DataSink


class TransformationEngine:
    def __init__(self, sink: DataSink, settings: dict[str, Any]):
        self.sink = sink
        self.settings = settings

    def execute(self, raw_data: list[dict[str, Any]]) -> None:
        frame = pd.DataFrame(raw_data)
        normalized = self._normalize(frame)
        report = self._build_report(normalized)
        self.sink.write(report)

    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        if "Region" not in df.columns and "Continent" in df.columns:
            df = df.rename(columns={"Continent": "Region"})

        has_long_shape = {"Country Name", "Region", "Year", "Value"}.issubset(set(df.columns))
        if not has_long_shape:
            year_columns = list(filter(lambda column_name: str(column_name).isdigit(), df.columns))
            required = ["Country Name", "Region"]
            missing = list(filter(lambda column_name: column_name not in df.columns, required))
            if missing:
                raise ValueError(f"Input data missing required fields: {missing}")
            df = df.melt(id_vars=required, value_vars=year_columns, var_name="Year", value_name="Value")

        df = df.dropna(subset=["Country Name", "Region", "Year", "Value"]).copy()
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
        df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
        df = df.dropna(subset=["Year", "Value"]).copy()
        df["Year"] = df["Year"].astype(int)
        df["Value"] = df["Value"].astype(float)
        return df

    def _build_report(self, df: pd.DataFrame) -> dict[str, Any]:
        region = self.settings["region"]
        single_year = int(self.settings["year"])
        start_year = int(self.settings["start_year"])
        end_year = int(self.settings["end_year"])
        decline_years = int(self.settings["decline_years"])

        if start_year > end_year:
            raise ValueError("start_year cannot be greater than end_year")

        region_filter = df if str(region).upper() == "ALL" else df[df["Region"] == region]
        year_region_df = region_filter[region_filter["Year"] == single_year]

        top10 = self._to_country_value_records(year_region_df.nlargest(10, "Value"))
        bottom10 = self._to_country_value_records(year_region_df.nsmallest(10, "Value"))

        range_df = region_filter[(region_filter["Year"] >= start_year) & (region_filter["Year"] <= end_year)]

        growth_rates = self._country_growth_rates(range_df)
        avg_by_continent = self._avg_gdp_by_continent(df, start_year, end_year)
        global_trend = self._global_gdp_trend(df, start_year, end_year)
        fastest_continent = self._fastest_growing_continent(df, start_year, end_year)
        declining_countries = self._consistent_decline(range_df, end_year, decline_years)
        continent_contribution = self._continent_contribution(df, start_year, end_year)

        return {
            "context": {
                "region": region,
                "year": single_year,
                "start_year": start_year,
                "end_year": end_year,
                "decline_years": decline_years,
            },
            "top_10_countries": top10,
            "bottom_10_countries": bottom10,
            "country_growth_rates": growth_rates,
            "average_gdp_by_continent": avg_by_continent,
            "global_gdp_trend": global_trend,
            "fastest_growing_continent": fastest_continent,
            "consistent_decline_countries": declining_countries,
            "continent_contribution": continent_contribution,
        }

    def _to_country_value_records(self, frame: pd.DataFrame) -> list[dict[str, Any]]:
        columns = frame[["Country Name", "Value"]]
        return list(
            map(
                lambda row: {
                    "country": row[0],
                    "gdp": float(row[1]),
                },
                columns.to_numpy(),
            )
        )

    def _country_growth_rates(self, frame: pd.DataFrame) -> list[dict[str, Any]]:
        if frame.empty:
            return []

        ordered = frame.sort_values(["Country Name", "Year"])
        grouped = ordered.groupby("Country Name", as_index=False)

        growth_rows: list[dict[str, Any]] = []
        for _, group in grouped:
            start_value = float(group.iloc[0]["Value"])
            end_value = float(group.iloc[-1]["Value"])
            if start_value == 0:
                continue
            growth_rate = ((end_value - start_value) / start_value) * 100
            growth_rows.append(
                {
                    "country": group.iloc[0]["Country Name"],
                    "start_value": start_value,
                    "end_value": end_value,
                    "growth_rate_pct": float(growth_rate),
                }
            )

        return sorted(growth_rows, key=lambda item: item["growth_rate_pct"], reverse=True)

    def _avg_gdp_by_continent(self, df: pd.DataFrame, start_year: int, end_year: int) -> list[dict[str, Any]]:
        in_range = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]
        grouped = in_range.groupby("Region", as_index=False)["Value"].mean().sort_values("Value", ascending=False)
        return list(
            map(
                lambda row: {
                    "continent": row[0],
                    "average_gdp": float(row[1]),
                },
                grouped[["Region", "Value"]].to_numpy(),
            )
        )

    def _global_gdp_trend(self, df: pd.DataFrame, start_year: int, end_year: int) -> list[dict[str, Any]]:
        in_range = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]
        grouped = in_range.groupby("Year", as_index=False)["Value"].sum().sort_values("Year")
        return list(
            map(
                lambda row: {
                    "year": int(row[0]),
                    "total_gdp": float(row[1]),
                },
                grouped[["Year", "Value"]].to_numpy(),
            )
        )

    def _fastest_growing_continent(self, df: pd.DataFrame, start_year: int, end_year: int) -> dict[str, Any]:
        in_range = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]
        if in_range.empty:
            return {}

        grouped = in_range.groupby(["Region", "Year"], as_index=False)["Value"].sum()
        candidates: list[dict[str, Any]] = []

        for continent in grouped["Region"].unique():
            continent_rows = grouped[grouped["Region"] == continent].sort_values("Year")
            start_value = float(continent_rows.iloc[0]["Value"])
            end_value = float(continent_rows.iloc[-1]["Value"])
            if start_value == 0:
                continue
            growth_rate = ((end_value - start_value) / start_value) * 100
            candidates.append(
                {
                    "continent": continent,
                    "start_total": start_value,
                    "end_total": end_value,
                    "growth_rate_pct": float(growth_rate),
                }
            )

        if not candidates:
            return {}

        return max(candidates, key=lambda item: item["growth_rate_pct"])

    def _consistent_decline(self, range_df: pd.DataFrame, end_year: int, decline_years: int) -> list[dict[str, Any]]:
        if decline_years < 2:
            raise ValueError("decline_years must be at least 2")

        start_decline_window = end_year - decline_years + 1
        window_df = range_df[(range_df["Year"] >= start_decline_window) & (range_df["Year"] <= end_year)]
        if window_df.empty:
            return []

        records: list[dict[str, Any]] = []
        grouped = window_df.groupby("Country Name")

        for country, group in grouped:
            series = group.sort_values("Year")["Value"].tolist()
            if len(series) != decline_years:
                continue
            decreasing = all(map(lambda pair: pair[1] < pair[0], zip(series, series[1:])))
            if decreasing:
                records.append({"country": country})

        return records

    def _continent_contribution(self, df: pd.DataFrame, start_year: int, end_year: int) -> list[dict[str, Any]]:
        in_range = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]
        if in_range.empty:
            return []

        continent_totals = in_range.groupby("Region", as_index=False)["Value"].sum()
        global_total = float(continent_totals["Value"].sum())
        if global_total == 0:
            return []

        return sorted(
            list(
                map(
                    lambda row: {
                        "continent": row[0],
                        "total_gdp": float(row[1]),
                        "contribution_pct": float((row[1] / global_total) * 100),
                    },
                    continent_totals[["Region", "Value"]].to_numpy(),
                )
            ),
            key=lambda item: item["contribution_pct"],
            reverse=True,
        )
