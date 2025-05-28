import requests
import csv
import geopandas as gpd
import pandas as pd
from shapely import count_coordinates
from datetime import datetime
import os

# get timestamp
timestamp = datetime.today().strftime('%Y-%m-%d')
filename = f"data/matrices/durations_in_hours_{timestamp}.csv"

# Set up headers for the API request
api_key = '5b3ce3597851110001cf62489b315fb177cd4d208a60bd2b9bf7df0f'
headers = {
    'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    'Authorization': api_key,
    'Content-Type': 'application/json; charset=utf-8'
}

def calculate_travel_matrix(gpkg_path, output_csv, attribute):
    # Load the point data from the GeoPackage
    gdf = gpd.read_file(gpkg_path)

    filter_attribute = attribute
    # gdf[filter_attribute] = gdf[filter_attribute].astype(int)

    # gdf = gdf[(gdf[filter_attribute] < 8100) & (gdf[filter_attribute] > 8000)]
    # gdf = gdf[gdf[filter_attribute] < 160]
    #gdf = gdf[gdf[filter_attribute].isin(id_codes)]

    # check layer type
    if not gdf.geom_type.eq("Point").all():
        raise ValueError("GeoPackage does not contain only point geometries.")

    # Extract names and coordinates
    names = gdf[attribute].tolist()
    locations = [[geom.x, geom.y] for geom in gdf.geometry]

    # reversed coordinates as ORS uses lon/lat instead of lat/lon
    coord_labels = [f"{lat},{lon}" for lon, lat in locations]

    # Construct the JSON body for the API request
    body = {
        "locations": locations
    }
    # Send the request
    response = requests.post('http://localhost:8080/ors/v2/matrix/driving-car', json=body, headers=headers)

    # Check for a successful response
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        # print(response.text)
        # print(response)
        # return
    # Convert response to JSON
    response_json = response.json()

    # Extract durations (time in seconds)
    durations = response_json["durations"]

    # Convert seconds to minutes
    durations_in_minutes = [[round(duration / 60, 2) if duration is not None else "N/A" for duration in row] for row in durations]

    if not len(durations[0]) == len(durations_in_minutes[0]):
        print("problem with convertion of hours, script stopped")
        return


    # Write to CSV
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["From/To"]+ [""] + coord_labels)
        writer.writerow([""] + [""] + names)  # Header row

        for i, row in enumerate(durations_in_minutes):
            writer.writerow([coord_labels[i]]+ [names[i]] + row)

        # could be used for validating travel times
        #google_maps_link = f"https://www.google.ch/maps/dir/{start_coord}/{end_coord}"

    print(f"Duration matrix saved to {output_csv}")
def get_directions(gpkg_path, origin, destination, attribute):
    gdf = gpd.read_file(gpkg_path)

    filtered_gdf = gdf[gdf[attribute].isin([origin, destination])]


    locations = [[geom.x, geom.y] for geom in filtered_gdf.geometry]
    body = {"coordinates": [locations[0], locations[1]]}

    response = requests.post('http://localhost:8080/ors/v2/directions/driving-car/geojson', json=body,
                         headers=headers)
    response_json = response.json()
    print(response_json)

    gdf = gpd.GeoDataFrame.from_features(response_json["features"],crs="EPSG:4326")
    gdf['duration_min'] = gdf["summary"][0]['duration'] / 60
    gdf['distance_km'] = gdf["summary"][0]['distance'] / 1000

    gdf = gdf.drop(columns=['segments', 'way_points', 'summary'])

    gdf.to_file(f"data/id_{origin}_to_{destination}.gpkg", driver="GPKG")
    print(f"plzID_{origin}_to_{destination}.gpkg")
    return
def bundle_segments(matrix):
    df = pd.read_csv(matrix, header=None)
    origin_coords = df.iloc[2:, 0].to_list()  # First column: origin coordinates
    origin_ids = df.iloc[2:, 1].to_list()  # Second column: origin IDs
    destinations_coords = df.iloc[0, 2:].to_list()  # First row: destination coordinates
    destination_ids = df.iloc[1, 2:].to_list()

    all_route_segments = []  # List to store all route data
    for i, origin in enumerate(origin_coords):
        origin_id = origin_ids[i]
        for j, destination in enumerate(destinations_coords):
            if i != j:  # Avoid self-loops
                time = df.iloc[i + 2, j + 2]
                coords = [[origin_coords[i]], [destinations_coords[j]]]
                swapped_coords = [[float(coord[0].split(',')[1]), float(coord[0].split(',')[0])] for coord in coords]

                body = {"coordinates": swapped_coords}
                response = requests.post('http://localhost:8080/ors/v2/directions/driving-car/geojson', json=body,
                                         headers=headers)

                response_json = response.json()
                gdf = gpd.GeoDataFrame.from_features(response_json["features"], crs="EPSG:4326")

                # Add identifiers
                gdf['origin'] = origin_id
                gdf['destination'] = destination_ids[j]
                gdf['distance_km'] = gdf["summary"][0]['distance'] / 1000
                gdf['duration_matrix'] = float(time)

                # Remove unnecessary columns
                gdf = gdf.drop(columns=['segments', 'way_points', 'summary'])

                all_route_segments.append(gdf)

    # Save all routes in a single GPKG layer
    if all_route_segments:
        combined_gdf = gpd.GeoDataFrame(pd.concat(all_route_segments, ignore_index=True), crs="EPSG:4326")
        #combined_gdf = combined_gdf.drop(columns=['warnings', 'extras'])
        combined_gdf = combined_gdf.drop_duplicates(subset=['distance_km'])
        combined_gdf.to_file("data/routes/matrix_as_route.gpkg", layer="routes", driver="GPKG")
        print(f"Saved all {len(all_route_segments)} routes in a single layer in matrix_as_route.gpkg")

# subset to test matrix
id_codes = [3825, 8002, 3826, 8003, 8006]

calculate_travel_matrix("data/input/plz_centers_wgs84.gpkg", filename, "ZIP4")

#09:23


# origin/destination for individual route calculations
origin = 2767
destination = 6300
# get_directions("data/input/gemeinden_centers_wgs84.gpkg", origin,destination, "bfs_nummer")

# calculate and save all routes of a matrice as gpkg
#bundle_segments(filename)

