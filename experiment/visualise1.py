import pandas as pd
import geopandas as gpd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium
import json
import webbrowser


def generate_disaster_map(data, layer_title, tags, user_agent="map_app"):
    # Function to geocode location data
    def geocode_locations(df, location_column):
        geolocator = Nominatim(user_agent=user_agent)
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

        def get_location(row):
            location_query = f"{row[location_column]}, Nepal"
            try:
                location = geocode(location_query)
                return (
                    (location.latitude, location.longitude)
                    if location
                    else (None, None)
                )
            except Exception as e:
                print(f"Error in geocoding {location_query}: {e}")
                return (None, None)

        df["latitude"], df["longitude"] = zip(*df.apply(get_location, axis=1))
        df.dropna(subset=["latitude", "longitude"], inplace=True)
        return df

    # Function to prepare GeoDataFrame
    def prepare_gdf(df):
        if not df.empty:
            gdf = gpd.GeoDataFrame(
                df,
                geometry=gpd.points_from_xy(df.longitude, df.latitude),
            )
            return gdf
        else:
            print("Processed DataFrame is empty after dropping NaNs.")
            return None

    # Process data and create GeoJSON
    df = pd.DataFrame([data])
    processed_df = geocode_locations(df, "location")
    if processed_df is not None and not processed_df.empty:
        gdf = prepare_gdf(processed_df)
        if gdf is not None:
            geojson_file = f"{layer_title}.geojson"
            gdf.to_file(geojson_file, driver="GeoJSON")
            print(f"GeoJSON file '{geojson_file}' is ready for upload.")
        else:
            print("GeoDataFrame creation failed.")
            return
    else:
        print("Geocode failed or resulted in empty DataFrame.")
        return

    # Load GeoJSON and create the map
    with open(geojson_file, "r") as f:
        geojson_data = json.load(f)

    map_center = [27.7172, 85.3240]  # Coordinates for Kathmandu, Nepal
    result_map = folium.Map(location=map_center, zoom_start=7, tiles="OpenStreetMap")

    # Define color for each hazard type
    hazard_colors = {
        "landslide": "black",
        "flood": "blue",
        "earthquake": "green",
        "fire": "orange",
        "drought": "yellow",
    }

    # Add markers to the map
    for feature in geojson_data["features"]:
        hazard_type = feature["properties"].get("hazard_type", "Unknown")
        date = feature["properties"].get("date", "Unknown date")
        location = feature["properties"].get("location", "Unknown location")
        tooltip_text = (
            f"  Disaster Type: {hazard_type}<br>Date: {date}<br>Location: {location}"
        )
        color = hazard_colors.get(hazard_type.lower(), "gray")
        coordinates = feature["geometry"]["coordinates"]
        folium.CircleMarker(
            location=[coordinates[1], coordinates[0]],  # Flip coordinates
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            tooltip=tooltip_text,
        ).add_to(result_map)

    return result_map

    # # Save the map to an HTML file and open it in a web browser
    # html_file = "output_map.html"
    # result_map.save(html_file)
    # webbrowser.open(html_file, new=2)


# # Example usage of the function
# data = {"location": "Sindhupalchowk", "hazard_type": "landslide", "date": "2024-04-20"}
# generate_disaster_map(data, "Disaster Layer", "Disaster Data")
