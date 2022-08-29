"""
Search a given <database> for a given <search term>.

Export file format depends on the database (e.g., json for CrossRef, xml for PubMed).
Export log file with metadata about the search.
"""
import argparse
import json
from pathlib import Path
import time

from habanero import Crossref


parser = argparse.ArgumentParser()
parser.add_argument("-d", "--database", type=str, default="crossref")
    # required=True, help="Choose which database to search.", choices=["crossref", "pubmed"])
parser.add_argument("-q", "--query", type=str, default="lucid dreaming")
    # required=True, help="Choose the database search term.")
args = parser.parse_args()

database = args.database
query = args.query


# Get a timestamp string of today to add to filename.
today = time.strftime("%Y%M%d")

extensions = {
    "crossref": ".json",
    "pubmed": ".xml",
}
export_dir = Path("./data")
export_path = (export_dir / f"db-{database}_query-{query}_date-{today}").with_suffix(extensions[database])




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
        limit=20, # 1000 max
        # select=["DOI", "title"],
        # cursor=None, cursor_max=5000, progress_bar=False, # use cursor for DEEP PAGING
    )

    # Export results as json file.
    with open(export_path, "w", encoding="utf-8") as fp:
        json.dump(results, fp, indent=4, ensure_ascii=True)
