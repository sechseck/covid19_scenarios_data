import sys
import requests
import csv
import io

from collections import defaultdict
from .utils import write_tsv, store_json, list_to_dict

# ------------------------------------------------------------------------
# Globals

cantonal_codes = {
   "ZH": "Zürich",
   "BE": "Bern",
   "LU": "Luzern",
   "UR": "Uri",
   "SZ": "Schwyz",
   "OW": "Obwalden",
   "NW": "Nidwalden",
   "GL": "Glarus",
   "ZG": "Zug",
   "FR": "Fribourg",
   "SO": "Solothurn",
   "BS": "Basel-Stadt",
   "BL": "Basel-Landschaft",
   "SH": "Schaffhausen",
   "AR": "Appenzell Ausserrhoden",
   "AI": "Appenzell Innerrhoden",
   "SG": "St. Gallen",
   "GR": "Graubünden",
   "AG": "Aargau",
   "TG": "Thurgau",
   "TI": "Ticino",
   "VD": "Vaud",
   "VS": "Valais",
   "NE": "Neuchâtel",
   "GE": "Geneva",
   "JU": "Jura",
   "FL": "Liechtenstein",
   "CH": "Switzerland",
}

URL  = "https://raw.github.com/openZH/covid_19/master/COVID19_Cases_Cantons_CH_total.csv"
LOC  = "case-counts/Europe/Western Europe/Switzerland"
LOC2 = "case-counts/Europe/Western Europe/Liechtenstein"
cols = ['time', 'cases', 'deaths', 'hospitalized', 'ICU', 'recovered']

# ------------------------------------------------------------------------
# Functions

def to_int(x):
    if x == "NA" or x == "":
        return None
    else:
        return int(x)

# ------------------------------------------------------------------------
# Main point of entry

def parse():
    r  = requests.get(URL)
    if not r.ok:
        print(f"Failed to fetch {URL}", file=sys.stderr)
        exit(1)
        r.close()

    regions = defaultdict(list)
    fd  = io.StringIO(r.text)
    rdr = csv.reader(fd)
    hdr = next(rdr)

    for row in rdr:
        date   = row[0]
        canton = cantonal_codes[row[1]]
        regions[canton].append([date, to_int(row[2]), to_int(row[5]), to_int(row[6]), None, to_int(row[7])])

    for region, data in regions.items():
        if region != "Liechtenstein":
            write_tsv(f"{LOC}/{region}.tsv", cols, data, "switzerland")
        else:
            write_tsv(f"{LOC2}/{region}.tsv", cols, data, "switzerland")

    # prepare dict for json
    regions2 = {}
    for region, data in regions.items():
        if not ((region == "Liechtenstein") or (region == "Switzerland")):
            regions2["CHE-"+region] = data
        else:
            regions2[region] = data
        
    regions3 = list_to_dict(regions2, cols)
    store_json(regions3)
