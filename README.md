## Setup and Installation

1.  Clone the repository: `git clone https://github.com/fmmido/Social-App.git`
2.  Navigate to the project directory: `cd Social-App`
3.  Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
4.  Install the required packages: `pip install -r requirements.txt`
5.  Initialize the database: `python db.py init`
6.  Run the Flask application: `python app.py`

### Authentication

*   `/api/register`: Register a new user.  (POST)
*   `/api/login`: Log in an existing user. (POST)
*   `/api/logout`: Log out the current user. (POST)
*   `/api/current_user`: Get information about the currently logged-in user. (GET)

### Profile

*   `/api/user_profile/<username>`: Get user profile data (including posts). (GET)
*   `/api/edit_profile`: Update the user's profile information. (POST)
*   `/api/upload_profile_pic`: Upload a new profile picture. (POST)
*  `/api/edit_username`: Edit username  (POST)
*  `/api/change_password`: Change password (POST)

### Posts

*   `/api/create_post`: Create a new post. (POST)
*   `/api/get_posts`: Get posts for the timeline. (GET)
*  `/api/get_guest_posts`: Get all posts for guest users. (GET)


### Interactions

*   `/api/like_post`: Like a post. (POST)
*   `/api/follow_user`: Follow a user. (POST)
*   `/api/unfollow_user`: Unfollow a user. (POST)
*   `/api/send_dm`: Send a direct message. (POST)
*   `/api/get_dms`: Get direct messages for the current user. (GET)

### Other

*   `/api/trending_topics`: Get trending topics/hashtags. (GET)
*   `/api/search`: Search for posts and users. (GET)
*  `/api/bookmark`: Bookmark a post. (POST)
*  `/api/get_bookmarks`: Get bookmarks for user. (GET)
*  `/api/remove_bookmark`: Remove a bookmark. (POST)
*  `/api/mute_user`: Mute a user. (POST)
*  `/api/unmute_user`: Unmute a user. (POST)
*  `/api/get_muted_users`: Get muted user for current user. (GET)


## Contributing

Contributions are welcome! Please open an issue or submit a pull request.


## Disclaimer

This is a simplified social media application for educational purposes. It is not intended for production use.  Security measures (input sanitization, authentication, authorization) may need to be strengthened for real-world deployment.
