import os
import time 
from datetime import timedelta


import folium
from folium.plugins import HeatMap
import pandas as pd
from selenium import webdriver
from moviepy.editor import ImageSequenceClip
from PIL import Image 
import tkinter as tk
from tkinter import filedialog


def resize_image(image_path, target_size):
    # If image is not the same size as the target, resize it
    image = Image.open(image_path)
    resized_image = image.resize(target_size, Image.LANCZOS)
    return resized_image

def create_base_map(csv_file):
    # Read the sorted CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)
    
    # Check if the CSV file contains the required columns
    if not all(col in df.columns for col in ['x', 'y', 'fecha', 'hora', 'delito']):
        raise Exception("The CSV file must contain, at least, the following column headers: x, y, fecha, hora, delito")
     
    # Convert 'fecha' column to datetime type
    df['fecha'] = pd.to_datetime(df['fecha'])

    # Find the minimum and maximum dates in the DataFrame
    min_date = df['fecha'].min()
    max_date = df['fecha'].max()

    # Create a list of all the weeks in the DataFrame
    all_weeks = pd.date_range(start=min_date - timedelta(days=min_date.weekday()), end=max_date + timedelta(days=6-max_date.weekday()), freq='W')

    # Create a map centered on a specific location
    latitude, longitude = df['y'].mean(), df['x'].mean()
    
     # Group the data into 7-day increments (weekly) and create the 'week' column
    df['week'] = df['fecha'].dt.to_period('W').dt.start_time

    # Create the base map
    crime_map = folium.Map(location=[latitude, longitude], zoom_start=11.3)

    # Create an empty HeatMap layer
    heatmap_layer = HeatMap([], radius=10, blur=5)

    # Add the HeatMap layer to the map
    heatmap_layer.add_to(crime_map)

    return crime_map, heatmap_layer, df, all_weeks

def update_heatmap(crime_map, heatmap_layer, df, week):
    # Convert the week to the correct format used in the DataFrame
    start_date = week.strftime('%Y-%m-%d')
    end_date = (week + pd.DateOffset(days=6)).strftime('%Y-%m-%d')

    # Filter the DataFrame for the selected week
    filtered_df = df[(df['fecha'] >= start_date) & (df['fecha'] <= end_date)]

    # Create a list of latitudes and longitudes for the heat map data for the selected week
    heat_data = [[row['y'], row['x']] for _, row in filtered_df.iterrows()]

    # Update the data in the HeatMap layer
    heatmap_layer.data = heat_data

def plot_weekly_heatmap(crime_map, heatmap_layer, df, all_weeks, title):
    
    # Set a consistent window size for the browser
    browser_width, browser_height = 1200, 800
    
    # Create a directory to save frames. If it already exists, delete all the files inside
    if not os.path.exists('frames'):
        os.makedirs('frames')
    else:
        for filename in os.listdir('frames'):
            os.remove(f'frames/{filename}')

    filenames = []

    # Set up a Selenium WebDriver for Chrome with the desired window size
    options = webdriver.ChromeOptions()
    options.add_argument(f'--window-size={browser_width},{browser_height}')
    driver = webdriver.Chrome(options=options)
    
     
    # Iterate over each week to create the animation-like effect
    for i, week in enumerate(all_weeks):
        update_heatmap(crime_map, heatmap_layer, df, week)

        # Calculate the start and end dates for the week to include in the title
        start_date = week.strftime('%Y-%m-%d')
        end_date = (week + pd.DateOffset(days=6)).strftime('%Y-%m-%d')

    
        title_html = f'''
                     <h3 align="center" style="font-size:16px"><b>{title}</b></h3>
                     <p align="center" style="font-size:14px"><b>{start_date} - {end_date}</b></p>
                     '''   
        crime_map.get_root().html.add_child(folium.Element(title_html))

        # Save the map as an HTML file
        html_file = f'map_{i}.html'
        crime_map.save(html_file)

        # Open the map in the browser and take a screenshot
        driver.get(f'file://{os.path.abspath(html_file)}')
        png_file = f'frames/frame_{i}.png'
        filenames.append(png_file)

        # Add a slight delay to avoid whitewashed/blank images
        time.sleep(.13)
        driver.save_screenshot(png_file)

        # Now delete the HTML file to avoid cluttering up the directory
        os.remove(html_file)

    driver.quit()
    
    try:
        # Create a GIF animation from the saved frames
        clip = ImageSequenceClip(filenames, fps=5)
        clip.write_videofile('animation.mp4', codec='libx264')
    except: 
        print("Error creating animation. Resizing images...")
        first_image = Image.open(filenames[0])
        image_size = first_image.size

        for filename in filenames:
            resized_image = resize_image(filename, image_size)
            resized_image.save(filename)
        print("Images succesfully resized!") 
        
        clip = ImageSequenceClip(filenames, fps=5)
        clip.write_videofile('animation.mp4', codec='libx264')
        
    print("Animation created successfully!")
    
    print("Would you like to delete all the frame? (y/n)")
    if input() == 'y':
        for filename in os.listdir('frames'):
            os.remove(f'frames/{filename}')
        print("All frames deleted successfully!")
       
        
def select_csv_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV files", "*.csv")])

    if file_path:
        return file_path
    else:
        print("No file selected.")
        return None
    

if __name__ == "__main__":
    filename = select_csv_file()
    if filename:
        # Can change title depending on context. 
        title = 'Homicides in Santiago, Chile' 
        crime_map, heatmap_layer, df, unique_weeks = create_base_map(filename)
        plot_weekly_heatmap(crime_map, heatmap_layer, df, unique_weeks, title)