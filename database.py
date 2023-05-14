import sqlite3

# Function to check if a video ID already exists
def video_exists(video_id):
    # Connect to the database (creates a new file if it doesn't exist)
    conn = sqlite3.connect('videos.db')

    # Create a cursor object to execute SQL statements
    cursor = conn.cursor()

    # Create a table to store video IDs if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id TEXT PRIMARY KEY
        )
    ''')
    cursor.execute('SELECT * FROM videos WHERE id=?', (video_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None

# Function to insert a new video ID
def insert_video(video_id):
    # Connect to the database (creates a new file if it doesn't exist)
    conn = sqlite3.connect('videos.db')

    # Create a cursor object to execute SQL statements
    cursor = conn.cursor()

    # Create a table to store video IDs if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id TEXT PRIMARY KEY
        )
    ''')
    cursor.execute('INSERT INTO videos VALUES (?)', (video_id,))
    conn.commit()
    cursor.close()
    conn.close()