# Code Readme

This code consists of several functions that are used to create videos from Reddit posts and their comments. The main workflow of the code is as follows:

Connect to the Reddit API using the connect() function.
Fetch the top posts from a chosen subreddit using the get_post() function.
For each post:
Check if a video with the same ID already exists in the database using the video_exists() function.
If a video already exists, skip the post.
If a video does not exist, create a video from the post and its selected comments using the create_video() function.
Insert the video ID into the database using the insert_video() function.
Upload the video to YouTube using the get_authenticated_service() and initialize_upload() functions.
Below is a detailed explanation of each function:

1. connect()

This function is used to connect to the Reddit API using the PRAW library. It reads the API keys from an external file and returns the authenticated Reddit instance.

2. get_post()

This function fetches the top posts from a chosen subreddit using the authenticated Reddit instance. It takes the subreddit name as input and returns the list of posts and the formatted subreddit name.

3. get_comments()

This function fetches the top comments of a given post. It takes the post object as input and returns a list of comments.

4. create_video()

This function creates a video from a given post and its selected comments. It takes the post object and the list of selected comments as input. The function performs the following steps:

Generate the audio for the post and selected comments using the generate_audio() function.
Concatenate the audio clips of the post and selected comments using the concatenate_audioclips() function from the moviepy.editor library.
Load the input video file using the VideoFileClip() function from the moviepy.editor library.
Set the start time of the video randomly within the duration of the input video.
Crop the video to the desired aspect ratio and size using the crop() method of the VideoFileClip object.
Create video clips for each audio clip using the create_video_clips() function.
Concatenate the video clips using the concatenate_videoclips() function.
Set the audio of the final video using the set_audio() method of the CompositeVideoClip object.
Calculate the bitrate based on the height of the video using the calculate_bitrate() function.
Write the final video file using the write_videofile() method of the CompositeVideoClip object.
5. generate_audio()

This function converts text to speech using the TTS (Text-to-Speech) library. It takes the text, ID, and post ID as input and returns the path to the generated audio file. The function performs the following steps:

Download the TTS model using the ModelManager class from the TTS.utils.manage module.
Initialize the TTS synthesizer using the downloaded model.
Normalize the text by expanding contractions, normalizing numbers, censoring profanity, and normalizing punctuation using the normalize_text() function.
Generate audio from the normalized text using the tts() method of the Synthesizer object.
Save the generated audio as a WAV file using the save_wav() method of the Synthesizer object.
Convert the WAV file to MP3 format using the AudioSegment class from the pydub library.
Delete the WAV file to save space.

6. normalize_text()

This function normalizes the text by expanding contractions, normalizing numbers, censoring profanity, and normalizing punctuation. It takes the text as input and returns the normalized text.

7. take_screenshot_post()

This function takes a screenshot of a Reddit post using the Playwright library. It takes the post object as input and returns the path to the screenshot image file. The function performs the following steps:

Launch a Playwright browser instance.
Navigate to the Reddit post URL.
Wait for the target post to be present on the page.
Get the target post using the provided selector.
Get the inner HTML of the title and body elements of the post.
Censor profanity in the title and body HTML.
Set the censored HTML back to the title and body elements.
Take a screenshot of the post using the screenshot() method of the target post element.
Close the browser instance.
8. take_screenshot_comment()

This function takes a screenshot of a Reddit comment using the Playwright library. It takes the post and comment objects as input and returns the path to the screenshot image file. The function performs the following steps:

Launch a Playwright browser instance.
Navigate to the Reddit comment URL.
Wait for the target comment to be present on the page.
Get the inner HTML of the comment.
Censor profanity in the comment HTML.
Set the censored HTML back to the comment element.
Take a screenshot of the comment using the screenshot() method of the target comment element.
Close the browser instance.
9. get_authenticated_service() and initialize_upload()

These two functions are used to authenticate the YouTube Data API and upload the generated video to YouTube. They use the Google API client libraries and the OAuth2 authentication process. The get_authenticated_service() function returns the authenticated YouTube service object, while the initialize_upload() function takes the YouTube service object, file path, and other metadata (such as title, description, and privacy status) as input and uploads the video to YouTube.

Overall, this code provides a framework for generating videos from Reddit posts and their comments and uploading them to YouTube. It utilizes various libraries and APIs to accomplish these tasks.
