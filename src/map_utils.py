import folium
import pandas as pd
import geopandas as gpd

def make_choropleth(ward_geojson_path: str, ward_population_csv: str, counts_csv: str, year: int, out_html: str):
    """Create a ward-level choropleth of requests per 10k residents for a given year."""
    wards = gpd.read_file(ward_geojson_path)  # must include ward name/number field
    pop = pd.read_csv(ward_population_csv)    # columns: ward_number, population
    counts = pd.read_csv(counts_csv)          # tidy counts with columns: year,type,division,ward,n

    # Extract ward number from 'ward' text, assume format 'Ward Name, Ward Number'
    counts_year = counts[counts['year'] == year].copy()
    counts_year['ward_number'] = counts_year['ward'].str.extract(r'(\d+)$').astype(float)

    ward_totals = counts_year.groupby('ward_number', as_index=False)['n'].sum()
    ward_totals = ward_totals.merge(pop, on='ward_number', how='left')
    ward_totals['per_10k'] = (ward_totals['n'] / ward_totals['population']) * 10000

    # Merge onto wards GeoDataFrame (ensure compatible key)
    if 'ward_number' not in wards.columns:
        # try to coerce from a field like 'WARD_NUM' or similar
        for c in wards.columns:
            if 'ward' in c.lower() and 'num' in c.lower():
                wards = wards.rename(columns={c: 'ward_number'})
                break

    wards = wards.merge(ward_totals[['ward_number','per_10k','n']], on='ward_number', how='left')

    # Center over Toronto roughly
    m = folium.Map(location=[43.7, -79.4], zoom_start=10, tiles='cartodbpositron')
    folium.Choropleth(
        geo_data=wards.to_json(),
        data=wards,
        columns=['ward_number','per_10k'],
        key_on='feature.properties.ward_number',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f'Requests per 10k residents ({year})'
    ).add_to(m)

    folium.LayerControl().add_to(m)
    m.save(out_html)
    return out_html
