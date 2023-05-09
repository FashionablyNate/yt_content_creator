import praw
import os
from dotenv import load_dotenv

# load API keys from external file
load_dotenv( 'config.env' )
client_id = os.getenv( 'CLIENT_ID' )
client_secret = os.getenv( 'CLIENT_SECRET' )
user_agent = os.getenv( 'USER_AGENT' )

# Authenticate your application
reddit = praw.Reddit(
    client_id = client_id,
    client_secret = client_secret,
    user_agent = user_agent
)

# Get a random subreddit
random_subreddit = reddit.random_subreddit( nsfw=False )

# Fetch random posts from the subreddit
random_posts = random_subreddit.random_rising( limit=10 )

# Process the posts
for post in random_posts:
    print( post.title )
    print( post.url )
    print( '---' )