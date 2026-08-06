from data.loaders.wikidata_loader import WikidataLoader
loader =WikidataLoader()

results = loader.fetch_companies(limit = 10)

for row in results["results"]["bindings"]:
    print(row["companyLabel"]["value"])