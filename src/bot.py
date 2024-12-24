from pathlib import Path

import praw
import prawcore
import yaml


class RedditBot:
    def __init__(self, config_path: str = "../config/config.yaml"):
        self.config = self._load_config(config_path)
        self.reddit = self._initialize_reddit()
        self._test_authentication()  # Add authentication test

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found at {config_path}")

        with open(config_path, "r") as file:
            return yaml.safe_load(file)

    def _initialize_reddit(self) -> praw.Reddit:
        """Initialize Reddit API client."""
        return praw.Reddit(
            client_id=self.config["reddit"]["client_id"],
            client_secret=self.config["reddit"]["client_secret"],
            user_agent=self.config["reddit"]["user_agent"],
            username=self.config["reddit"]["username"],
            password=self.config["reddit"]["password"],
        )

    def _test_authentication(self):
        """Test if authentication is working."""
        try:
            # This will fail if authentication is incorrect
            self.reddit.user.me()
            print("Authentication successful!")
        except prawcore.exceptions.OAuthException as e:
            print("Authentication failed!")
            print("Please verify your credentials in config.yaml")
            print(f"Error: {str(e)}")
            raise

    def get_subreddit_hot_posts(self, subreddit_name: str, limit: int = 10):
        """Fetch hot posts from a specified subreddit."""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            return list(subreddit.hot(limit=limit))
        except prawcore.exceptions.OAuthException as e:
            print(f"Authentication error: {e}")
            raise
        except Exception as e:
            print(f"Error fetching posts: {e}")
            raise

    def get_post_comments(self, post_id: str, limit: int = None):
        """Fetch comments from a specific post."""
        submission = self.reddit.submission(id=post_id)
        submission.comments.replace_more(limit=None)  # Expand all comment trees
        return submission.comments.list()


if __name__ == "__main__":
    try:
        # Example usage
        bot = RedditBot()

        # Get hot posts from a subreddit
        subreddit_name = "Python"  # Example subreddit
        posts = bot.get_subreddit_hot_posts(subreddit_name, limit=5)

        print(f"\nHot posts from r/{subreddit_name}:")
        for post in posts:
            print(f"\nTitle: {post.title}")
            print(f"Score: {post.score}")
            print(f"URL: {post.url}")
    except Exception as e:
        print(f"An error occurred: {e}")
