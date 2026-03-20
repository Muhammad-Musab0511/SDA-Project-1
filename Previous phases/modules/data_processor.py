def filter_dataset(df, region, year):

    filtered = df[(df["Region"] == region) & (df["Year"] == year)]

    return filtered


def compute_statistic(filtered_df, operation):

    values = list(map(lambda x: x, filtered_df["Value"]))

    if len(values) == 0:
        raise Exception("No matching data found")

    if operation == "average":
        return sum(values) / len(values)

    if operation == "sum":
        return sum(values)

    raise Exception("Invalid operation")
