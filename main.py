import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


data_file = Path("data") / "wildlife.csv"
print("UK Wildlife Data Project")
print(f"Dataset location: {data_file}")

wildlife = pd.read_csv(data_file, encoding="cp1252")
print(f"Number of rows: {len(wildlife)}")
print("\nColumn names:")
print(wildlife.columns.tolist())

columns_to_view = [
    "SITENAME",
    "COUNTRY",
    "LAY_TITLE",
    "COUNT",
    "UNITS",
    "YEAR"
]

print("\nFirst five bird records:")
print(wildlife[columns_to_view].head().to_string(index=False))

wildlife["COUNT_NUMERIC"] = pd.to_numeric(
    wildlife["COUNT"].str.replace(",", "", regex=False),
    errors="coerce"
)

print("\nCleaned count type:")
print(wildlife["COUNT_NUMERIC"].dtype)

print("\nMissing numeric counts:")
print(wildlife["COUNT_NUMERIC"].isna().sum())

bird_names = wildlife["LAY_TITLE"]
contains_assemblage = bird_names.str.contains("assemblage")
print("\n Assemblage records", contains_assemblage.sum())

individual_species = wildlife[~contains_assemblage]
print("\n Individual species", len(individual_species))

largest_records = individual_species.nlargest(5, "COUNT_NUMERIC")
print("\n Largest records",(largest_records[["LAY_TITLE", "SITENAME", "COUNT_NUMERIC", "UNITS", "YEAR" ]].to_string(index=False)))

chart_labels = largest_records["LAY_TITLE"].str.strip() + " at " + largest_records["SITENAME"].str.strip()
plt.figure(figsize =(12, 6))
plt.barh(chart_labels, largest_records["COUNT_NUMERIC"])
plt.title("Five Largest Individual Bird Records at UK Ramsar Sites")
plt.xlabel("Recorded number of individual birds")
plt.tight_layout()
plt.savefig("output/largest_bird_records.png", dpi=300, bbox_inches="tight")
plt.close()

species_per_site = individual_species.groupby("SITENAME")["LAY_TITLE"].nunique()
top_sites = species_per_site.nlargest(5)
print("\nTop 5 sites:")
print(top_sites)

plt.figure(figsize =(10, 6))
plt.barh(top_sites.index, top_sites.values)
plt.title("Ramsar sites with the most qualifying bird species")
plt.xlabel("Number of distinct qualifying bird species")
plt.tight_layout()
plt.savefig("output/top_ramsar_sites.png", dpi=300, bbox_inches="tight")
plt.close()

site_summary = individual_species.groupby("SITENAME").agg(
    species_count=("LAY_TITLE", "nunique"),
    x_coordinate=("X_COORDINATE", "first"),
    y_coordinate=("Y_COORDINATE", "first"),
).reset_index()
print("\nMissing site-summary values:")
print(site_summary.isna().sum())

plt.figure(figsize =(8, 10))
site_points= plt.scatter(
    site_summary["x_coordinate"],
    site_summary["y_coordinate"],
    c=site_summary["species_count"],
    cmap="viridis",
    s=60
)
colour_key = plt.colorbar(site_points)
colour_key.set_label("Number of distinct qualifying bird species")
plt.title("UK ramsar sites qualifying bird species")
plt.xlabel("British national grid easting")
plt.ylabel("British national grid northing")
label_offsets = {"North Norfolk Coast": (-5, 8), "The Wash": (-5, -10)}
for site_name in top_sites.index:
    site_row = site_summary[site_summary["SITENAME"] == site_name].iloc[0]
    plt.annotate(
        site_name,
        (site_row['x_coordinate'], site_row['y_coordinate']),
        xytext=label_offsets.get(site_name, (-5, 5)),
        textcoords="offset points",
        fontsize=7,
        ha="right",
)
plt.tight_layout()
plt.savefig("output/ramsar_site_locations.png", dpi=300, bbox_inches="tight")
plt.close()
