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

# Get to the AskReddit subreddit
subreddit = reddit.subreddit( 'AskReddit' )

# Fetch top posts from the subreddit
top_posts = subreddit.top( time_filter='all', limit=10 )

# Process the posts
for post in top_posts:
    print("Title:", post.title)
    print("Content:", post.selftext)  # Retrieve the content of the post
    print("URL:", post.url)
    print("---")

    # Fetch top comments of the post

    post.comment_sort = 'top'
    post.comment_limit = 5
    post.comments.replace_more(limit=0)

    # Process the top comments
    for comment in post.comments.list():
        print("Comment:", comment.body)  # Retrieve the content of the comment
        print("Score:", comment.score)
        print("---")