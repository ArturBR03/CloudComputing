import csv
import requests


def write_gdp_csv(
    path: str,
    indicator_key="gdp",
    indicator_code="NY.GDP.MKTP.CD",
    BASE_URL="http://api.worldbank.org/v2/country/all/indicator/{}?format=json&per_page=1000",
):
    """
    A special function to create a csv file with the actual
    gdp of every country, supported by the given API

    Params:
        path (str): path plus name of the csv file
        indicator_key (str): key to hand over which type of data you want to extract
        indicator_code (str): codes to hand over which type of data you want to extract
        BASE_URL (str): the given API to extract BIP information

    Returns:
        None
    """

    page = 1
    results = {}
    data = {}
    country_names = {}

    while True:
        url = BASE_URL.format(indicator_code) + f"&page={page}"
        res = requests.get(url)
        if res.status_code != 200:
            print(f"Failed to fetch page {page}")
            break

        json_data = res.json()

        if len(json_data) < 2 or not isinstance(json_data[1], list):
            break

        for entry in json_data[1]:
            code = entry["country"]["id"]
            name = entry["country"]["value"]
            year = entry["date"]
            value = entry["value"]

            if year is None or value is None:
                continue

            # Ländercode → Name speichern
            country_names[code] = name

            if code not in results:
                results[code] = {}
            results[code][year] = value

        if page >= json_data[0]["pages"]:
            break

        page += 1

    for country, years in results.items():
        if country not in data:
            data[country] = {}
        for year, value in years.items():
            if year not in data[country]:
                data[country][year] = {}
            data[country][year][indicator_key] = value

    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["country", "year", "gdp"])

        for code, years in data.items():
            country_name = country_names.get(code, code)
            for year in sorted(years.keys(), reverse=True):
                row = years[year]
                gdp = row.get("gdp")
                if gdp is not None:
                    writer.writerow([country_name, year, gdp])
