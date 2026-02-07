import matplotlib.pyplot as plt

def region_bar_chart(filtered_df, region, year):

    plt.figure()
    plt.bar(filtered_df["Country Name"], filtered_df["Value"], label="GDP")
    plt.title(f"GDP of {region} ({year})")
    plt.xlabel("Country")
    plt.ylabel("GDP")
    plt.legend()
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()


def region_pie_chart(filtered_df, region, year):

    plt.figure()
    plt.pie(filtered_df["Value"], autopct="%1.1f%%")
    plt.title(f"GDP Distribution of {region} ({year})")
    plt.legend(filtered_df["Country Name"], loc="best", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.show()


def yearly_histogram(df, year):

    year_df = df[df["Year"] == year]

    plt.figure()
    plt.hist(year_df["Value"])
    plt.title(f"GDP Histogram ({year})")
    plt.xlabel("GDP")
    plt.ylabel("Frequency")
    plt.show()


def yearly_scatter(df, year):

    year_df = df[df["Year"] == year]

    plt.figure()
    plt.scatter(year_df["Country Name"], year_df["Value"])
    plt.title(f"GDP Scatter Plot ({year})")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()