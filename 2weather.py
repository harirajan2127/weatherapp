import streamlit as st
import requests
import pyttsx3
import speech_recognition as sr
from PIL import Image
import io
from datetime import datetime
import webbrowser
import threading

# Set Streamlit page config
st.set_page_config(page_title="Weather App", layout="centered")

# Initialize pyttsx3 engine
engine = pyttsx3.init()

# Speak function with threading
def speak(text):
    def run():
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=run).start()

# Speech recognition function
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Please say the name of the city.")
        try:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
            city = recognizer.recognize_google(audio)
            speak(f"You said {city}.")
            return city
        except sr.UnknownValueError:
            speak("Sorry, I could not understand what you said.")
        except sr.RequestError:
            speak("Could not request results from the speech service.")
        except sr.WaitTimeoutError:
            speak("Listening timed out. Please try again.")
    return None

# Get weather data from API
def get_weather(city):
    api_key = "a823dac285eb4ad1858f1e0e4d1a3065"  # Replace with your OpenWeather API key
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            condition = data['weather'][0]['description']
            humidity = data['main']['humidity']
            wind = data['wind']['speed']
            icon_code = data['weather'][0]['icon']
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
            icon_response = requests.get(icon_url)
            icon_img = None
            if icon_response.status_code == 200:
                icon_img = Image.open(io.BytesIO(icon_response.content))

            weather_report = {
                "city": city,
                "timestamp": timestamp,
                "temp": temp,
                "condition": condition,
                "humidity": humidity,
                "wind": wind,
                "icon": icon_img
            }

            return weather_report
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# UI layout
st.title("🌦️ Weather App with Voice & Map")
st.markdown("Get real-time weather updates using voice or text input.")

# Text input
city = st.text_input("Enter city name")

# Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("Get Weather"):
        if city:
            report = get_weather(city)
            if report:
                st.image(report["icon"], width=100)
                st.markdown(f"### Weather in {report['city']}")
                st.write(f"**Date & Time:** {report['timestamp']}")
                st.write(f"**Temperature:** {report['temp']}°C")
                st.write(f"**Condition:** {report['condition'].title()}")
                st.write(f"**Humidity:** {report['humidity']}%")
                st.write(f"**Wind Speed:** {report['wind']} m/s")

                speak(
                    f"The weather in {report['city']} is {report['condition']}, "
                    f"temperature {report['temp']} degrees Celsius, "
                    f"humidity {report['humidity']} percent, "
                    f"and wind speed {report['wind']} meters per second."
                )

                map_url = f"https://www.google.com/maps/search/{report['city']}"
                st.markdown(f"[🗺️ Show on Google Maps]({map_url})", unsafe_allow_html=True)
            else:
                st.error("City not found.")
        else:
            st.warning("Please enter a city name.")

with col2:
    if st.button("🎤 Speak City Name"):
        city_from_voice = recognize_speech()
        if city_from_voice:
            st.success(f"You said: {city_from_voice}")
            report = get_weather(city_from_voice)
            if report:
                st.image(report["icon"], width=100)
                st.markdown(f"### Weather in {report['city']}")
                st.write(f"**Date & Time:** {report['timestamp']}")
                st.write(f"**Temperature:** {report['temp']}°C")
                st.write(f"**Condition:** {report['condition'].title()}")
                st.write(f"**Humidity:** {report['humidity']}%")
                st.write(f"**Wind Speed:** {report['wind']} m/s")

                speak(
                    f"The weather in {report['city']} is {report['condition']}, "
                    f"temperature {report['temp']} degrees Celsius, "
                    f"humidity {report['humidity']} percent, "
                    f"and wind speed {report['wind']} meters per second."
                )

                map_url = f"https://www.google.com/maps/search/{report['city']}"
                st.markdown(f"[🗺️ Show on Google Maps]({map_url})", unsafe_allow_html=True)
            else:
                st.error("City not found.")

