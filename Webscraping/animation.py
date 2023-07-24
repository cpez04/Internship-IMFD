import folium
from folium.plugins import HeatMap
import time
import pandas as pd
import os
from selenium import webdriver
from moviepy.editor import ImageSequenceClip
from PIL import Image 


def resize_image(image_path, target_size):
    image = Image.open(image_path)
    resized_image = image.resize(target_size, Image.LANCZOS)
    return resized_image

# Creates an animated heat map of the crime data (GIF format)
def create_base_map(csv_file):
    # Read the sorted CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Convert 'fecha' column to datetime type
    df['fecha'] = pd.to_datetime(df['fecha'])

    # Group the data into 7-day increments (weekly)
    df['week'] = df['fecha'].dt.to_period('W').dt.start_time

    # Get unique weeks from the DataFrame
    unique_weeks = df['week'].unique()

    # Create a map centered on a specific location
    latitude, longitude = df['y'].mean(), df['x'].mean()

    # Create the base map
    crime_map = folium.Map(location=[latitude, longitude], zoom_start=11.6)

    # Create an empty HeatMap layer
    heatmap_layer = HeatMap([], radius=10, blur=5)

    # Add the HeatMap layer to the map
    heatmap_layer.add_to(crime_map)

    return crime_map, heatmap_layer, df, unique_weeks


def update_heatmap(crime_map, heatmap_layer, df, week):
    # Filter the DataFrame for the selected week
    filtered_df = df[df['week'] == week]

    # Create a list of latitudes and longitudes for the heat map data for the selected week
    heat_data = [[row['y'], row['x']] for _, row in filtered_df.iterrows()]

    # Update the data in the HeatMap layer
    heatmap_layer.data = heat_data

def plot_weekly_heatmap(crime_map, heatmap_layer, df, unique_weeks):
    
    # Set a consistent window size for the browser
    browser_width, browser_height = 1200, 800
    
    # Create a directory to save frames
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
    for i, week in enumerate(sorted(unique_weeks)):
        update_heatmap(crime_map, heatmap_layer, df, week)
        
        # Save the map as an HTML file
        html_file = f'map_{i}.html'
        crime_map.save(html_file)

        # Open the map in the browser and take a screenshot
        driver.get(f'file://{os.path.abspath(html_file)}')
        png_file = f'frames/frame_{i}.png'
        filenames.append(png_file)
        #Add a slight delay
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
         # Resize the images to the dimensions of the first image
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
       
        
    
filename = 'data_homicides_2.csv'  # Replace with the actual filename of the sorted CSV file
crime_map, heatmap_layer, df, unique_weeks = create_base_map(filename)
plot_weekly_heatmap(crime_map, heatmap_layer, df, unique_weeks)