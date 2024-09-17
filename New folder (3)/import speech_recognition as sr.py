import speech_recognition as sr
import pyttsx3
import openai
import wikipedia
import webbrowser
import os
import sys
import time
import pygame
from gtts import gTTS  # Added gTTS import for Google Text-to-Speech

# Set the console to use UTF-8 encoding for Unicode characters
sys.stdout.reconfigure(encoding='utf-8')

# OpenAI API Key
openai.api_key = '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'

# Initialize the speech recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Set the initial language for recognition and response
language = 'en-US'  # Default to English
use_gtts = False  # Default to pyttsx3 for English responses

# Flag to manage whether the system is speaking
speaking = False

def list_voices():
    """List available voices and their properties."""
    voices = engine.getProperty('voices')
    for index, voice in enumerate(voices):
        print(f"Index: {index}, ID: {voice.id}, Name: {voice.name}, Lang: {voice.languages}")

def listen():
    """Capture and recognize speech, returning the recognized text."""
    global language, use_gtts, speaking
    while speaking:  # Wait until speaking is finished before listening
        time.sleep(0.1)  # Slight delay to prevent high CPU usage
    
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise based on the environment
        audio = recognizer.listen(source, phrase_time_limit=15)  # No timeout, just a phrase time limit of 15 seconds
        try:
            text = recognizer.recognize_google(audio, language=language)
            print(f"You said: {text}")

            # Switch to Bengali if the word "Bangla" is spoken
            if 'bangla' in text.lower() or 'Bangla' in text:
                language = 'bn-BD'
                use_gtts = True
                print("Switched to Bengali language for recognition and response")

            # Switch back to English if the word "English" or "ইংলিশ" is spoken
            elif 'english' in text.lower() or 'ইংলিশ' in text:
                language = 'en-US'
                use_gtts = False
                print("Switched to English language for recognition and response")

            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Error from Google Speech Recognition service: {e}")
            return None

def reply(response):
    """Use the appropriate text-to-speech engine to reply with the first 10 lines of the given response."""
    global use_gtts, speaking
    print(f"Bot: {response}")  # Display full response

    # Limit the response to 10 lines
    limited_response = "\n".join(response.splitlines()[:10])

    speaking = True
    if use_gtts:
        tts = gTTS(text=limited_response, lang='bn', slow=False)
        tts.save("response.mp3")
        
        # Initialize pygame mixer and play audio
        pygame.mixer.init()
        pygame.mixer.music.load("response.mp3")
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():  # Wait for playback to finish
            time.sleep(0.1)
        
        pygame.mixer.music.stop()  # Ensure the audio file is no longer in use
        pygame.mixer.quit()  # Close the mixer
        os.remove("response.mp3")  # Now it is safe to delete the file
    else:
        engine.say(limited_response)
        engine.runAndWait()

    speaking = False

def handle_special_cases(user_input):
    """Handle special cases like opening map or playing video."""
    # Check if the user mentions map or ম্যাপ
    if 'map' in user_input.lower() or 'ম্যাপ' in user_input.lower():
        # Redirect to the Indoor Navigation website
        webbrowser.open("https://nakib00.github.io/Indoor-Navigation-js/")
        return "Redirecting to the map."

    # Check if the user mentions IUB or iob or আই ইউ বি
    if 'iub' in user_input.lower() or 'iob' in user_input.lower() or 'আই ইউ বি' in user_input.lower():
        # Play the video from the specified path
        video_path = "C:\\Users\\Administrator\\Desktop\\New folder (3)\\y2mate.com - Independent University Bangladesh IUB_1080p.mp4"
        os.startfile(video_path)
        return "Playing the IUB video."

    return None  # No special case detected

def get_wikipedia_summary(query):
    """Get a summary from Wikipedia for the given query."""
    try:
        # Fetch the summary (2 sentences) for the query
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"There are multiple results for {query}. Please be more specific."
    except wikipedia.exceptions.PageError:
        return "Sorry, I couldn't find anything on Wikipedia for that topic."
    except Exception as e:
        return f"An error occurred while fetching the Wikipedia information: {e}"

def get_chatgpt_response(user_input):
    """Get a response from OpenAI's ChatGPT model or handle special cases."""
    
    # Check if the user asks who made you (custom response)
    # Add variations for Bengali phrases
    if any(phrase in user_input.lower() for phrase in ['who made you', 'আপনারা কে বানাইছে', 'আপনাকে কে বানিয়েছে', 'তোদের কে বানাইছে']):
        return 'I was created by a group of CSE students from FAB Lab Independent University Bangladesh. They are Umme Aiman. Nakibul Islam. Hana Sultan.'

    # Handle special cases like map or video
    special_response = handle_special_cases(user_input)
    if special_response:
        return special_response

    # Otherwise, get response from ChatGPT
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input},
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error communicating with OpenAI: {e}")
        return None

# Main loop
if __name__ == "__main__":
    # Initialize pygame (important to do this before using mixer)
    pygame.init()

    while True:
        user_input = listen()  # Listen to the user
        if user_input:
            chatgpt_reply = get_chatgpt_response(user_input)  # Get response from GPT or handle custom responses
            if chatgpt_reply:
                reply(chatgpt_reply)  # Reply using appropriate voice engine
            else:
                print("No response from ChatGPT or an error occurred.")
