import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import io
import numpy as np

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ZenithSky Weather App")
        self.root.geometry("800x600")

        # Set background color
        self.root.configure(bg="#87CEFA")  # Sky blue background

        # Load a background image
        self.bg_image = Image.open("background.jpg")  # Ensure you have a background.jpg in your directory
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.bg_label = tk.Label(self.root, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)

        # Create input and button frame
        self.input_frame = tk.Frame(self.root, bg="#FFFFFF", padx=10, pady=10)
        self.input_frame.grid(row=0, column=0, padx=20, pady=20, columnspan=2, sticky="ew")

        self.city_entry = tk.Entry(self.input_frame, width=30, font=("Arial", 14))
        self.city_entry.grid(row=0, column=0, padx=10, pady=10)
        self.search_button = tk.Button(self.input_frame, text="Get Weather", command=self.fetch_weather, font=("Arial", 12), bg="#4CAF50", fg="#FFFFFF")
        self.search_button.grid(row=0, column=1, padx=10, pady=10)
        
        self.refresh_button = tk.Button(self.input_frame, text="Refresh Data", command=self.fetch_weather, font=("Arial", 12), bg="#2196F3", fg="#FFFFFF")
        self.refresh_button.grid(row=1, column=0, padx=10, pady=10, columnspan=2)
        
        # Create weather display area
        self.weather_frame = tk.Frame(self.root, bg="#FFFFFF", padx=10, pady=10)
        self.weather_frame.grid(row=1, column=0, padx=20, pady=20, columnspan=2, sticky="ew")

        self.weather_label = tk.Label(self.weather_frame, text="", font=("Arial", 12), bg="#FFFFFF")
        self.weather_label.pack()

        # Create an error display area
        self.error_label = tk.Label(self.weather_frame, text="", font=("Arial", 12), fg="red", bg="#FFFFFF")
        self.error_label.pack()

        # Create a loading spinner
        self.spinner = ttk.Label(self.weather_frame, text="Loading...", font=("Arial", 12))
        self.spinner.pack()
        self.spinner_visible = False
        self.update_spinner()

        # Load and display weather icons
        self.icon_label = tk.Label(self.weather_frame, bg="#FFFFFF")
        self.icon_label.pack()

        # Create a frame for analysis
        self.analysis_frame = tk.Frame(self.root, bg="#FFFFFF", padx=10, pady=10)
        self.analysis_frame.grid(row=2, column=0, padx=20, pady=20, columnspan=2, sticky="ew")
        self.analysis_label = tk.Label(self.analysis_frame, text="Weather Data Analysis", font=("Arial", 14), bg="#FFFFFF")
        self.analysis_label.pack()
        
        # Placeholder for the Matplotlib plot
        self.plot_canvas = None
        
        # Set auto-refresh interval (e.g., every 30 minutes)
        self.auto_refresh_interval = 1800000  # 30 minutes in milliseconds
        self.schedule_auto_refresh()

    def update_spinner(self):
        if self.spinner_visible:
            self.spinner.pack_forget()
            self.spinner_visible = False
        else:
            self.spinner.pack()
            self.spinner_visible = True
        self.root.after(500, self.update_spinner)

    def fetch_weather(self):
        city = self.city_entry.get()
        if not city:
            self.error_label.config(text="Please enter a city.")
            return

        self.weather_label.config(text="")
        self.error_label.config(text="")
        self.update_spinner()

        api_key = "58f344ac1b81449db0883346242907"  # Replace with your actual API key
        url = f"http://api.weatherapi.com/v1/forecast.json?q={city}&key={api_key}&days=5"
        
        try:
            response = requests.get(url)
            data = response.json()
            self.root.after(0, self.display_weather, data)
        except Exception as e:
            self.root.after(0, self.error_display, "Error fetching weather data.")

    def display_weather(self, data):
        if "error" in data:
            self.error_display("City not found.")
            return

        city = data['location']['name']
        weather_info = f"Weather in {city}:\n"
        timestamps = []
        temperatures = []
        humidities = []
        wind_speeds = []
        
        for day in data['forecast']['forecastday']:
            date = day['date']
            temperature = day['day']['avgtemp_c']
            description = day['day']['condition']['text']
            humidity = day['day']['avghumidity']
            wind_speed = day['day']['maxwind_kph']
            
            weather_info += (
                f"\nDate: {date}\n"
                f"Temperature: {temperature}°C\n"
                f"Description: {description}\n"
                f"Humidity: {humidity}%\n"
                f"Wind Speed: {wind_speed} kph\n"
                "-"*30
            )

            timestamps.append(date)
            temperatures.append(temperature)
            humidities.append(humidity)
            wind_speeds.append(wind_speed)

        self.weather_label.config(text=weather_info)
        self.spinner.pack_forget()

        # Perform data analysis
        self.perform_analysis(timestamps, temperatures, humidities, wind_speeds)

    def perform_analysis(self, timestamps, temperatures, humidities, wind_speeds):
        if self.plot_canvas:
            self.plot_canvas.get_tk_widget().pack_forget()

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(timestamps, temperatures, label='Temperature (°C)', color='blue', marker='o')
        ax.plot(timestamps, humidities, label='Humidity (%)', color='green', marker='o')
        ax.plot(timestamps, wind_speeds, label='Wind Speed (kph)', color='red', marker='o')
        ax.set_xlabel('Date')
        ax.set_ylabel('Values')
        ax.set_title('Weather Data Analysis')
        ax.legend()
        ax.grid(True)

        self.plot_canvas = FigureCanvasTkAgg(fig, master=self.analysis_frame)
        self.plot_canvas.draw()
        self.plot_canvas.get_tk_widget().pack()

    def error_display(self, message):
        self.error_label.config(text=message)
        self.spinner.pack_forget()

    def schedule_auto_refresh(self):
        self.root.after(self.auto_refresh_interval, self.fetch_weather)

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
