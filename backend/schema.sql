DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    following TEXT,
    followers TEXT,
    lists TEXT,
    profile TEXT  --  **This line is important - it defines the 'profile' column**
);

DROP TABLE IF EXISTS posts;
CREATE TABLE posts (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    user_id TEXT NOT NULL,
    post_type TEXT NOT NULL, -- tweet, reply, retweet, quote_tweet
    original_post_id TEXT, -- For retweets, replies, quote tweets
    quoted_content TEXT,    -- For quote tweets
    likes INTEGER DEFAULT 0,
    liked_by TEXT,        -- JSON array of user IDs who liked
    replies TEXT,         -- JSON array of reply post IDs
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (original_post_id) REFERENCES posts(id)
);

DROP TABLE IF EXISTS hashtags;
CREATE TABLE hashtags (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

DROP TABLE IF EXISTS post_hashtags;
CREATE TABLE post_hashtags (
    post_id TEXT NOT NULL,
    hashtag_id TEXT NOT NULL,
    PRIMARY KEY (post_id, hashtag_id),
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (hashtag_id) REFERENCES hashtags(id)
);

DROP TABLE IF EXISTS direct_messages;
CREATE TABLE direct_messages (
    id TEXT PRIMARY KEY,
    sender_id TEXT NOT NULL,
    receiver_id TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id)
);

DROP TABLE IF EXISTS bookmarks;
CREATE TABLE bookmarks (
    user_id TEXT NOT NULL,
    post_id TEXT NOT NULL,
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

DROP TABLE IF EXISTS mutes;
CREATE TABLE mutes (
    muter_id TEXT NOT NULL,
    muted_id TEXT NOT NULL,
    PRIMARY KEY (muter_id, muted_id),
    FOREIGN KEY (muter_id) REFERENCES users(id),
    FOREIGN KEY (muted_id) REFERENCES users(id),
    UNIQUE (muter_id, muted_id) -- Prevent duplicate mutes
);

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    following TEXT,
    followers TEXT,
    lists TEXT,
    profile TEXT,
    profile_pic TEXT  -- ADDED profile_pic column
);