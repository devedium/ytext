import argparse
from pytube import YouTube
import whisper
import os

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="youtube text transcript.")

    # Add the arguments
    parser.add_argument('--url', metavar='url', type=str, help='youtube video url')
    parser.add_argument('--dir', metavar='dir', type=str, default='.', help='the directory for the downloaded files.')

    # Parse the arguments
    args = parser.parse_args()

    url = args.url
    yt = YouTube(url, 
                 on_progress_callback = lambda stream, chuck, remain : print(f"\r remain bytes {remain}"),
                 on_complete_callback = lambda stream, path : print(f"\r\nDownloaded at {path}"))
    audio = yt.streams.filter(only_audio=True).first()
    if audio is None:
        audio = yt.streams.first()

    audio_filepath = audio.download(args.dir)

    # Split the filepath into name and extension
    name, ext = os.path.splitext(audio_filepath)
    # Replace the extension with ".txt"
    txt_filepath = name + ".txt"

    model = whisper.load_model("large")
    text = model.transcribe(audio_filepath)
    #printing the transcribe
    transcribed_text = text['text']
    # Open a file in write mode ('w')
    with open(txt_filepath, "w", encoding='utf-8') as file:
        # Write the transcribed text to the file
        file.write(transcribed_text)

if __name__ == "__main__":
    main()
