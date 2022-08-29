"""
Search a given <database> for a given <search term>.

Export file format is json.
Export log file with metadata about the search.
"""
import argparse
import json
from pathlib import Path
import time

from Bio import Entrez
from habanero import Crossref



parser = argparse.ArgumentParser()
parser.add_argument("-d", "--database", type=str, default="crossref")
    # required=True, help="Choose which database to search.", choices=["crossref", "pubmed"])
parser.add_argument("-q", "--query", type=str, default="lucid dreaming")
    # required=True, help="Choose the database search term.")
parser.add_argument("-l", "--limit", type=int, default=10)
args = parser.parse_args()

database = args.database
query = args.query
limit = args.limit


# Get a timestamp string of today to add to filename.
today = time.strftime("%Y%m%d")

export_dir = Path("./data")
export_stem =  f"db-{database}_query-{query}_date-{today}"
export_suffix = ".json"
export_path = export_dir / (export_stem+export_suffix)


if database == "crossref":

    # Initiate search object.
    cr = Crossref(
        base_url="https://api.crossref.org",
        api_key=None,
        mailto=None, # to get into Polite pool
        ua_string=None,
    )

    # Search database.
    results = cr.works(
        query=query,
        # filter={"has_full_text": True},
        # offset=None, # 1 to 10000, use if iterating beyond limit param?
        limit=limit, # 1000 max
        # select=["DOI", "title"],
        # cursor=None, cursor_max=5000, progress_bar=False, # use cursor for DEEP PAGING
    )

    # Export results as json file.
    with open(export_path, "w", encoding="utf-8") as fp:
        json.dump(results, fp, indent=4, ensure_ascii=True)


elif database == "pubmed":

    # ESummary (document summary downloads)

    # Set personal API keys.
    Entrez.email = "lenter360@gmail.com"

    # Search database.
    with Entrez.esearch(
            db=database,
            term=query,
            retmax=limit,
            retmode="xml",
        ) as handle:
        record = Entrez.read(handle)

    # Get DOIs, titles, etc.
    record_ids = record["IdList"]

    with Entrez.efetch(
        db=database,
        id=record_ids,
        retmode="xml",
        #rettype="abstract",
        ) as handle:
        # results = handle.read()
        results = Entrez.read(handle)

    # Export full search results.
    with open(export_path, "w", encoding="utf-8") as fp:
        json.dump(results, fp, indent=4, ensure_ascii=True)

    # Export record json, which has search parameters etc.
    export_path_metadata = export_path.with_stem(export_stem+"_metadata")
    with open(export_path_metadata, "w", encoding="utf-8") as fp:
        json.dump(record, fp, indent=4, ensure_ascii=True)
