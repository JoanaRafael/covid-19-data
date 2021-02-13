import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
import vaxutils


def read(source: str) -> pd.Series:
    soup = BeautifulSoup(requests.get(source).content, "html.parser")
    table = soup.find(class_="geo-unit-vacc-doses-data__table")
    date = soup.find(class_="detail-card__source").find("span").text
    date = re.search(r"[\d\.]{10}", date).group(0)
    date = str(date)
    date = vaxutils.clean_date(date, "%d.%m.%Y")
    total_vaccinations = vaxutils.clean_count(pd.read_html(str(table))[0].loc[1]['absolute numbers'])
    return pd.Series([total_vaccinations], index=['total_vaccinations']).append(pd.Series([date], index=['date']))


def enrich_location(input: pd.Series) -> pd.Series:
    return vaxutils.enrich_data(input, 'location', "Switzerland")


def enrich_vaccine(input: pd.Series) -> pd.Series:
    return vaxutils.enrich_data(input, 'vaccine', "Moderna, Pfizer/BioNTech")


def enrich_source(input: pd.Series) -> pd.Series:
    return vaxutils.enrich_data(input, 'source_url',
                                "https://www.covid19.admin.ch/en/epidemiologic/vacc-doses?detGeo=CH")


def pipeline(input: pd.Series) -> pd.Series:
    return (
        input.pipe(enrich_location)
            .pipe(enrich_vaccine)
            .pipe(enrich_source)
    )


def main():
    source = "https://www.covid19.admin.ch/en/epidemiologic/vacc-doses?detGeo=CH"
    data = read(source).pipe(pipeline)
    vaxutils.increment(
        location=str(data['location']),
        total_vaccinations=int(data['total_vaccinations']),
        date=str(data['date']),
        source_url=str(data['source_url']),
        vaccine=str(data['vaccine'])
    )


if __name__ == "__main__":
    main()
