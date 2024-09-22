# WeatherApp

Weather Forecast Desktop Application
This Weather Forecast Desktop Application is a simple and user-friendly Python-based weather app that displays current weather conditions, hourly forecasts, and a 7-day forecast for any city. The app leverages the OpenWeatherMap API to fetch real-time data and provides an intuitive graphical user interface (GUI) built using Tkinter.

Features:
Current Weather Display:

Displays real-time weather data such as temperature, humidity, wind speed, and weather conditions for a selected city.
Shows high and low temperatures for the day.
Hourly Forecast:

Displays the hourly weather forecast for the next several hours, including the temperature and weather conditions.
5-Day Forecast:

Shows the daily high and low temperatures for the next 7 days.
Forecast is updated in real-time based on the selected city.
Favorite Locations:

Allows users to save cities to their list of favorites.
Users can view the weather for any saved favorite city by selecting it from the list.
Option to remove cities from the favorites list.
Responsive Interface:

Clean and modern design with easy-to-read fonts and dark-themed interface for better visibility.
Displays weather data in a well-organized manner, making it easy for users to navigate.
Technologies Used:
Python: Core language used to build the application.
Tkinter: Python’s built-in library for creating graphical user interfaces (GUIs).
OpenWeatherMap API: Used to fetch real-time weather data for the application.
SQLite: Local database to store user preferences and favorite locations.

How It Works:
Search for a City:

Users can enter the name of any city in the search field.
The app fetches real-time weather data for the city using the OpenWeatherMap API.
Add to Favorites:

After retrieving the weather for a city, users can add it to their favorites list.
The city will be saved in a local SQLite database for easy access.
View Weather for Favorite Cities:

Users can select any city from the favorites list to view the current, hourly, and 7-day weather forecast for that city.
Remove from Favorites:

Cities can be removed from the favorites list if they are no longer needed.
