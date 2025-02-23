import pyttsx3
import speech_recognition as sr
import webbrowser
import random
import datetime
from plyer import notification
import pyautogui
import wikipedia
import pywhatkit as pwk
import smtplib
import user_config
import os
from mtranslate import translate
import requests
import json

engine = pyttsx3.init()
engine.setProperty("rate", 170)

# Get Gemini API key from environment variable
GEMINI_API_KEY = os.environ.get("gemini ai key")

if not GEMINI_API_KEY:
    print("Error: Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        user_command = r.recognize_google(audio, language='hi')
        print(f"You said: {user_command}")

        translated_text = translate(user_command, to_language="en")
        print(f"Translated: {translated_text}")
        return translated_text.lower().strip()
    except sr.UnknownValueError:
        print("I couldn't understand. Please try again.")
        return None
    except sr.RequestError as e:
        print(f"Could not connect to the recognition service: {e}")
        return None

def play_music():
    speak("Playing music...")
    music_links = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=3JZ4pnNtyxQ",
        "https://www.youtube.com/watch?v=kJQP7kiw5Fk"
    ]
    webbrowser.open(random.choice(music_links))

def search_wikipedia(query):
    wikipedia.set_lang("en")
    try:
        result = wikipedia.summary(query, sentences=2)
        print(result)
        speak(result)
        return result
    except wikipedia.exceptions.DisambiguationError:
        speak("There are multiple results. Please be more specific.")
    except wikipedia.exceptions.PageError:
        speak("I couldn't find anything on Wikipedia for that search.")

def ask_gemini(query):
    if not GEMINI_API_KEY:
        return "Gemini API key is missing."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": query}]}]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
        if 'candidates' in result and result['candidates']:
            ai_response = result['candidates'][0]['content']['parts'][0]['text']
            print(ai_response)
            speak(ai_response)
            return ai_response
        else:
            return "Gemini API returned an unexpected response."
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Gemini API: {e}")
        return "I'm unable to process your request right now."
    except json.JSONDecodeError:
        return "Error: Could not decode Gemini API response."

def main_process():
    while True:
        request = command()

        if request is None:
            continue

        if "hello" in request:
            speak("Welcome! How can I help you?")

        elif "play music" in request:
            play_music()

        elif "exit" in request or "stop" in request:
            speak("Goodbye! Have a great day.")
            break

        elif "say time" in request:
            now_time = datetime.datetime.now().strftime("%I:%M %p")
            speak("The current time is " + now_time)

        elif "say date" in request:
            now_date = datetime.datetime.now().strftime("%d-%m-%Y")
            speak("Today's date is " + now_date)

        elif "open youtube" in request:
            webbrowser.open("https://www.youtube.com")

        elif "search wikipedia" in request:
            search_query = request.replace("search wikipedia", "").strip()
            search_wikipedia(search_query)

        elif "search google" in request:
            query = request.replace("search google", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={query}")

        elif "send whatsapp" in request:
            phone_number = "+910123456789"
            message = "Hi, this is an automated message."
            now = datetime.datetime.now() + datetime.timedelta(minutes=2)
            pwk.sendwhatmsg(phone_number, message, now.hour, now.minute)
            speak("WhatsApp message scheduled.")

        elif "ask gemini" in request:
            query = request.replace("ask gemini", "").strip()
            ask_gemini(query)

        else:
            ask_gemini(request)

if __name__ == "__main__":
    main_process()
