import json
import sys
from pathlib import Path

import yaml

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from storage.supabase_storage import SupabaseStorage


def load_config(config_path: str = "../../config/config.yaml") -> dict:
    """Load configuration from YAML file."""
    config_path = Path(config_path).resolve()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")

    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def migrate_data():
    """Migrate data from JSON to Supabase."""
    # Load config
    config = load_config()

    # Initialize Supabase storage
    storage = SupabaseStorage(
        url=config["supabase"]["url"], key=config["supabase"]["key"]
    )

    # Load JSON data
    json_path = Path("../data/posts.json").resolve()
    if not json_path.exists():
        print("No JSON data found to migrate")
        return

    with open(json_path, "r") as f:
        data = json.load(f)

    # Convert dict to list of posts
    posts = list(data.values())

    # Save to Supabase
    print(f"Migrating {len(posts)} posts to Supabase...")
    storage.save_posts(posts)
    print("Migration complete!")


if __name__ == "__main__":
    migrate_data()
