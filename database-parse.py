"""Parse raw output from search_database file.

Every database will provide varying information and in different formats,
so these functions get them all into pandas dataframes.
"""
import argparse
import json
from pathlib import Path

import pandas as pd


parser = argparse.ArgumentParser()
parser.add_argument("-d", "--database", type=str, default="crossref")
    # required=True, help="Choose which database to search.", choices=["crossref", "pubmed"])
parser.add_argument("-q", "--query", type=str, default="lucid dreaming")
    # required=True, help="Choose the database search term.")
args = parser.parse_args()

database = args.database
query = args.query


import_dir = Path("./data")
import_paths = list(import_dir.glob(f"db-{database}_query-*"))
if database == "crossref":
    assert len(import_paths) == 1
    import_path = import_paths[0]
elif database == "pubmed":
    assert len(import_paths) == 2
    import_path, metadata_path = sorted(import_paths)

with open(import_path, "r", encoding="utf-8") as fp:
    data = json.load(fp)

    if database == "crossref":
        results_list =  data["message"]["items"]
        df = pd.DataFrame.from_records(results_list, columns=["DOI", "title"])
        df["title"] = df["title"].str[0]
        ser = df.set_index("DOI").squeeze("columns")

    elif database == "pubmed":
        results_list =  data["PubmedArticle"]
        records = []
        for r in results_list:
            article_info = {}
            title = r["MedlineCitation"]["Article"]["ArticleTitle"]
            abstract = r["MedlineCitation"]["Article"]["Abstract"]["AbstractText"]
            article_ids = r["PubmedData"]["ArticleIdList"]
            for id_ in article_ids:
                if id_.startswith("10.") and id_.count("/") > 0:
                    break
            article_info = dict(doi=id_, title=title, abstract=abstract)
            records.append(article_info)
            
        df = pd.DataFrame.from_records(records, index="doi")