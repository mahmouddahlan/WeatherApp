import tkinter as tk
from tkinter import ttk, messagebox, font
import requests
import sqlite3
from datetime import datetime

# Database setup
conn = sqlite3.connect('weather_app.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS favorite_locations (id INTEGER PRIMARY KEY, city TEXT UNIQUE, temperature TEXT)''')
conn.commit()

API_KEY = "06c921750b9a82d8f5d1294e1586276f"  # Replace with your actual API key

# Function to get detailed location info using the Geocoding API
def get_location_details(city):
    try:
        geo_api_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        response = requests.get(geo_api_url)
        if response.status_code == 200:
            location_data = response.json()
            if location_data:
                city_name = location_data[0]['name']
                country = location_data[0]['country']
                state = location_data[0].get('state', '')
                return city_name, state, country
            else:
                raise Exception("Location not found")
        else:
            raise Exception("Error fetching location details")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None, None, None
    
    
def get_7_day_forecast(lat, lon):
    try:
        one_call_api_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&appid={API_KEY}"
        response = requests.get(one_call_api_url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Error fetching forecast data")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None


# Display the 7-day forecast
def display_7_day_forecast(city):
    city_name, state, country, lat, lon = get_location_details(city)
    if not lat or not lon:
        return

    forecast_data = get_7_day_forecast(lat, lon)
    if forecast_data:
        forecast_label_5_day.config(text="")  # Clear previous data
        
        daily_forecast = forecast_data['daily']  # Get the daily forecast data
        
        display_text = "7-Day Forecast:\n"
        
        for day_data in daily_forecast[:7]:  # Ensure it iterates through all 7 days
            day = datetime.fromtimestamp(day_data['dt']).strftime('%A')
            high_temp = round(day_data['temp']['max'] - 273.15)  # Convert from Kelvin to Celsius
            low_temp = round(day_data['temp']['min'] - 273.15)   # Convert from Kelvin to Celsius
            display_text += f"{day}: H: {high_temp}°C  L: {low_temp}°C\n"
        
        forecast_label_5_day.config(text=display_text)


# Add to favorites function
def add_to_favorites():
    city = textField.get().strip()
    if not city:
        messagebox.showwarning("Input Error", "Please enter a city name")
        return

    city_name, state, country = get_location_details(city)
    if not city_name:
        return

    weather_data = get_weather(city)
    if weather_data:
        temp = int(weather_data['main']['temp'] - 273.15)  # Convert temperature to Celsius
        # Format the location with temperature
        if state:
            full_location = f"{city_name.title()}, {state.title()}, {country} - {temp}°C"
        else:
            full_location = f"{city_name.title()}, {country} - {temp}°C"

        # Check if the city is already in favorites
        try:
            c.execute("INSERT INTO favorite_locations (city, temperature) VALUES (?, ?)", (full_location, f"{temp}°C"))
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showinfo("Already Exists", f"{full_location} is already in your favorites.")
            return
        
        # Update the favorites listbox
        favorite_listbox.insert(tk.END, full_location)
        messagebox.showinfo("Success", f"{full_location} added to favorites")

# Remove from favorites function
def remove_from_favorites():
    selected_index = favorite_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("Selection Error", "Please select a location to remove")
        return

    selected_city = favorite_listbox.get(selected_index)

    # Remove from the database
    try:
        c.execute("DELETE FROM favorite_locations WHERE city = ?", (selected_city,))
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        return

    # Remove from the listbox
    favorite_listbox.delete(selected_index)
    messagebox.showinfo("Success", f"{selected_city} removed from favorites")

# Fetch weather data
def get_weather(city):
    try:
        api_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("City not found or API error")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None

# Function to fetch the 5-day forecast data
def get_5_day_forecast(city):
    try:
        forecast_api_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}"
        response = requests.get(forecast_api_url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("City not found or API error")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None

# Display the 5-day forecast vertically
def display_5_day_forecast(city):
    forecast_data = get_5_day_forecast(city)
    if forecast_data:
        forecast_label_5_day.config(text="")  # Clear previous data
        
        daily_forecast = {}
        for entry in forecast_data['list']:
            date_text = datetime.utcfromtimestamp(entry['dt'] + forecast_data['city']['timezone']).strftime('%A')
            temp = round(entry['main']['temp'] - 273.15)

            if date_text not in daily_forecast:
                daily_forecast[date_text] = {'high': temp, 'low': temp}
            else:
                if temp > daily_forecast[date_text]['high']:
                    daily_forecast[date_text]['high'] = temp
                if temp < daily_forecast[date_text]['low']:
                    daily_forecast[date_text]['low'] = temp
        
        display_text = ""
        count = 0
        for day, temps in daily_forecast.items():
            if count < 5:
                high_temp = round(temps['high'])
                low_temp = round(temps['low'])
                display_text += f"{day}: H: {high_temp}°C  L: {low_temp}°C\n"
                count += 1
        
        forecast_label_5_day.config(text=display_text)

# Function to display the hourly forecast horizontally
def display_hourly_forecast(city):
    forecast_data = get_5_day_forecast(city)
    if forecast_data:
        hourly_label.config(text="")
        display_text = ""
        
        for i in range(6):
            forecast = forecast_data['list'][i]
            time_text = datetime.utcfromtimestamp(forecast['dt'] + forecast_data['city']['timezone']).strftime('%I:%M %p')
            temp = round(forecast['main']['temp'] - 273.15)
            display_text += f"{time_text}: {temp}°C | "
        
        hourly_label.config(text=display_text.rstrip(" | "))

# Display weather details
def display_weather():
    city = textField.get().strip()
    if not city:
        messagebox.showwarning("Input Error", "Please enter a city name")
        return
    
    city_name, state, country = get_location_details(city)
    if not city_name:
        return
    
    weather_data = get_weather(city)
    if weather_data:
        temp = int(weather_data['main']['temp'] - 273.15) 
        condition = weather_data['weather'][0]['main']
        high_temp = int(weather_data['main']['temp_max'] - 273.15)
        low_temp = int(weather_data['main']['temp_min'] - 273.15)
        
        location_label.config(text=f"{city_name}, {state}, {country}")
        condition_label.config(text=f"{condition}, {temp}°C")
        high_low_label.config(text=f"H: {high_temp}°C  L: {low_temp}°C")
        
        display_hourly_forecast(city)
        display_5_day_forecast(city)

# Function to display weather for the selected favorite city
def display_selected_favorite(event):
    selected_index = favorite_listbox.curselection()
    if selected_index:
        selected_city = favorite_listbox.get(selected_index).split(" - ")[0]
        textField.delete(0, tk.END)
        textField.insert(tk.END, selected_city)
        display_weather()



# GUI setup
canvas = tk.Tk()
canvas.title("Weather Application")
canvas.geometry("1000x1100")  # Adjusted height to accommodate additional forecast display
canvas.configure(bg="#333333")  # Set a darker background color

# Fonts and styles (Increased font sizes)
title_font = ("Georgia", 28, "bold")
label_font = ("Arial", 16)
entry_font = ("Calibri", 14)
favorite_font = font.Font(family="Courier New", size=16, weight="bold")

# Main frame
main_frame = tk.Frame(canvas, bg="#333333")
main_frame.pack(pady=20)

# Title
title_label = tk.Label(main_frame, text="Weather Forecast", font=title_font, bg="#333333", fg="white")
title_label.pack()

# Input frame
input_frame = tk.Frame(main_frame, bg="#333333")
input_frame.pack(pady=10)

textField = ttk.Entry(input_frame, font=entry_font, width=30)
textField.grid(row=0, column=0, padx=5)

get_weather_btn = ttk.Button(input_frame, text="Get Weather", command=display_weather)
get_weather_btn.grid(row=0, column=1)

add_favorite_btn = ttk.Button(input_frame, text="Add to Favorites", command=add_to_favorites)
add_favorite_btn.grid(row=0, column=2, padx=5)

# Display details frame
display_frame = tk.Frame(main_frame, bg="#333333")
display_frame.pack(pady=20)

location_label = tk.Label(display_frame, text="Location", font=label_font, bg="#333333", fg="white")
location_label.pack()

condition_label = tk.Label(display_frame, text="Condition", font=label_font, bg="#333333", fg="white")
condition_label.pack()

# Add a label for the High and Low temperatures
high_low_label = tk.Label(display_frame, text="", font=("Helvetica", 16), bg="#333333", fg="white")
high_low_label.pack()

# Hourly forecast frame
hourly_frame = tk.LabelFrame(main_frame, text="Hourly Forecast", bg="#333333", font=label_font, fg="white", relief="groove", padx=10, pady=5)
hourly_frame.pack(pady=10)

hourly_label = tk.Label(hourly_frame, text="", font=label_font, bg="#333333", fg="white", justify="left", wraplength=800)
hourly_label.pack(pady=5)

# 5-day forecast frame
forecast_5_day_frame = tk.LabelFrame(main_frame, text="Daily Forecast", bg="#333333", font=label_font, fg="white", relief="groove", padx=10, pady=5)
forecast_5_day_frame.pack(pady=10)

forecast_label_5_day = tk.Label(forecast_5_day_frame, text="", font=label_font, bg="#333333", fg="white", justify="left", wraplength=800)
forecast_label_5_day.pack(pady=5)

# Favorites frame
favorites_frame = tk.LabelFrame(main_frame, text="Favorite Locations", bg="#333333", font=label_font, fg="white", relief="groove", padx=10, pady=5)
favorites_frame.pack(pady=10)

favorite_listbox = tk.Listbox(favorites_frame, width=50, height=6, font=favorite_font, bg="#333333", fg="white", selectbackground="#666666")
favorite_listbox.pack(side=tk.LEFT, padx=5, pady=5)
favorite_listbox.bind('<<ListboxSelect>>', display_selected_favorite)  # Bind the event

remove_favorite_btn = ttk.Button(favorites_frame, text="Remove from Favorites", command=remove_from_favorites)
remove_favorite_btn.pack(pady=5)

# Close the database connection when the app is closed
def on_closing():
    conn.close()
    canvas.destroy()

canvas.protocol("WM_DELETE_WINDOW", on_closing)
canvas.mainloop()
