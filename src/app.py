"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.

Now uses MongoDB for persistent storage instead of in-memory data.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from db import db

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on app startup."""
    if not db.connect():
        print("⚠️  Warning: MongoDB connection failed. Using fallback in-memory storage.")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on app shutdown."""
    db.close()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    """Get all activities from MongoDB."""
    activities = db.get_all_activities()
    return activities if activities else {}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    activity = db.get_activity(activity_name)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate student is not already signed up
    if email in activity.get("participants", []):
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    if db.add_participant(activity_name, email):
        return {"message": f"Signed up {email} for {activity_name}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to sign up student")


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    activity = db.get_activity(activity_name)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate student is signed up
    if email not in activity.get("participants", []):
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    if db.remove_participant(activity_name, email):
        return {"message": f"Unregistered {email} from {activity_name}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to unregister student")
