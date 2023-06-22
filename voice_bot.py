import openai
import os
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
import simpleaudio as sa
import threading
import numpy as np
import time

openai.api_key = "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"

sound_file = "typing.mp3" # replace with your typing sound file
typing_sound = AudioSegment.from_file(sound_file)

typing = threading.Event()
play_obj = None

def transcribe_audio_to_text(audio):
    recognizer = sr.Recognizer()
    try:
        return recognizer.recognize_google(audio, language='zh-CN')  # change to Chinese
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    except Exception as e:
        print(f"Unexpected error: {e}")

def generate_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=400,
        n = 1
    )
    return response['choices'][0]['message']['content']

def speak(text):
    global play_obj
    tts = gTTS(text=text, lang='zh-CN')  # change to Chinese
    filename = "output.mp3"
    tts.save(filename)
    audio = AudioSegment.from_mp3(filename)
    play_obj = sa.play_buffer(np.array(audio.get_array_of_samples()), 1, 2, audio.frame_rate)
    play_obj.wait_done()

def play_typing_sound():
    global play_obj
    while typing.is_set():
        play_obj = sa.play_buffer(np.array(typing_sound.get_array_of_samples()), 1, 2, typing_sound.frame_rate)
        while play_obj.is_playing() and typing.is_set():
            time.sleep(0.1)
        if play_obj.is_playing():
            play_obj.stop()

def main():
    speak("我能帮你什么？")  # change to Chinese
    while True:
        with sr.Microphone() as source:
            recognizer = sr.Recognizer()
            print("Listening...")
            audio = recognizer.listen(source)
            try:
                transcription = transcribe_audio_to_text(audio)
                print(f"Transcription: {transcription}")

                if transcription:
                    print(f"You said: {transcription}")

                    # Start typing sound
                    typing.set()
                    typing_thread = threading.Thread(target=play_typing_sound)
                    typing_thread.start()

                    # Generate response
                    response = generate_response(transcription)
                    print(f"GPT said: {response}")

                    # Stop typing sound and start speaking
                    typing.clear()
                    if play_obj.is_playing():
                        play_obj.stop()
                    typing_thread.join()

                    speak(response)

            except Exception as e: 
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()