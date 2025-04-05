import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton

import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import smtplib
import requests

# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to fetch news
def fetch_news(api_key):
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles')
        if articles:
            news_text = ""
            for idx, article in enumerate(articles, start=1):
                news_text += f"{idx}. {article['title']}\n"
                news_text += f"   {article['description']}\n"
                news_text += f"   Read more: {article['url']}\n\n"
            return news_text
        else:
            return "No articles found."
    else:
        return "Failed to fetch news."

# Function to send an email
def send_email(receiver, subject, message):
    EMAIL_ADDRESS = 'mullajaaveed786@gmail.com'
    EMAIL_PASSWORD = '************'
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, receiver, f"Subject: {subject}\n\n{message}")
        server.close()
        speak("Email sent successfully!")
    except Exception as e:
        print(e)
        speak("Sorry, I am unable to send the email at the moment.")

# Function to shutdown the PC
def shutdown():
    os.system("shutdown /s /t 1")

# Function to restart the PC
def restart():
    os.system("shutdown /r /t 1")

# Function to handle speech recognition
def take_command():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 2
        audio = recognizer.listen(source)

        try:
            print("Recognizing...")
            query = recognizer.recognize_google(audio, language='en-in')
            print("You:", query)
            return query.lower()
        except Exception as e:
            print(e)
            speak("Sorry, I didn't get that.")
            return ""

# Main App Class
class PersonalAssistantApp(App):

    def build(self):
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header
        header = Label(text="Personal Assistant", font_size=32, color=[1, 1, 1, 1], size_hint=(1, 0.1))
        layout.add_widget(header)

        # Grid Layout for buttons
        grid_layout = GridLayout(cols=2, spacing=10, size_hint=(1, 0.6))

        # Wikipedia Search Button
        btn_wikipedia = Button(text="Search Wikipedia", background_color=[0, 0, 0, 1], color=[1, 1, 1, 1])
        btn_wikipedia.bind(on_press=self.search_wikipedia)
        grid_layout.add_widget(btn_wikipedia)

        # Open YouTube Button
        btn_youtube = Button(text="Open YouTube", background_color=[0, 0, 0, 1], color=[1, 1, 1, 1])
        btn_youtube.bind(on_press=lambda x: self.open_website("https://www.youtube.com"))
        grid_layout.add_widget(btn_youtube)

        # Open Google Button
        btn_google = Button(text="Open Google", background_color=[0, 0, 0, 1], color=[1, 1, 1, 1])
        btn_google.bind(on_press=lambda x: self.open_website("https://www.google.com"))
        grid_layout.add_widget(btn_google)

        # Fetch News Button
        btn_news = Button(text="Fetch News", background_color=[0, 0, 0, 1], color=[1, 1, 1, 1])
        btn_news.bind(on_press=self.fetch_news_popup)
        grid_layout.add_widget(btn_news)

        # Open File Button
        btn_open_file = Button(text="Open File", background_color=[0, 0, 0, 1], color=[1, 1, 1, 1])
        btn_open_file.bind(on_press=self.open_file)
        grid_layout.add_widget(btn_open_file)

        # Exit Button
        btn_exit = Button(text="Exit", background_color=[1, 0, 0, 1], color=[1, 1, 1, 1])
        btn_exit.bind(on_press=self.stop)
        grid_layout.add_widget(btn_exit)

        layout.add_widget(grid_layout)

        # Text input area for manual commands
        self.text_input = TextInput(hint_text="Type your command here...", size_hint=(1, 0.1))
        layout.add_widget(self.text_input)

        # Toggle Button to switch between Text and Speech input
        self.toggle_button = ToggleButton(text="Speech Input", state='down', size_hint=(1, 0.1))
        self.toggle_button.bind(on_press=self.toggle_input_mode)
        layout.add_widget(self.toggle_button)

        # Language Dropdown
        self.language_dropdown = DropDown()
        languages = ['en', 'es', 'fr', 'de', 'zh']
        for lang in languages:
            btn = Button(text=lang, size_hint_y=None, height=44, background_color=[0, 0, 0, 1], color=[1, 1, 1, 1])
            btn.bind(on_release=lambda btn: self.language_dropdown.select(btn.text))
            self.language_dropdown.add_widget(btn)

        self.language_button = Button(text='Select Language', size_hint=(1, 0.1), background_color=[0, 0, 0, 1],
                                      color=[1, 1, 1, 1])
        self.language_button.bind(on_release=self.language_dropdown.open)
        self.language_dropdown.bind(on_select=lambda instance, x: setattr(self.language_button, 'text', x))
        layout.add_widget(self.language_button)

        # Footer
        footer = Label(text="Voice-Activated Personal Assistant", font_size=18, color=[1, 1, 1, 1], size_hint=(1, 0.1))
        layout.add_widget(footer)

        # Set background color
        layout.canvas.before.clear()
        with layout.canvas.before:
            kivy.graphics.Color(0, 0, 0, 1)  # Black border
            kivy.graphics.Rectangle(size=layout.size, pos=layout.pos)

        return layout

    # Toggle between Text and Speech input
    def toggle_input_mode(self, instance):
        if self.toggle_button.state == 'down':
            self.toggle_button.text = "Speech Input"
        else:
            self.toggle_button.text = "Text Input"

    # Search Wikipedia Function
    def search_wikipedia(self, instance):
        if self.toggle_button.state == 'down':  # Speech input
            speak("What do you want to search?")
            query = take_command()
        else:  # Text input
            query = self.text_input.text

        if query:
            try:
                results = wikipedia.summary(query, sentences=2)
                speak("According to Wikipedia")
                speak(results)
                self.show_popup("Wikipedia Results", results)
            except wikipedia.exceptions.PageError:
                self.show_popup("Wikipedia Error", "Page not found.")
            except wikipedia.exceptions.DisambiguationError as e:
                self.show_popup("Wikipedia Error", f"Disambiguation error: {e.options}")
            except Exception as e:
                self.show_popup("Wikipedia Error", str(e))

    # Function to open a website
    def open_website(self, url):
        webbrowser.open(url)

    # Function to fetch news and show in popup
    def fetch_news_popup(self, instance):
        api_key = 'YOUR_NEWS_API_KEY'
        news = fetch_news(api_key)
        self.show_popup("Latest News", news)

    # Function to open a file
    def open_file(self, instance):
        if self.toggle_button.state == 'down':  # Speech input
            speak("Please provide the file path.")
            file_path = take_command()
        else:  # Text input
            file_path = self.text_input.text

        if os.path.exists(file_path):
            os.startfile(file_path)
        else:
            self.show_popup("Error", "File not found.")

    # Function to show a popup with results or errors
    def show_popup(self, title, content):
        popup_content = Label(text=content, size_hint_y=None, height=200)
        popup = Popup(title=title, content=popup_content, size_hint=(0.8, 0.8))
        popup.open()

if __name__ == "__main__":
    PersonalAssistantApp().run()
