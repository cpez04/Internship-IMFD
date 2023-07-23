import csv
import folium
from folium.plugins import HeatMap
from IPython.display import display
import pandas as pd
import os


# pre-process the delitos dataset
def sort_csv_file(filename):
    base_name, ext = os.path.splitext(filename)
    output_filename = f'{base_name}_sorted{ext}'

    with open(filename, 'r', newline='') as file:
        reader = csv.DictReader(file)
        sorted_rows = sorted(reader, key=lambda row: (row['fecha'], row['hora']))

    # Write the sorted rows to a new CSV file with the modified filename
    with open(output_filename, 'w', newline='') as output_file:
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_rows)


def plot_crime_heatmap(csv_file):
    # Read the sorted CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Create a map centered on a specific location
    latitude, longitude = df['y'].mean(), df['x'].mean()
    crime_map = folium.Map(location=[latitude, longitude], zoom_start=12)

    # Create a list of latitudes and longitudes for the heat map data
    heat_data = [[row['y'], row['x']] for _, row in df.iterrows()]

    # Add the heat map layer to the map with adjusted radius and blur
    HeatMap(heat_data, radius=10, blur=5).add_to(crime_map)

     # Display the map in a separate window
    display(crime_map)
    
# Example usage
filename = 'data_homicides_sorted.csv'  # Replace with the actual filename of the sorted CSV file
plot_crime_heatmap(filename)
