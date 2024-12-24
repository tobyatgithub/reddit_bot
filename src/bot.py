from pathlib import Path

import praw
import prawcore
import yaml

from storage.json_storage import JsonStorage
from storage.supabase_storage import SupabaseStorage


class RedditBot:
    def __init__(self, config_path: str = "../config/config.yaml"):
        self.config = self._load_config(config_path)
        self.reddit = self._initialize_reddit()
        self.storage = self._initialize_storage()
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

    def get_detailed_posts(
        self, subreddit_name: str, limit: int = 10, post_type: str = "hot"
    ):
        """
        Fetch detailed information about posts from a subreddit.

        Args:
            subreddit_name (str): Name of the subreddit
            limit (int): Number of posts to fetch
            post_type (str): Type of posts to fetch ('hot', 'new', 'top', 'rising')

        Returns:
            list: List of dictionaries containing post details
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)

            # Get the posts based on type
            if post_type == "hot":
                posts = subreddit.hot(limit=limit)
            elif post_type == "new":
                posts = subreddit.new(limit=limit)
            elif post_type == "top":
                posts = subreddit.top(limit=limit)
            elif post_type == "rising":
                posts = subreddit.rising(limit=limit)
            else:
                raise ValueError(f"Invalid post type: {post_type}")

            detailed_posts = []
            for post in posts:
                post_details = {
                    "id": post.id,
                    "title": post.title,
                    "author": str(post.author),
                    "created_utc": post.created_utc,
                    "score": post.score,
                    "upvote_ratio": post.upvote_ratio,
                    "num_comments": post.num_comments,
                    "permalink": post.permalink,
                    "url": post.url,
                    "is_self": post.is_self,  # True if it's a text post
                    "selftext": post.selftext if post.is_self else None,
                    "link_flair_text": post.link_flair_text,
                    "subreddit": subreddit_name,
                    "top_comments": self._get_top_comments(post, limit=5),
                }
                detailed_posts.append(post_details)

            return detailed_posts

        except Exception as e:
            print(f"Error fetching posts from r/{subreddit_name}: {e}")
            raise

    def _get_top_comments(self, post, limit: int = 5):
        """Get top comments from a post."""
        post.comments.replace_more(limit=0)  # Remove "More Comments" objects
        return [
            {
                "author": str(comment.author),
                "body": comment.body,
                "score": comment.score,
                "created_utc": comment.created_utc,
            }
            for comment in sorted(post.comments, key=lambda x: x.score, reverse=True)[
                :limit
            ]
        ]

    def get_posts_by_flair(self, subreddit_name: str, flair: str, limit: int = 10):
        """
        Fetch posts with a specific flair from a subreddit.

        Args:
            subreddit_name (str): Name of the subreddit
            flair (str): The flair to filter by
            limit (int): Maximum number of posts to return
        """
        try:
            # Using Reddit's search syntax to filter by flair
            query = f"flair:{flair}"
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = subreddit.search(query, limit=limit)
            return self._process_posts(posts)
        except Exception as e:
            print(
                f"Error fetching posts with flair '{flair}' from r/{subreddit_name}: {e}"
            )
            raise

    def get_positive_content(
        self, subreddits: list = None, post_type: str = "hot", limit: int = 5
    ):
        """
        Fetch positive content from multiple self-improvement subreddits.

        Args:
            subreddits (list): List of subreddit names. If None, uses default list.
            post_type (str): Type of posts to fetch ('hot', 'new', 'top', 'rising')
            limit (int): Number of posts per subreddit
        """
        if subreddits is None:
            subreddits = [
                "selfimprovement",
                "GetMotivated",
                "DecidingToBeBetter",
                "productivity",
                "MadeMeSmile",
                "LifeProTips",
            ]

        all_posts = {}
        for subreddit in subreddits:
            try:
                posts = self.get_detailed_posts(
                    subreddit, limit=limit, post_type=post_type
                )
                all_posts[subreddit] = posts
            except Exception as e:
                print(f"Error fetching from r/{subreddit}: {e}")
                continue

        return all_posts

    def _process_posts(self, posts):
        """Helper method to process posts into detailed format."""
        return [
            {
                "id": post.id,
                "title": post.title,
                "author": str(post.author),
                "created_utc": post.created_utc,
                "score": post.score,
                "upvote_ratio": post.upvote_ratio,
                "num_comments": post.num_comments,
                "permalink": post.permalink,
                "url": post.url,
                "is_self": post.is_self,
                "selftext": post.selftext if post.is_self else None,
                "link_flair_text": post.link_flair_text,
                "subreddit": post.subreddit.display_name,
                "top_comments": self._get_top_comments(post, limit=5),
            }
            for post in posts
        ]

    def save_subreddit_posts(
        self, subreddit_name: str, limit: int = 10, post_type: str = "hot"
    ):
        """Fetch and save posts from a subreddit."""
        posts = self.get_detailed_posts(
            subreddit_name, limit=limit, post_type=post_type
        )
        self.storage.save_posts(posts)
        return posts

    def _initialize_storage(self):
        """Initialize storage based on configuration."""
        if "supabase" in self.config:
            return SupabaseStorage(
                url=self.config["supabase"]["url"], key=self.config["supabase"]["key"]
            )
        return JsonStorage()


if __name__ == "__main__":
    try:
        bot = RedditBot()

        # Example: Save posts from multiple subreddits
        subreddits = ["selfimprovement", "GetMotivated"]
        for subreddit in subreddits:
            print(f"\nFetching and saving posts from r/{subreddit}")
            posts = bot.save_subreddit_posts(subreddit, limit=5)
            print(f"Saved {len(posts)} posts")

        # Example: Retrieve saved posts
        for subreddit in subreddits:
            saved_posts = bot.storage.get_posts_by_subreddit(subreddit)
            print(f"\nRetrieved {len(saved_posts)} posts from r/{subreddit}")
            for post in saved_posts[:2]:  # Show first 2 posts
                print(f"\nTitle: {post['title']}")
                print(f"Score: {post['score']} | Comments: {post['num_comments']}")
                print(f"Collected at: {post['collected_at']}")

    except Exception as e:
        print(f"An error occurred: {e}")
