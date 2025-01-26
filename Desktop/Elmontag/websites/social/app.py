from flask import Flask, render_template, request, redirect, flash, session, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret_key_for_session"

# Database and upload configurations
DATABASE = "users.db"
UPLOAD_FOLDER = "static/avatars"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER



# Routes
@app.route("/", methods=["GET", "POST"])
def index():
    tweets = []
    if request.method == "POST" and session.get("username"):
        # Handle tweet submission
        content = request.form["tweet"]
        if content.strip():
            user_id = session["user_id"]
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO tweets (user_id, content) VALUES (?, ?)", (user_id, content))
                conn.commit()
            flash("Tweet posted successfully!", "success")
        else:
            flash("Tweet cannot be empty.", "danger")
        return redirect(url_for("index"))

    # Fetch all tweets for timeline
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tweets.content, tweets.created_at, users.username
            FROM tweets
            JOIN users ON tweets.user_id = users.id
            ORDER BY tweets.created_at DESC
        """)
        tweets = cursor.fetchall()

    return render_template("index.html", tweets=tweets)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                flash("Registration successful! Please log in.", "success")
                return redirect('/login')
            except sqlite3.IntegrityError:
                flash("Username already exists.", "danger")
    return render_template('register.html', current_page='register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            if user:
                session['username'] = username
                session['user_id'] = user[0]
                flash("Login successful!", "success")
                return redirect('/')
            else:
                flash("Invalid username or password.", "danger")
    return render_template('login.html', current_page='login')


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    flash("You have been logged out.", "success")
    return redirect('/')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        flash("Please log in to access the profile page.", "danger")
        return redirect('/login')

    user_id = session['user_id']
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, avatar FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']
        avatar = request.files.get('avatar')

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()

            # Update username
            if new_username and new_username != user[0]:
                try:
                    cursor.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, user_id))
                    session['username'] = new_username
                    flash("Username updated successfully!", "success")
                except sqlite3.IntegrityError:
                    flash("Username already exists.", "danger")

            # Update password
            if new_password:
                cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))
                flash("Password updated successfully!", "success")

            # Save avatar
            if avatar and avatar.filename != "":
                filename = secure_filename(avatar.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                avatar.save(filepath)
                cursor.execute("UPDATE users SET avatar = ? WHERE id = ?", (filename, user_id))
                flash("Avatar updated successfully!", "success")

            conn.commit()

        return redirect('/profile')

    return render_template('profile.html', user={"username": user[0], "avatar": user[1]})

@app.route('/tweets', methods=['GET', 'POST'])
def tweets():
    if 'username' not in session:
        flash("Please log in to view tweets.", "danger")
        return redirect('/login')

    user_id = session['user_id']
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            content = request.form['content']
            if content.strip():
                cursor.execute("INSERT INTO tweets (user_id, content) VALUES (?, ?)", (user_id, content))
                conn.commit()
                flash("Tweet posted successfully!", "success")
            else:
                flash("Tweet cannot be empty.", "danger")

        # Fetch all tweets (newest first)
        cursor.execute("""
            SELECT tweets.id, users.username, tweets.content, tweets.created_at
            FROM tweets
            JOIN users ON tweets.user_id = users.id
            ORDER BY tweets.created_at DESC
        """)
        all_tweets = cursor.fetchall()

    return render_template('tweets.html', tweets=all_tweets)


@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if 'username' not in session:
        flash("Please log in to view messages.", "danger")
        return redirect('/login')

    user_id = session['user_id']
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            receiver_username = request.form['receiver']
            content = request.form['content']
            if content.strip():
                # Get receiver ID
                cursor.execute("SELECT id FROM users WHERE username = ?", (receiver_username,))
                receiver = cursor.fetchone()
                if receiver:
                    receiver_id = receiver[0]
                    cursor.execute("INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)", 
                                   (user_id, receiver_id, content))
                    conn.commit()
                    flash("Message sent successfully!", "success")
                else:
                    flash("User not found.", "danger")
            else:
                flash("Message cannot be empty.", "danger")

        # Fetch messages (sent and received)
        cursor.execute("""
            SELECT messages.id, users.username AS sender, messages.content, messages.created_at
            FROM messages
            JOIN users ON messages.sender_id = users.id
            WHERE messages.receiver_id = ?
            ORDER BY messages.created_at DESC
        """, (user_id,))
        received_messages = cursor.fetchall()

        cursor.execute("""
            SELECT messages.id, users.username AS receiver, messages.content, messages.created_at
            FROM messages
            JOIN users ON messages.receiver_id = users.id
            WHERE messages.sender_id = ?
            ORDER BY messages.created_at DESC
        """, (user_id,))
        sent_messages = cursor.fetchall()

    return render_template('messages.html', received=received_messages, sent=sent_messages)


if __name__ == '__main__':
    app.run(debug=True)
