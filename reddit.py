
import praw
import os
from dotenv import load_dotenv

def connect():

    # load API keys from external file
    load_dotenv( 'config.env' )

    # Authenticate your application
    reddit = praw.Reddit(
        client_id = os.getenv( 'CLIENT_ID' ),
        client_secret = os.getenv( 'CLIENT_SECRET' ),
        user_agent = os.getenv( 'USER_AGENT' ),
    )

    return reddit

def get_post( reddit ):

    # Get to the AskReddit subreddit
    subreddit = reddit.subreddit( 'AskWomen' )
    posts = subreddit.top( time_filter = 'week', limit = 1 )

    return next(posts)

def get_comments(post):

    # Fetch top comments of the post
    post.comment_sort = 'top'
    post.comments.replace_more(limit=0)

    # Filter comments with length <= 1000 characters
    filtered_comments = [comment for comment in post.comments.list() if len(comment.body) <= 1100]

    # Get the top 10 comments
    top_comments = filtered_comments[:10]

    return top_comments