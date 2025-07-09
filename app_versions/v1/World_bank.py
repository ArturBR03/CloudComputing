import requests
import csv
import time


indicators = {
    "gdp": "NY.GDP.MKTP.CD",
}


BASE_URL = "http://api.worldbank.org/v2/country/all/indicator/{}?format=json&per_page=1000"


data = {}
country_names = {}  

def fetch_indicator(indicator_key, indicator_code):
    print(f"Lade Daten für {indicator_key.upper()} ...")
    page = 1
    results = {}

    while True:
        url = BASE_URL.format(indicator_code) + f"&page={page}"
        res = requests.get(url)
        if res.status_code != 200:
            print(f"Failed to fetehc page {page}")
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
        time.sleep(0.2)

    return results

for key, code in indicators.items():
    result = fetch_indicator(key, code)
    for country, years in result.items():
        if country not in data:
            data[country] = {}
        for year, value in years.items():
            if year not in data[country]:
                data[country][year] = {}
            data[country][year][key] = value

with open("world_data.csv", "w", newline='', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["country", "year", "gdp"])

    for code, years in data.items():
        country_name = country_names.get(code, code)
        for year in sorted(years.keys(), reverse=True):
            row = years[year]
            gdp = row.get("gdp")
            if gdp is not None:
                writer.writerow([country_name, year, gdp])

print("CSV-Datei 'world_data.csv' erfolgreich mit Ländernamen erstellt.")
