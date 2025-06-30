# Swiss Travel Time Calculations

A GIS-based analysis for calculating car travel times between all Swiss municipalities and postal code zones using network centrality algorithms and openrouteservice.

## Overview

Calculation of approximately 18 million individual travel time 
computations between Swiss municipalities (\~2,000) and postal code zones 
(\~4,000) to quantify the concept of "local" for research on effects of local 
business mergers, meaning up to what travel time by car can a zone be considered
as "local".

## Methodology

Uses openrouteservice hosted locally via Docker to overcome API limitations.
Python scripts handle API requests and data processing.

Calculates the most central point within each zone's road network, by 
calculating the highest betweenness centrality value for each network. 
Ensures start/end points are always on actual roads. Better represents 
perceived community centers than geometric centroids. Excludes some communes
and zones (unreachable, lakes etc.)
The result is a origin destination matrix as csv containing the bfs_number/zip code
and the start/end coordinates.

## Data Sources
The data used in this project is provided by the Federal Office of Topography swisstopo.
©swisstopo

swissTLM3D dataset with the following road categories:

-   Highways (Autobahn, Autostrasse) Various road widths (3m, 4m, 6m, 8m, 10m roads) 
-   Access roads (Einfahrt, Ausfahrt, Zufahrt, Dienstzufahrt) 
-   Connections and service areas

swissBOUNDARIES3D:
-   tlm_landesgebiet
-   tlm_hoheitsgebiet

Amtliches Ortschaftenverzeichnis
-   AMTOVZ_ZIP

## Data Processing

Preprocessing: 
- RStudio  
    - Network Analysis: Betweenness centrality calculation for each municipality/postal zone.  
    - Exclusions: Unreachable areas, lakes, and Liechtenstein postal zones.  
    
Routing Configuration

Routing was performed using a local Docker instance of [openrouteservice](https://github.com/GIScience/openrouteservice) 

The following settings were used in the ORS config (`ors-config.yml`):

- `source_file`: `switzerland-latest.osm.pbf`
- `min_network_size`: 200
- `maximum_distance`: 1,000,000
- `maximum_snapping_radius`: 8,000
- `maximum_routes` (matrix): 20,000,000
- `maximum_visited_nodes` (matrix): 1,000,000,000
- `maximum_search_radius` (matrix): 1,500
- Enabled profile: `driving-car`

## Requirements

-   Docker
-   Python 3.x
-   R/RStudio
-   openrouteservice Docker image

Note: This project was part of a small task. It's not intended for reuse, but published here to document the workflow and share data.
