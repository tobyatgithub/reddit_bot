import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .base import BaseStorage


class JsonStorage(BaseStorage):
    def __init__(self, data_dir: str = "../data"):
        self.data_dir = Path(data_dir)
        self.posts_file = self.data_dir / "posts.json"
        self._ensure_data_dir()
        self._initialize_storage()

    def _ensure_data_dir(self) -> None:
        """Ensure the data directory exists."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_storage(self) -> None:
        """Initialize the storage files if they don't exist."""
        if not self.posts_file.exists():
            self._save_data({})

    def _load_data(self) -> Dict:
        """Load data from JSON file."""
        try:
            with open(self.posts_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def _save_data(self, data: Dict) -> None:
        """Save data to JSON file."""
        with open(self.posts_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save_posts(self, posts: List[Dict]) -> None:
        """Save multiple posts, avoiding duplicates."""
        current_data = self._load_data()

        for post in posts:
            post_id = post["id"]
            if post_id not in current_data:
                post["collected_at"] = datetime.utcnow().isoformat()
                current_data[post_id] = post
            else:
                # Update existing post if score or comments changed
                if (
                    current_data[post_id]["score"] != post["score"]
                    or current_data[post_id]["num_comments"] != post["num_comments"]
                ):
                    post["last_updated"] = datetime.utcnow().isoformat()
                    current_data[post_id].update(post)

        self._save_data(current_data)

    def get_post(self, post_id: str) -> Optional[Dict]:
        """Retrieve a specific post by ID."""
        data = self._load_data()
        return data.get(post_id)

    def post_exists(self, post_id: str) -> bool:
        """Check if a post already exists."""
        return post_id in self._load_data()

    def get_posts_by_subreddit(self, subreddit: str) -> List[Dict]:
        """Retrieve all posts from a specific subreddit."""
        data = self._load_data()
        return [
            post
            for post in data.values()
            if post["subreddit"].lower() == subreddit.lower()
        ]
