from datetime import datetime
from typing import Dict, List, Optional

from supabase import create_client
from supabase.client import Client

from .base import BaseStorage


class SupabaseStorage(BaseStorage):
    def __init__(self, url: str, key: str):
        """Initialize Supabase client."""
        self.supabase: Client = create_client(url, key)

    def save_posts(self, posts: List[Dict]) -> None:
        """Save multiple posts to Supabase."""
        for post in posts:
            # Create a copy of the post to avoid modifying the original
            post_data = post.copy()

            # Convert created_utc from timestamp to datetime
            created_dt = datetime.fromtimestamp(post_data["created_utc"])
            post_data["created_utc"] = created_dt.isoformat()

            # Extract comments before inserting post
            comments = post_data.pop("top_comments", [])

            # Check if post exists
            if not self.post_exists(post_data["id"]):
                # Add collected_at timestamp
                post_data["collected_at"] = datetime.utcnow().isoformat()
                # Insert new post
                self.supabase.table("posts").insert(post_data).execute()
            else:
                # Update existing post
                post_data["last_updated"] = datetime.utcnow().isoformat()
                self.supabase.table("posts").update(post_data).eq(
                    "id", post_data["id"]
                ).execute()

            # Save comments if they exist
            for comment in comments:
                comment_data = comment.copy()
                # Generate a unique ID for the comment using post_id and author
                comment_data[
                    "id"
                ] = f"{post_data['id']}_{comment['author']}_{comment['created_utc']}"
                comment_data["post_id"] = post_data["id"]
                comment_data["created_utc"] = datetime.fromtimestamp(
                    comment["created_utc"]
                ).isoformat()
                comment_data["collected_at"] = datetime.utcnow().isoformat()
                self.supabase.table("comments").upsert(
                    comment_data, on_conflict="id"
                ).execute()

    def get_post(self, post_id: str) -> Optional[Dict]:
        """Retrieve a specific post by ID."""
        response = self.supabase.table("posts").select("*").eq("id", post_id).execute()
        return response.data[0] if response.data else None

    def post_exists(self, post_id: str) -> bool:
        """Check if a post already exists."""
        response = self.supabase.table("posts").select("id").eq("id", post_id).execute()
        return bool(response.data)

    def get_posts_by_subreddit(self, subreddit: str) -> List[Dict]:
        """Retrieve all posts from a specific subreddit."""
        response = (
            self.supabase.table("posts")
            .select("*")
            .eq("subreddit", subreddit)
            .order("created_utc", desc=True)
            .execute()
        )
        return response.data
