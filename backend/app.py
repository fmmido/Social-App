from flask import Flask, request, jsonify, send_from_directory, session, render_template, url_for
from flask_cors import CORS
import json
import datetime
import os
from uuid import uuid4
from functools import wraps
import sqlite3
import re  # For hashtag extraction
from db import get_db_connection, init_db  # Import database functions
import hashlib
from werkzeug.utils import secure_filename # Import secure_filename at the top of app.py
from flask import g #import g


app = Flask(__name__, static_folder='static', template_folder='../frontend') # Set template folder
upload_folder = os.path.join(app.static_folder, 'profile_pics')
os.makedirs(upload_folder, exist_ok=True)  # Create the directory if it doesn't exist


CORS(app)
app.secret_key = "my_super_secret_key"

# Initialize database
init_db()

# Serve files from the /frontend folder
@app.route('/frontend/<path:filename>')
def serve_frontend(filename):
    return send_from_directory('../frontend', filename)

# Helper function to find a user by ID
def find_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# Helper function to find a user by username
def find_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# Helper function to find a post by ID
def find_post(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    conn.close()
    return post
# Hash Password
def hash_password(password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password
# Decorator to check if a user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Helper Function to extract hashtags
def extract_hashtags(text):
    return re.findall(r"#(\w+)", text)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if find_user_by_username(username):
        return jsonify({"error": "Username already exists"}), 409
    hashed_password = hash_password(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = str(uuid4())
    try:
        cursor.execute("INSERT INTO users (id, username, password, following, followers, lists, profile, profile_pic) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (user_id, username, hashed_password, '[]', '[]', '[]', '{}', None)) # Initial profile_pic as None
        conn.commit()
        print(f"User '{username}' registered successfully. User ID: {user_id}")
        return jsonify({"message": "User registered", "userId": user_id}), 201 # Return success jsonify inside try
    except sqlite3.IntegrityError as integrity_err:
        conn.close()
        print(f"IntegrityError during registration for user '{username}': {integrity_err}") # Log IntegrityError
        return jsonify({"error": "Username already exists"}), 409
    except sqlite3.Error as db_err: # Catch other sqlite3.Error exceptions
        conn.close()
        print(f"Database error during registration for user '{username}': {db_err}") # Log general DB error
        return jsonify({"error": "Database error during registration"}), 500 # Return 500 for DB errors
    except Exception as e: # Catch any other unexpected exceptions
        conn.close()
        print(f"Unexpected error during registration for user '{username}': {e}") # Log unexpected error
        return jsonify({"error": "Unexpected error during registration"}), 500
    finally: # Ensure connection is closed in all cases
        if conn: # Check if connection is still open before closing
            conn.close()


# Serve User Profile Pages
@app.route('/profile/')
def profile_home():
    return render_template('profile.html', user_profile=None, error="No username provided")

@app.route('/profile/<username>')
def serve_profile_page(username):
    user = find_user_by_username(username)
    if not user:
        return render_template('profile.html', user_profile=None, error="User not found")
    user_profile_data = dict(user)
    user_profile_data['profile'] = json.loads(user_profile_data['profile']) if user_profile_data['profile'] else {}
    return render_template('profile.html', user_profile=user_profile_data)


# User Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = find_user_by_username(username)
    if not user or hash_password(password) != user['password']:
         return jsonify({"error": "Invalid credentials"}), 401

    session['user_id'] = user['id']
    return jsonify({"message": "Login successful", "userId": user['id']}), 200

# User Logout
@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logout successful"}), 200

# Get Current User
@app.route('/api/current_user', methods=['GET'])
def get_current_user():
     if 'user_id' in session:
        user = find_user(session['user_id'])
        if user:
             return jsonify({"userId": user['id'], "username": user['username'], "profile": json.loads(user["profile"])}), 200
     return jsonify({"user": None}), 401

# Edit User profile
@app.route('/api/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    data = request.get_json()
    user_id = session['user_id']
    profile = data.get('profile')

    if not profile:
        return jsonify({"error": "Profile is required"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET profile = ? WHERE id = ?", (json.dumps(profile), user_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Profile Updated Successfully", "profile": profile}), 200

# Create a Tweet
@app.route('/api/create_post', methods=['POST'])
@login_required
def create_post():
    data = request.get_json()
    content = data.get('content')
    user_id = session['user_id']
    post_type = data.get('post_type', 'tweet')
    original_post_id = data.get('original_post_id')
    quoted_content = data.get('quoted_content')

    if not content:
        return jsonify({"error": "Content is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    post_id = str(uuid4())
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute("INSERT INTO posts (id, content, timestamp, user_id, post_type, original_post_id, quoted_content, liked_by, replies) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (post_id, content, timestamp, user_id, post_type, original_post_id, quoted_content, '[]', '[]'))
    conn.commit()

    # Handle Hashtags
    hashtags = extract_hashtags(content)
    for tag in hashtags:
        # Check if the hashtag exists or create it
        cursor.execute("SELECT id FROM hashtags WHERE name = ?", (tag,))
        hashtag_record = cursor.fetchone()
        if not hashtag_record:
            hashtag_id = str(uuid4())
            cursor.execute("INSERT INTO hashtags (id, name) VALUES (?, ?)", (hashtag_id, tag))
            conn.commit()
        else:
            hashtag_id = hashtag_record['id']
        # Create relation between post and hashtag
        cursor.execute("INSERT INTO post_hashtags (post_id, hashtag_id) VALUES (?, ?)", (post_id, hashtag_id))
        conn.commit()

    conn.close()
    return jsonify({"message": "Post Created", "postId": post_id}), 201

# Retweet a Post
@app.route('/api/retweet', methods=['POST'])
@login_required
def retweet():
    data = request.get_json()
    user_id = session['user_id']
    original_post_id = data.get('original_post_id')

    original_post = find_post(original_post_id)
    if not original_post:
        return jsonify({"error": "Original post not found"}), 404

    conn = get_db_connection()
    cursor = conn.cursor()
    post_id = str(uuid4())
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute("INSERT INTO posts (id, content, timestamp, user_id, post_type, original_post_id, liked_by, replies) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (post_id, "", timestamp, user_id, "retweet", original_post_id, '[]', '[]'))
    conn.commit()
    conn.close()
    return jsonify({"message": "Retweeted", "post": find_post(post_id)}), 201

# Quote Tweet
@app.route('/api/quote_tweet', methods=['POST'])
@login_required
def quote_tweet():
    data = request.get_json()
    user_id = session['user_id']
    original_post_id = data.get('original_post_id')
    quoted_content = data.get('quoted_content')

    original_post = find_post(original_post_id)
    if not original_post:
        return jsonify({"error": "Original post not found"}), 404

    conn = get_db_connection()
    cursor = conn.cursor()
    post_id = str(uuid4())
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute("INSERT INTO posts (id, content, timestamp, user_id, post_type, original_post_id, quoted_content, liked_by, replies) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (post_id, quoted_content, timestamp, user_id, "quote_tweet", original_post_id, quoted_content, '[]', '[]'))
    conn.commit()
    conn.close()
    return jsonify({"message": "Quote Tweet Created", "post": find_post(post_id)}), 201

# Reply to a Post
@app.route('/api/reply', methods=['POST'])
@login_required
def reply():
    data = request.get_json()
    user_id = session['user_id']
    original_post_id = data.get('original_post_id')
    content = data.get('content')

    original_post = find_post(original_post_id)
    if not original_post:
        return jsonify({"error": "Original post not found"}), 404

    conn = get_db_connection()
    cursor = conn.cursor()
    post_id = str(uuid4())
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute("INSERT INTO posts (id, content, timestamp, user_id, post_type, original_post_id, liked_by, replies) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (post_id, content, timestamp, user_id, "reply", original_post_id, '[]', '[]'))
    conn.commit()
     # Update original post to include this reply
    replies = json.loads(original_post['replies']) if original_post['replies'] else []
    replies.append(post_id)
    cursor.execute("UPDATE posts SET replies = ? WHERE id = ?", (json.dumps(replies), original_post_id))
    conn.commit()

    conn.close()
    return jsonify({"message": "Reply Created", "post": find_post(post_id)}), 201

# Like a Post
@app.route('/api/like_post', methods=['POST'])
@login_required
def like_post():
    data = request.get_json()
    post_id = data.get('post_id')
    user_id = session['user_id']

    post = find_post(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    liked_by = json.loads(post['liked_by']) if post['liked_by'] else []
    if user_id in liked_by:
        return jsonify({"error": "Post already liked by user"}), 400

    liked_by.append(user_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE posts SET likes = likes + 1, liked_by = ? WHERE id = ?", (json.dumps(liked_by), post_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Post liked", "post": find_post(post_id)}), 200

# Follow a User
@app.route('/api/follow_user', methods=['POST'])
@login_required
def follow_user():
    data = request.get_json()
    user_id = session['user_id']
    follow_id = data.get('follow_id')

    user = find_user(user_id)
    follow_user = find_user(follow_id)

    if not user or not follow_user:
        return jsonify({"error": "User not found"}), 404

    following = json.loads(user['following']) if user['following'] else []
    followers = json.loads(follow_user['followers']) if follow_user['followers'] else []

    if follow_id in following:
        return jsonify({"error": "Already following this user"}), 400

    following.append(follow_id)
    followers.append(user_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET following = ? WHERE id = ?", (json.dumps(following), user_id))
    cursor.execute("UPDATE users SET followers = ? WHERE id = ?", (json.dumps(followers), follow_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "User followed", "following": following}), 200

# Unfollow a User
@app.route('/api/unfollow_user', methods=['POST'])
@login_required
def unfollow_user():
    data = request.get_json()
    user_id = session['user_id']
    unfollow_id = data.get('unfollow_id')

    user = find_user(user_id)
    unfollow_user = find_user(unfollow_id)

    if not user or not unfollow_user:
        return jsonify({"error": "User not found"}), 404

    following = json.loads(user['following']) if user['following'] else []
    followers = json.loads(unfollow_user['followers']) if unfollow_user['followers'] else []

    if unfollow_id not in following:
         return jsonify({"error": "Not following this user"}), 400

    following.remove(unfollow_id)
    followers.remove(user_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET following = ? WHERE id = ?", (json.dumps(following), user_id))
    cursor.execute("UPDATE users SET followers = ? WHERE id = ?", (json.dumps(followers), unfollow_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "User unfollowed", "following": following}), 200

# Get Posts (Timeline)
@app.route("/api/get_posts")
def get_posts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            posts.*,
            users.username,
            users.profile_pic  -- Select profile_pic from users table
        FROM
            posts
        JOIN
            users ON posts.user_id = users.id  -- Join based on user_id
        ORDER BY
            timestamp DESC
    """)
    posts = cursor.fetchall()
    conn.close()

    # Format the results to include username and profile_pic in each post dictionary
    formatted_posts = []
    for post in posts:
        post_dict = dict(post) # Convert row (sqlite3.Row) to a dictionary
        post_dict['username'] = post['username'] # Add the username to the dictionary
        post_dict['profile_pic'] = post['profile_pic'] # Add the profile_pic to the dictionary
        formatted_posts.append(post_dict)

    return jsonify(formatted_posts)

# Get User Profile by Username
@app.route('/api/user_profile/<username>', methods=['GET'])
def get_user_profile(username):
    user = find_user_by_username(username)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Fetch user's posts (you can customize this query as needed)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM posts
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """, (user['id'],))
    user_posts = cursor.fetchall()
    conn.close()

    # Format user data and posts for response
    user_profile_data = dict(user) # Convert user row to dict
    user_profile_data['profile'] = json.loads(user_profile_data['profile']) if user_profile_data['profile'] else {} # Parse profile JSON
    user_profile_data['posts'] = [dict(post) for post in user_posts] # Format user's posts

    return jsonify(user_profile_data), 200

# Upload Profile Picture
import os
from werkzeug.utils import secure_filename

@app.route('/api/upload_profile_pic', methods=['POST'])
@login_required
def upload_profile_pic():
    if 'profile_pic' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['profile_pic']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        # Ensure the 'profile_pics' directory exists
        upload_folder = os.path.join(app.static_folder, 'profile_pics')
        os.makedirs(upload_folder, exist_ok=True)

        # Sanitize the filename
        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_folder, filename)

        # Save the file
        file.save(filepath)

        # Generate the URL for the uploaded file
        profile_pic_url = url_for('static', filename=f'profile_pics/{filename}', _external=True)

        # Debugging: Print file path and URL
        print("Upload folder:", upload_folder)
        print("File path:", filepath)
        print("Profile picture URL:", profile_pic_url)

        # Update the user's profile picture in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        user_id = session['user_id']
        try:
            cursor.execute("UPDATE users SET profile_pic = ? WHERE id = ?", (profile_pic_url, user_id))
            conn.commit()
            return jsonify({"message": "Profile picture uploaded successfully", "profilePicUrl": profile_pic_url}), 200
        except sqlite3.Error as db_err:
            conn.close()
            os.remove(filepath)  # Remove the uploaded file on DB error
            return jsonify({"error": "Database error during profile picture update"}), 500
        except Exception as e:
            conn.close()
            os.remove(filepath)  # Remove the uploaded file on unexpected error
            return jsonify({"error": "Unexpected error during profile picture upload"}), 500
        finally:
            if conn:
                conn.close()
    else:
        return jsonify({"error": "Invalid file"}), 400
    

# Edit Username
@app.route('/api/edit_username', methods=['POST'])
@login_required
def edit_username():
    data = request.get_json()
    new_username = data.get('new_username')
    user_id = session['user_id']

    if not new_username:
        return jsonify({"error": "New username is required"}), 400

    if find_user_by_username(new_username):
        return jsonify({"error": "Username already taken"}), 409 # 409 Conflict if username exists

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, user_id))
        conn.commit()
        print(f"Username updated successfully for user ID: {user_id} to '{new_username}'") # Success log
    except sqlite3.Error as db_err:
        conn.close()
        print(f"Database error during username update for user ID '{user_id}': {db_err}") # Log DB error
        return jsonify({"error": "Database error during username update"}), 500
    except Exception as e:
        conn.close()
        print(f"Unexpected error during username update for user ID '{user_id}': {e}") # Log unexpected error
        return jsonify({"error": "Unexpected error during username update"}), 500
    finally:
        if conn:
            conn.close()

    return jsonify({"message": "Username updated successfully", "username": new_username}), 200

# Change Password
@app.route('/api/change_password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    new_password = data.get('new_password')
    user_id = session['user_id']

    if not new_password:
        return jsonify({"error": "New password is required"}), 400

    hashed_password = hash_password(new_password) # Hash the new password

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
        conn.commit()
        print(f"Password changed successfully for user ID: {user_id}") # Success log
    except sqlite3.Error as db_err:
        conn.close()
        print(f"Database error during password change for user ID '{user_id}': {db_err}") # Log DB error
        return jsonify({"error": "Database error during password change"}), 500
    except Exception as e:
        conn.close()
        print(f"Unexpected error during password change for user ID '{user_id}': {e}") # Log unexpected error
        return jsonify({"error": "Unexpected error during password change"}), 500
    finally:
        if conn:
            conn.close()

    return jsonify({"message": "Password changed successfully"}), 200


# Guest Access to posts
@app.route('/api/get_guest_posts', methods=['GET'])
def get_guest_posts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY timestamp DESC")
    posts = cursor.fetchall()
    conn.close()
    return jsonify([dict(post) for post in posts])

# GET Trending Topics
@app.route('/api/trending_topics', methods=['GET'])
def get_trending_topics():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Simplified trending, can be improved with real algorithms
    cursor.execute("""
    SELECT h.name, COUNT(ph.hashtag_id) AS count
    FROM hashtags h
    JOIN post_hashtags ph ON h.id = ph.hashtag_id
    GROUP BY h.name
    ORDER BY count DESC
    LIMIT 10
    """)
    trending = cursor.fetchall()
    conn.close()
    return jsonify([dict(tag) for tag in trending])

# Spaces Placeholder
@app.route('/api/spaces', methods=['GET'])
def get_spaces():
    return jsonify({"message": "Spaces data here"}), 200

# Search posts and users
@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('query', '').lower()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Search Posts
    cursor.execute("SELECT * FROM posts WHERE LOWER(content) LIKE ?", ('%' + query + '%',))
    posts = cursor.fetchall()

    # Search Users
    cursor.execute("SELECT * FROM users WHERE LOWER(username) LIKE ?", ('%' + query + '%',))
    users = cursor.fetchall()
    conn.close()

    return jsonify({
        "posts": [dict(post) for post in posts],
        "users": [dict(user) for user in users]
    })

# Bookmarks
@app.route('/api/bookmark_post', methods=['POST'])
@login_required
def bookmark_post():
   data = request.get_json()
   post_id = data.get('post_id')
   user_id = session['user_id']

   conn = get_db_connection()
   cursor = conn.cursor()
   try:
       cursor.execute("INSERT INTO bookmarks (user_id, post_id) VALUES (?, ?)", (user_id, post_id))
       conn.commit()
       conn.close()
       return jsonify({"message": "Post bookmarked successfully"}), 200
   except sqlite3.IntegrityError:
       conn.close()
       return jsonify({"error": "Post already bookmarked"}), 400

# Get Bookmarks
@app.route('/api/get_bookmarks', methods=['GET'])
@login_required
def get_bookmarks():
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*
        FROM posts p
        JOIN bookmarks b ON p.id = b.post_id
        WHERE b.user_id = ?
        ORDER BY p.timestamp DESC
    """, (user_id,))
    bookmarks = cursor.fetchall()
    conn.close()
    return jsonify([dict(bookmark) for bookmark in bookmarks])

# Remove Bookmarks
@app.route('/api/remove_bookmark', methods=['POST'])
@login_required
def remove_bookmark():
    data = request.get_json()
    post_id = data.get('post_id')
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookmarks WHERE user_id = ? AND post_id = ?", (user_id, post_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Bookmark removed"}), 200

# Mute a User
@app.route('/api/mute_user', methods=['POST'])
@login_required
def mute_user():
    data = request.get_json()
    muter_id = session['user_id']
    muted_id = data.get('muted_id')

    if not find_user(muted_id):
        return jsonify({"error": "User to mute not found"}), 404

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO mutes (muter_id, muted_id) VALUES (?, ?)", (muter_id, muted_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "User muted"}), 200
    except sqlite3.IntegrityError:
         conn.close()
         return jsonify({"error": "User already muted"}), 400

# Unmute a User
@app.route('/api/unmute_user', methods=['POST'])
@login_required
def unmute_user():
    data = request.get_json()
    muter_id = session['user_id']
    muted_id = data.get('muted_id')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mutes WHERE muter_id = ? AND muted_id = ?", (muter_id, muted_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "User unmuted"}), 200

# Get muted user IDs
@app.route('/api/get_muted_users', methods=['GET'])
@login_required
def get_muted_users():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT muted_id FROM mutes WHERE muter_id = ?", (user_id,))
    muted_users = cursor.fetchall()
    conn.close()
    return jsonify({"mutedUsers":[dict(user)['muted_id'] for user in muted_users]}), 200

# Moments (Placeholder)
@app.route('/api/moments', methods=['GET'])
def get_moments():
    return jsonify({"message": "Moments data here"}), 200

# Analytics (Placeholder)
@app.route('/api/analytics', methods=['GET'])
@login_required
def get_analytics():
    return jsonify({"message": "Analytics data here"}), 200

# Polls (Placeholder)
@app.route('/api/polls', methods=['GET'])
@login_required
def get_polls():
    return jsonify({"message": "Polls data here"}), 200

# Notifications (Placeholder)
@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    return jsonify({"message": "Notifications data here"}), 200

# Serve Frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    elif path == "":
        return render_template('index.html')
    else:
        return "404 - Page Not Found", 404
    

@app.route('/direct_messages')
@login_required
def direct_messages():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    all_users = cursor.fetchall()
    conn.close()

    return render_template('direct_messages.html', all_users=all_users, current_user=find_user(session['user_id']))

#New route for getting users:

@app.route('/api/users')
@login_required  # Protect this route if needed
def get_users():
  conn = get_db_connection()
  cursor = conn.cursor()
  cursor.execute("SELECT id, username FROM users") # Query to get all users
  users = [dict(user) for user in cursor.fetchall()]  #Convert to a list of dictionaries
  conn.close()

  return jsonify({'users': users})

#Modified get_dms route
@app.route('/api/get_dms')
@login_required
def get_dms():
    user_id = session['user_id']
    receiver_id = request.args.get('receiver_id') # Get the receiver ID from query parameters


    conn = get_db_connection()
    cursor = conn.cursor()
    if receiver_id:
      cursor.execute("""
           SELECT dm.*, sender.username as sender_username  FROM direct_messages dm
           JOIN users sender on sender.id=dm.sender_id
           WHERE (dm.sender_id = ? AND dm.receiver_id = ?) OR (dm.sender_id = ? AND dm.receiver_id = ?)
           ORDER BY dm.timestamp
       """, (user_id, receiver_id, receiver_id, user_id))#Get messages for the selected chat

    else:

       cursor.execute("SELECT * FROM direct_messages WHERE sender_id = ? OR receiver_id = ? ORDER BY timestamp DESC", (user_id, user_id))#get all user's dms
    dms = cursor.fetchall()
    conn.close()
    return jsonify([dict(dm) for dm in dms])


#updated send_dm route
@app.route('/api/send_dm', methods=['POST'])
@login_required
def send_dm():
    data = request.get_json()
    sender_id = session['user_id']
    receiver_id = data.get('receiver_username') # receiver_username now holds the receiver's ID
    content = data.get('content')

    if not receiver_id or not content:
        return jsonify({"error": "Receiver ID and content are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    dm_id = str(uuid4())
    timestamp = datetime.datetime.now().isoformat()

    cursor.execute("INSERT INTO direct_messages (id, sender_id, receiver_id, content, timestamp) VALUES (?, ?, ?, ?, ?)",
                   (dm_id, sender_id, receiver_id, content, timestamp))

    conn.commit()
    conn.close()
    return jsonify({"message": "Direct message sent", "dmId": dm_id}), 201

@app.route('/')
def index():
    current_user = None  
    if 'user_id' in session:
        current_user = find_user(session.get('user_id'))
    return render_template('index.html', current_user=current_user)

@app.context_processor
def inject_current_user():
    current_user = None
    if 'user_id' in session:
        current_user = find_user(session['user_id'])
    return dict(current_user=current_user)
    
    

@app.route('/test_template')
def test_template():
    return render_template('test.html')

if __name__ == '__main__':
    print(" * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)")
    app.run(debug=True, port=5000)
