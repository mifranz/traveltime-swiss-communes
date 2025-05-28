# Swiss Travel Time Calculations

A GIS-based analysis for calculating car travel times between all Swiss municipalities and postal code zones using network centrality algorithms and openrouteservice.

## Overview

This project calculates approximately 18 million individual travel time computations between Swiss municipalities (\~2,000) and postal code zones (\~4,000) to quantify the concept of "local" for research on local business mergers.

## Methodology

Uses openrouteservice hosted locally via Docker Overcomes API limitations of commercial services like TravelTime. Python scripts handle API requests and data processing

Calculates the most central point within each zone's road network, by calculating the highest betweenness centrality value for each network. Ensures start/end points are always on actual roads. Better represents perceived community centers than geometric centroids

## Road Network Data

Uses swissTLM3D dataset with the following road categories: - Highways (Autobahn, Autostrasse) Various road widths (3m, 4m, 6m, 8m, 10m roads) - Access roads (Einfahrt, Ausfahrt, Zufahrt, Dienstzufahrt) - Connections and service areas

## Data Processing

Preprocessing: RStudio Network Analysis: Betweenness centrality calculation for each municipality/postal zone Routing: Local openrouteservice instance via Docker Exclusions: Unreachable areas, lakes, and Liechtenstein postal zones

## Requirements

-   Docker
-   Python 3.x
-   R/RStudio
-   openrouteservice Docker image
