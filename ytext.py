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
    parser.add_argument('--prompt',metavar='prompt', type=str, default=None, help='inital prompt for the first window')

    # Parse the arguments
    args = parser.parse_args()

    url = args.url
    yt = YouTube(url, 
                 on_progress_callback = lambda stream, chuck, remain : print(f"\r remain bytes {remain}"),
                 on_complete_callback = lambda stream, path : print(f"\r\ndownloaded at {path}"))
    audio = yt.streams.filter(only_audio=True).first()
    if audio is None:
        audio = yt.streams.first()

    audio_filepath = audio.download(args.dir)

    # Split the filepath into name and extension
    name, ext = os.path.splitext(audio_filepath)
    # Replace the extension with ".txt"
    txt_filepath = name + ".txt"
    segments_filepath = name + "_segments.txt"

    model = whisper.load_model("large")
    result = model.transcribe(audio_filepath,
                              verbose=True,
                              initial_prompt=args.prompt,
                              fp16=False,
                              word_timestamps = False,
                              condition_on_previous_text=True)
    text = result['text']
    
    with open(txt_filepath, "w", encoding='utf-8') as file:
        # Write the transcribed text to the file
        file.write(text)

    with open(segments_filepath, 'w', encoding='utf-8') as f:
        for segment in result['segments']:
            start_min, start_remainder = divmod(segment['start'], 60)
            start_sec, start_ms = divmod(start_remainder, 1)
            start_ms *= 1000  # Convert fractional seconds to milliseconds

            end_min, end_remainder = divmod(segment['end'], 60)
            end_sec, end_ms = divmod(end_remainder, 1)
            end_ms *= 1000  # Convert fractional seconds to milliseconds

            f.write(f"[{int(start_min):02d}:{int(start_sec):02d}:{int(start_ms):03d} --> {int(end_min):02d}:{int(end_sec):02d}:{int(end_ms):03d}] {segment['text']}\n")


if __name__ == "__main__":
    main()
