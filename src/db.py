"""
Database module for MongoDB connection and operations.
Handles activities collection management.
"""

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import os
from typing import Optional, Dict, List
from bson import ObjectId


class ActivityDatabase:
    """Manages MongoDB connection and activities collection."""

    def __init__(self, mongo_url: Optional[str] = None, db_name: str = "mergington_school"):
        """
        Initialize database connection.
        
        Args:
            mongo_url: MongoDB connection string. Defaults to MONGO_URL env var or local instance.
            db_name: Database name. Defaults to "mergington_school".
        """
        self.mongo_url = mongo_url or os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self.db_name = db_name
        self.client: Optional[MongoClient] = None
        self.db = None
        self.activities_collection = None

    def connect(self):
        """Connect to MongoDB and initialize collections."""
        try:
            self.client = MongoClient(self.mongo_url, serverSelectionTimeoutMS=5000)
            # Verify connection
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.activities_collection = self.db['activities']
            
            # Create index on activity name for uniqueness and performance
            self.activities_collection.create_index("name", unique=True)
            print(f"✓ Connected to MongoDB at {self.mongo_url}")
            return True
        except ServerSelectionTimeoutError:
            print(f"✗ Failed to connect to MongoDB at {self.mongo_url}")
            return False
        except Exception as e:
            print(f"✗ Database connection error: {e}")
            return False

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()

    def get_all_activities(self) -> Dict[str, Dict]:
        """
        Retrieve all activities from database.
        
        Returns:
            Dictionary with activity names as keys and activity data as values.
        """
        if not self.activities_collection:
            return {}
        
        activities = {}
        for doc in self.activities_collection.find():
            activity_name = doc.pop("name")
            doc.pop("_id", None)  # Remove MongoDB ObjectId
            activities[activity_name] = doc
        
        return activities

    def get_activity(self, activity_name: str) -> Optional[Dict]:
        """
        Retrieve a single activity by name.
        
        Args:
            activity_name: Name of the activity.
            
        Returns:
            Activity data or None if not found.
        """
        if not self.activities_collection:
            return None
        
        doc = self.activities_collection.find_one({"name": activity_name})
        if doc:
            doc.pop("_id", None)
        return doc

    def create_activity(self, name: str, activity_data: Dict) -> bool:
        """
        Create a new activity.
        
        Args:
            name: Activity name.
            activity_data: Activity details (description, schedule, max_participants, participants).
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.activities_collection:
            return False
        
        try:
            self.activities_collection.insert_one({
                "name": name,
                **activity_data
            })
            return True
        except Exception as e:
            print(f"Error creating activity: {e}")
            return False

    def add_participant(self, activity_name: str, email: str) -> bool:
        """
        Add a participant to an activity.
        
        Args:
            activity_name: Name of the activity.
            email: Student email.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.activities_collection:
            return False
        
        try:
            result = self.activities_collection.update_one(
                {"name": activity_name},
                {"$addToSet": {"participants": email}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error adding participant: {e}")
            return False

    def remove_participant(self, activity_name: str, email: str) -> bool:
        """
        Remove a participant from an activity.
        
        Args:
            activity_name: Name of the activity.
            email: Student email.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.activities_collection:
            return False
        
        try:
            result = self.activities_collection.update_one(
                {"name": activity_name},
                {"$pull": {"participants": email}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error removing participant: {e}")
            return False

    def delete_activity(self, activity_name: str) -> bool:
        """
        Delete an activity.
        
        Args:
            activity_name: Name of the activity.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.activities_collection:
            return False
        
        try:
            result = self.activities_collection.delete_one({"name": activity_name})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting activity: {e}")
            return False

    def update_activity(self, activity_name: str, updates: Dict) -> bool:
        """
        Update activity details.
        
        Args:
            activity_name: Name of the activity.
            updates: Fields to update (e.g., description, schedule, max_participants).
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.activities_collection:
            return False
        
        try:
            result = self.activities_collection.update_one(
                {"name": activity_name},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating activity: {e}")
            return False


# Global database instance
db = ActivityDatabase()
