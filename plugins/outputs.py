from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt

from core.contracts import DataSink


class ConsoleWriter(DataSink):
    def write(self, records: dict[str, Any]) -> None:
        context = records["context"]
        print("========== GDP ANALYTICS REPORT ==========")
        print(
            "Context:",
            f"Region={context['region']}, Year={context['year']}, "
            f"Range={context['start_year']}-{context['end_year']}, "
            f"DeclineWindow={context['decline_years']} years",
        )

        self._print_ranked("Top 10 Countries by GDP", records["top_10_countries"])
        self._print_ranked("Bottom 10 Countries by GDP", records["bottom_10_countries"])
        self._print_growth_rates(records["country_growth_rates"])
        self._print_avg_continent(records["average_gdp_by_continent"])
        self._print_global_trend(records["global_gdp_trend"])
        self._print_fastest_continent(records["fastest_growing_continent"])
        self._print_decline(records["consistent_decline_countries"])
        self._print_contribution(records["continent_contribution"])

    def _print_ranked(self, title: str, rows: list[dict[str, Any]]) -> None:
        print(f"\n{title}:")
        list(
            map(
                lambda item: print(f"- {item['country']}: {item['gdp']:.2f}"),
                rows,
            )
        )

    def _print_growth_rates(self, rows: list[dict[str, Any]]) -> None:
        print("\nGDP Growth Rate by Country:")
        list(
            map(
                lambda item: print(
                    f"- {item['country']}: {item['growth_rate_pct']:.2f}% "
                    f"({item['start_value']:.2f} -> {item['end_value']:.2f})"
                ),
                rows,
            )
        )

    def _print_avg_continent(self, rows: list[dict[str, Any]]) -> None:
        print("\nAverage GDP by Continent:")
        list(map(lambda item: print(f"- {item['continent']}: {item['average_gdp']:.2f}"), rows))

    def _print_global_trend(self, rows: list[dict[str, Any]]) -> None:
        print("\nTotal Global GDP Trend:")
        list(map(lambda item: print(f"- {item['year']}: {item['total_gdp']:.2f}"), rows))

    def _print_fastest_continent(self, item: dict[str, Any]) -> None:
        print("\nFastest Growing Continent:")
        if not item:
            print("- Not available")
            return
        print(
            f"- {item['continent']}: {item['growth_rate_pct']:.2f}% "
            f"({item['start_total']:.2f} -> {item['end_total']:.2f})"
        )

    def _print_decline(self, rows: list[dict[str, Any]]) -> None:
        print("\nCountries with Consistent GDP Decline:")
        if not rows:
            print("- None")
            return
        list(map(lambda item: print(f"- {item['country']}"), rows))

    def _print_contribution(self, rows: list[dict[str, Any]]) -> None:
        print("\nContinent Contribution to Global GDP:")
        list(
            map(
                lambda item: print(
                    f"- {item['continent']}: {item['contribution_pct']:.2f}% "
                    f"(Total={item['total_gdp']:.2f})"
                ),
                rows,
            )
        )


class GraphicsChartWriter(DataSink):
    def write(self, records: dict[str, Any]) -> None:
        self._plot_top_bottom(records)
        self._plot_global_trend(records)
        self._plot_average_by_continent(records)
        self._plot_continent_contribution(records)
        plt.show()

    def _plot_top_bottom(self, records: dict[str, Any]) -> None:
        top_rows = records["top_10_countries"]
        bottom_rows = records["bottom_10_countries"]

        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        if top_rows:
            top_countries = list(map(lambda item: item["country"], top_rows))
            top_values = list(map(lambda item: item["gdp"], top_rows))
            axes[0].bar(top_countries, top_values)
            axes[0].set_title("Top 10 Countries by GDP")
            axes[0].tick_params(axis="x", rotation=75)

        if bottom_rows:
            bottom_countries = list(map(lambda item: item["country"], bottom_rows))
            bottom_values = list(map(lambda item: item["gdp"], bottom_rows))
            axes[1].bar(bottom_countries, bottom_values, color="orange")
            axes[1].set_title("Bottom 10 Countries by GDP")
            axes[1].tick_params(axis="x", rotation=75)

        fig.tight_layout()

    def _plot_global_trend(self, records: dict[str, Any]) -> None:
        trend_rows = records["global_gdp_trend"]
        if not trend_rows:
            return

        years = list(map(lambda item: item["year"], trend_rows))
        values = list(map(lambda item: item["total_gdp"], trend_rows))

        plt.figure(figsize=(8, 4))
        plt.plot(years, values, marker="o")
        plt.title("Total Global GDP Trend")
        plt.xlabel("Year")
        plt.ylabel("GDP")
        plt.tight_layout()

    def _plot_average_by_continent(self, records: dict[str, Any]) -> None:
        rows = records["average_gdp_by_continent"]
        if not rows:
            return

        continents = list(map(lambda item: item["continent"], rows))
        averages = list(map(lambda item: item["average_gdp"], rows))

        plt.figure(figsize=(8, 4))
        plt.bar(continents, averages)
        plt.title("Average GDP by Continent")
        plt.xticks(rotation=45)
        plt.ylabel("Average GDP")
        plt.tight_layout()

    def _plot_continent_contribution(self, records: dict[str, Any]) -> None:
        rows = records["continent_contribution"]
        if not rows:
            return

        continents = list(map(lambda item: item["continent"], rows))
        percentages = list(map(lambda item: item["contribution_pct"], rows))

        plt.figure(figsize=(7, 7))
        plt.pie(percentages, labels=continents, autopct="%1.1f%%")
        plt.title("Contribution of Each Continent to Global GDP")
        plt.tight_layout()
