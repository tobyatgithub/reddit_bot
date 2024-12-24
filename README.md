# Reddit Positive Content Bot

A Python bot that collects positive and motivational content from various self-improvement subreddits.

## Features

- Collects posts from multiple self-improvement subreddits:
  - r/selfimprovement
  - r/GetMotivated
  - r/DecidingToBeBetter
  - r/productivity
  - r/MadeMeSmile
  - r/LifeProTips

- Supports different post types:
  - Hot posts
  - New posts
  - Top posts
  - Rising posts

- Stores detailed post information:
  - Post content and metadata
  - Top comments
  - Upvote ratios
  - Timestamps
  - Flairs

- Flexible storage options:
  - JSON file storage
  - Supabase database storage

## Setup

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd reddit_bot
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure the bot:
   - Copy `config/config.yaml.example` to `config/config.yaml`
   - Add your Reddit API credentials
   - (Optional) Add your Supabase credentials

4. Initialize the database (if using Supabase):
   ```sql
   -- Run these commands in your Supabase SQL editor
   CREATE TABLE posts (
       id TEXT PRIMARY KEY,
       title TEXT NOT NULL,
       author TEXT NOT NULL,
       created_utc TIMESTAMP NOT NULL,
       score INTEGER NOT NULL,
       upvote_ratio FLOAT NOT NULL,
       num_comments INTEGER NOT NULL,
       permalink TEXT NOT NULL,
       url TEXT NOT NULL,
       is_self BOOLEAN NOT NULL,
       selftext TEXT,
       link_flair_text TEXT,
       subreddit TEXT NOT NULL,
       collected_at TIMESTAMP NOT NULL DEFAULT now(),
       last_updated TIMESTAMP
   );

   CREATE TABLE comments (
       id TEXT PRIMARY KEY,
       post_id TEXT NOT NULL REFERENCES posts(id),
       author TEXT NOT NULL,
       body TEXT NOT NULL,
       score INTEGER NOT NULL,
       created_utc TIMESTAMP NOT NULL,
       collected_at TIMESTAMP NOT NULL DEFAULT now()
   );
   ```

## Usage

1. Basic usage:
   ```python
   from src.bot import RedditBot

   bot = RedditBot()

   # Fetch and save posts from multiple subreddits
   subreddits = ["selfimprovement", "GetMotivated"]
   for subreddit in subreddits:
       posts = bot.save_subreddit_posts(subreddit, limit=5)
   ```

2. Migrate data from JSON to Supabase:
   ```bash
   python src/migrate_to_supabase.py
   ```

## Project Structure

```
reddit_bot/
├── src/
│   ├── bot.py              # Main bot implementation
│   ├── migrate_to_supabase.py  # Data migration script
│   └── storage/            # Storage implementations
│       ├── base.py         # Abstract storage interface
│       ├── json_storage.py # JSON file storage
│       └── supabase_storage.py  # Supabase storage
├── data/                   # Local data storage
├── config/                 # Configuration files
└── requirements.txt        # Project dependencies
```

## Dependencies

- PRAW (Python Reddit API Wrapper)
- Supabase Python Client
- PyYAML
- pandas

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License Here]
