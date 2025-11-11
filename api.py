import uvicorn
from fastapi import FastAPI
import db_utils # We still use our database logic!

# Create the FastAPI app
app = FastAPI()

# --- API Endpoints ---

@app.get("/")
def read_root():
    """Root endpoint, just to check if the API is running."""
    return {"message": "Welcome to the Trip Wala API!"}

@app.get("/destinations")
def get_all_destinations():
    """
    Fetches all destinations from the database.
    This replaces the load_data() call.
    """
    destinations = db_utils.get_all_destinations()
    return destinations

@app.get("/bookings/{username}")
def get_user_bookings(username: str):
    """
    Fetches all bookings for a specific user.
    'username' is passed from the URL.
    """
    bookings = db_utils.get_user_bookings(username)
    return bookings

# This line allows you to run the API directly with `python api.py`
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)