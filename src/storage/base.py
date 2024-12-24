from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseStorage(ABC):
    """Abstract base class for data storage implementations."""

    @abstractmethod
    def save_posts(self, posts: List[Dict]) -> None:
        """Save multiple posts."""
        pass

    @abstractmethod
    def get_post(self, post_id: str) -> Optional[Dict]:
        """Retrieve a specific post by ID."""
        pass

    @abstractmethod
    def post_exists(self, post_id: str) -> bool:
        """Check if a post already exists."""
        pass

    @abstractmethod
    def get_posts_by_subreddit(self, subreddit: str) -> List[Dict]:
        """Retrieve all posts from a specific subreddit."""
        pass
