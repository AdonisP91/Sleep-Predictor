import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import pytz


# Function to get the selected date and time from the GUI
def get_input():
    selected_date = cal.get_date()
    selected_time = f"{hour_var.get()}:{minute_var.get()}"
    drift_minutes = int(drift_entry.get())

    current_sleep_time = f"{selected_date} {selected_time}"

    # Get the future date from the calendar widget
    future_date = future_cal.get_date()

    # Predict sleep time using the function
    predicted_sleep_time = predict_sleep_time(current_sleep_time, future_date, drift_minutes)

    # Check if "Travel" is selected and adjust for time zone difference
    if travel_var.get():
        local_city = local_city_entry.get()  # Get the local city name
        destination_city = destination_city_entry.get()  # Get the destination city name
        time_zone_shift = calculate_time_zone_difference(local_city, destination_city)
        if time_zone_shift is not None:
            new_time_zone_time = predicted_sleep_time + timedelta(hours=time_zone_shift)
            result_label.config(text=f"Predicted local sleep time: {predicted_sleep_time.strftime('%Y-%m-%d %H:%M')}\n"
                                     f"Predicted sleep time in {destination_city}: {new_time_zone_time.strftime('%Y-%m-%d %H:%M')}")
        else:
            result_label.config(text="Cities not found or time zones could not be determined.")
    else:
        result_label.config(text=f"Predicted sleep time: {predicted_sleep_time.strftime('%Y-%m-%d %H:%M')}")


# Function to predict sleep time
def predict_sleep_time(current_sleep_time: str, future_date: str, drift_minutes: int) -> datetime:
    current_datetime = datetime.strptime(current_sleep_time, '%m/%d/%y %H:%M')
    future_datetime = datetime.strptime(future_date, '%m/%d/%y')
    future_datetime = future_datetime.replace(hour=current_datetime.hour, minute=current_datetime.minute)

    days_difference = (future_datetime.date() - current_datetime.date()).days
    total_time_shift = timedelta(minutes=drift_minutes * days_difference)

    predicted_sleep_time = current_datetime + total_time_shift
    return predicted_sleep_time


# Calculate time zone difference based on local and destination cities
def calculate_time_zone_difference(local_city: str, destination_city: str):
    geolocator = Nominatim(user_agent="sleep_time_predictor")
    try:
        # Get the local city location
        local_location = geolocator.geocode(local_city)
        destination_location = geolocator.geocode(destination_city)
        if local_location and destination_location:
            # Find the time zones of both the local and destination locations
            tf = TimezoneFinder()
            local_tz_name = tf.timezone_at(lng=local_location.longitude, lat=local_location.latitude)
            destination_tz_name = tf.timezone_at(lng=destination_location.longitude, lat=destination_location.latitude)
            if local_tz_name and destination_tz_name:
                local_tz = pytz.timezone(local_tz_name)
                destination_tz = pytz.timezone(destination_tz_name)

                # Get current UTC offset for both local and destination
                now = datetime.now()
                local_offset = local_tz.utcoffset(now).total_seconds() / 3600
                destination_offset = destination_tz.utcoffset(now).total_seconds() / 3600

                return destination_offset - local_offset
    except Exception as e:
        print(f"Error finding time zone: {e}")
    return None


# Toggle the city input entry based on the checkbox
def toggle_travel():
    if travel_var.get():
        local_city_label.grid(row=11, column=0, padx=10, pady=5, sticky="w")
        local_city_entry.grid(row=12, column=0, padx=10, pady=5)
        destination_city_label.grid(row=13, column=0, padx=10, pady=5, sticky="w")
        destination_city_entry.grid(row=14, column=0, padx=10, pady=5)
    else:
        local_city_label.grid_remove()
        local_city_entry.grid_remove()
        destination_city_label.grid_remove()
        destination_city_entry.grid_remove()


# GUI setup
root = tk.Tk()
root.title("Sleep Time Predictor")

# Adjust window size to accommodate the new feature
root.geometry("450x1000")

# Drift input
tk.Label(root, text="Enter your average drift (time increment in minutes per day):").grid(row=0, column=0, padx=10, pady=(20, 5),
                                                                                 sticky="w")
drift_entry = tk.Entry(root, width=20)
drift_entry.grid(row=1, column=0, padx=10, pady=(5, 20))

# Current sleep date selection
tk.Label(root, text="Select the last date you went to sleep:").grid(row=2, column=0, padx=10, pady=(10, 5), sticky="w")
cal = Calendar(root, selectmode="day", date_pattern="mm/dd/yy")
cal.grid(row=3, column=0, padx=10, pady=(5, 20))

# Time selection (hours and minutes)
tk.Label(root, text="Select the last time you went to sleep (24-hour format):").grid(row=4, column=0, padx=10, pady=(10, 5),
                                                                                sticky="w")

time_frame = tk.Frame(root)
time_frame.grid(row=5, column=0, padx=10, pady=(5, 20))

hour_var = tk.StringVar(value="22")
minute_var = tk.StringVar(value="00")

ttk.Spinbox(time_frame, from_=0, to=23, textvariable=hour_var, width=5, format="%02.0f").grid(row=0, column=0, padx=2)
ttk.Spinbox(time_frame, from_=0, to=59, textvariable=minute_var, width=5, format="%02.0f").grid(row=0, column=1, padx=2)

# Future date selection
tk.Label(root, text="Select the future date for prediction:").grid(row=6, column=0, padx=10, pady=(10, 5), sticky="w")
future_cal = Calendar(root, selectmode="day", date_pattern="mm/dd/yy")
future_cal.grid(row=7, column=0, padx=10, pady=(5, 20))

# Travel checkbox
travel_var = tk.IntVar()
travel_checkbox = tk.Checkbutton(root, text="Travel (Adjust for time zone changes)", variable=travel_var,
                                 command=toggle_travel)
travel_checkbox.grid(row=10, column=0, padx=10, pady=(10, 5), sticky="w")

# Local city and destination city entries (hidden by default)
local_city_label = tk.Label(root, text="Enter your local city:")
local_city_entry = tk.Entry(root, width=20)

destination_city_label = tk.Label(root, text="Enter the destination city:")
destination_city_entry = tk.Entry(root, width=20)

# Button to submit and get prediction
submit_button = tk.Button(root, text="Predict Sleep Time", command=get_input)
submit_button.grid(row=15, column=0, padx=10, pady=(10, 20))

# Label to display the result
result_label = tk.Label(root, text="", font=("Helvetica", 12), wraplength=400)
result_label.grid(row=16, column=0, padx=10, pady=(10, 20))

# Run the GUI event loop
root.mainloop()
