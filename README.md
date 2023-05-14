# Reddit Video Generator

The Reddit Video Generator is a Python script that generates videos from Reddit posts and their comments. It utilizes the Reddit API, text-to-speech (TTS) synthesis, video editing, and YouTube Data API to create and upload videos to YouTube.

## Features

Fetches top posts from selected subreddits.
Generates audio from the post title and body using TTS synthesis.
Takes screenshots of the post and comment threads using the Playwright library.
Creates a video by combining the post audio, screenshots, and comment audio.
Uploads the generated video to YouTube using the YouTube Data API.

## Requirements

- Python 3.7 or higher
- Playwright
- TTS (Text-to-Speech)
- MoviePy
- PyDub
- Better Profanity
- Pillow
- Praw (Python Reddit API Wrapper)
- Num2words
- httplib2
- Google API Python Client

## Installation

Clone the repository:

```sh
git clone https://github.com/FashionablyNate/yt_content_creator.git
```
Install the required dependencies:
```sh
pip install -r requirements.txt
```
Set up the necessary API credentials:
Reddit API credentials: Obtain the client ID, client secret, and user agent by creating a Reddit developer application. Set these credentials in the config.env file.
YouTube API credentials: Follow the instructions in the YouTube Data API documentation to create and obtain the necessary credentials. Place the client_secrets.json file in the project directory.

## Usage

Run the main.py script:
```sh
python main.py
```
Select the subreddit from which you want to fetch posts.
The script will fetch the top posts from the selected subreddit, generate audio from the post titles and bodies, take screenshots of the post and comment threads, create a video by combining the audio and screenshots, and upload the video to YouTube.
The generated video will be uploaded to your YouTube channel with the specified title, description, and privacy settings.

## Limitations

The script may encounter issues with certain post or comment formats that deviate from the expected structure.

## Contributing

Contributions to the Reddit Video Generator project are welcome. If you find any issues or have ideas for improvements, please submit an issue or pull request.

## License

This project is licensed under the GPLv3 License.

Feel free to customize and modify the code to suit your needs.
