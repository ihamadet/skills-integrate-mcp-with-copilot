#!/usr/bin/env python3
"""
Migration script to load initial activities data into MongoDB.
Run this once to populate the database with sample activities.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from db import db

# Sample activities data (from original in-memory store)
INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


def migrate():
    """Load initial activities into MongoDB."""
    print("🚀 Starting migration to MongoDB...")
    
    # Connect to database
    if not db.connect():
        print("❌ Failed to connect to MongoDB. Please ensure MongoDB is running.")
        print("   Set MONGO_URL environment variable if using a remote instance.")
        return False
    
    # Clear existing activities (optional - comment out to preserve)
    db.activities_collection.delete_many({})
    print("  Cleared existing activities")
    
    # Insert activities
    success_count = 0
    for activity_name, activity_data in INITIAL_ACTIVITIES.items():
        if db.create_activity(activity_name, activity_data):
            success_count += 1
            print(f"  ✓ Created: {activity_name}")
        else:
            print(f"  ✗ Failed: {activity_name}")
    
    db.close()
    
    print(f"\n✅ Migration complete! {success_count}/{len(INITIAL_ACTIVITIES)} activities loaded.")
    return success_count == len(INITIAL_ACTIVITIES)


if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
