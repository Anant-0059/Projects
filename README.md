# 🗺️ Trip Wala - A Tourist Planner & Booking App

[](https://www.python.org/)
[](https://streamlit.io)
[](https://www.sqlite.org/index.html)

A fully-functional, interactive tourist planner for destinations across Maharashtra, built from scratch with Python and Streamlit. This app provides a complete user workflow, from secure login and trip planning to a simulated UPI booking and booking history.

-----
## 📸 Key Features in Action

## ✨ Features

  * **🛡️ Secure Authentication:** A complete login system (`streamlit-authenticator`) with hashed passwords and role-based access.
  * **👨‍💼 Admin Panel:** A separate admin-only view to perform **CRUD** (Create, Read, Update, Delete) operations on all destinations.
  * **📅 Dynamic Trip Planner:** Calculates a detailed estimated budget based on:
      * Starting City (Sangli, Ashta, Islampur)
      * Destination
      * Number of Persons
      * Number of Stay Days
      * Mode of Transport (Car or Bus)
  * **💳 Simulated UPI Payment:** A complete booking flow that generates a dynamic **QR Code** for the total amount and displays GPay/PhonePe logos.
  * **🧾 My Bookings:** A dedicated page for users to view their entire history of (simulated) booked trips, read from the database.
  * **🖼️ Dynamic Destination Cards:** Fetches and displays all available destinations from the database, complete with images, highlights, and base costs.
  * **🎉 Animations:** Includes loading spinners and a `st.balloons()` celebration after a successful booking.

-----

## 💻 Tech Stack & Architecture

This project is built on a clean, decoupled 3-tier architecture, all within Python.

  * **Frontend (`newMain.py`):**
      * **Streamlit** for the interactive web UI.
  * **Backend Logic (`db_utils.py`):**
      * A dedicated Python module that handles all database operations (CRUD).
      * Contains all SQL queries, keeping the frontend clean.
  * **Database (`tripwala.db`):**
      * **SQLite** for a persistent, file-based database.
      * Features two tables: `destinations` (for places) and `bookings` (for user history).
  * **Authentication (`config.yaml`):**
      * YAML file storing hashed user credentials for `streamlit-authenticator`.

-----

## ⚙️ How to Run Locally

Follow these steps to set up and run the project on your local machine.

**1. Clone the Repository:**

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

**2. Create and Activate Virtual Environment:**

```bash
# Create the environment
python -m venv .venv

# Activate on Windows
.\.venv\Scripts\activate

# Activate on macOS/Linux
source .venv/bin/activate
```

**3. Install Dependencies:**
(This uses the `requirements.txt` file you created)

```bash
pip install -r requirements.txt
```

**4. Run the App:**

```bash
streamlit run newMain.py
```

The app will open in your browser at `http://localhost:8501`.

-----

### Default Logins

You can find all users in `config.yaml`. The default logins are:

  * **Admin:**
      * **Username:** `admin`
      * **Password:** (your admin password)
  * **Guest:**
      * **Username:** `guest`
      * **Password:** (your guest password)