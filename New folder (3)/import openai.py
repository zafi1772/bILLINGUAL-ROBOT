import speech_recognition as sr
import pyttsx3
import openai
from gtts import gTTS
import os
import sys

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

def listen():
    """Capture and recognize speech, returning the recognized text."""
    global language, use_gtts
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise based on the environment
        audio = recognizer.listen(source, phrase_time_limit=15)  # No timeout, just a phrase time limit of 15 seconds
        try:
            text = recognizer.recognize_google(audio, language=language)
            print(f"You said: {text}")

            # Switch to Bengali if the word "Bangla" is spoken
            if 'bangla' in text.lower():
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
    """Use the appropriate text-to-speech engine to reply with the given response."""
    global use_gtts
    print(f"Bot: {response}")  # This should now handle Unicode characters properly
    if use_gtts:
        # Use gTTS for Bengali response
        tts = gTTS(text=response, lang='bn')
        tts.save("response.mp3")
        os.system("start response.mp3")
    else:
        # Use pyttsx3 for English response
        engine.say(response)
        engine.runAndWait()

def get_chatgpt_response(user_input):
    """Get a response from OpenAI's ChatGPT model."""
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
while True:
    user_input = listen()  # Listen to the user
    if user_input:
        chatgpt_reply = get_chatgpt_response(user_input)  # Get response from GPT
        if chatgpt_reply:
            reply(chatgpt_reply)  # Reply using appropriate voice engine
        else:
            print("No response from ChatGPT or an error occurred.")
