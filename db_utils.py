import sqlite3
import datetime # Needed for timestamp

# Define the database file
DB_FILE = "tripwala.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Creates the destinations table with the new image_url column."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Destinations table (ADDED image_url TEXT)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS destinations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        region TEXT NOT NULL,
        highlights TEXT,
        cost INTEGER,
        image_url TEXT  -- New column for the image link
    )
    """)
    conn.commit()
    conn.close()

# --- Bookings Table (No changes) ---
def create_bookings_table():
    """Creates the bookings table if it doesn't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        start_city TEXT,
        destination_name TEXT,
        num_people INTEGER,
        stay_days INTEGER,
        transport_mode TEXT,
        total_budget REAL,
        booking_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

# --- CRUD Functions for Destinations ---

# --- CREATE ---
# Added image_url parameter (now 5 arguments)
def add_destination(name, region, highlights, cost, image_url):
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        # Added image_url column
        cursor.execute("INSERT INTO destinations (name, region, highlights, cost, image_url) VALUES (?, ?, ?, ?, ?)", (name, region, highlights, cost, image_url))
        conn.commit(); return True
    except sqlite3.Error as e: print(f"DB err: {e}"); return False
    finally: conn.close()

# --- READ ---
def get_all_destinations():
    conn = get_db_connection(); cursor = conn.cursor()
    # Added image_url column to SELECT
    cursor.execute("SELECT id, name, region, highlights, cost, image_url FROM destinations ORDER BY name")
    destinations = cursor.fetchall(); conn.close()
    return [dict(row) for row in destinations]

# --- UPDATE ---
# Added image_url parameter (now 6 arguments)
def update_destination(id, name, region, highlights, cost, image_url):
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        # Added image_url column
        cursor.execute("UPDATE destinations SET name = ?, region = ?, highlights = ?, cost = ?, image_url = ? WHERE id = ?", (name, region, highlights, cost, image_url, id))
        conn.commit(); return True
    except sqlite3.Error as e: print(f"DB err: {e}"); return False
    finally: conn.close()

# --- DELETE ---
# (No changes needed)
def delete_destination(id):
    conn = get_db_connection(); cursor = conn.cursor()
    try: cursor.execute("DELETE FROM destinations WHERE id = ?", (id,)); conn.commit(); return True
    except sqlite3.Error as e: print(f"DB err: {e}"); return False
    finally: conn.close()

# --- Functions for Bookings ---
# (save_booking and get_user_bookings remain the same)
def save_booking(username, trip_details):
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO bookings (username, start_city, destination_name, num_people, stay_days, transport_mode, total_budget) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                       (username, trip_details.get('start_city'), trip_details.get('destination_name'), trip_details.get('num_people'), trip_details.get('stay_days'), trip_details.get('transport_mode'), trip_details.get('total_budget')))
        conn.commit(); return True
    except sqlite3.Error as e: print(f"Error saving booking: {e}"); return False
    finally: conn.close()

def get_user_bookings(username):
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("SELECT id, start_city, destination_name, num_people, stay_days, transport_mode, total_budget, booking_timestamp FROM bookings WHERE username = ? ORDER BY booking_timestamp DESC", (username,))
    bookings = cursor.fetchall(); conn.close()
    return [dict(row) for row in bookings]

# --- Utility Function ---
def populate_database_if_empty():
    """Populates the destinations DB if empty."""
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM destinations")
    count = cursor.fetchone()[0]; conn.close()

    if count == 0:
        print("Destinations DB empty. Populating with sample data...")
        # ADDED sample image URLs
        sample_data = [
            ("Matheran", "Maharashtra", "Hill Station, Viewpoints, Toy Train", 800, "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Matheran_Hills.jpg/1024px-Matheran_Hills.jpg"),
            ("Konkan", "Maharashtra", "Beaches, Forts, Seafood (Ratnagiri)", 400, "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Ratnagiri_fort.jpg/1024px-Ratnagiri_fort.jpg"),
            ("Malshej Ghat", "Maharashtra", "Waterfalls, Monsoon destination, Hiking", 580, "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Malshej_Ghat_3.jpg/1024px-Malshej_Ghat_3.jpg"),
            ("Mumbai", "Maharashtra", "Gateway of India, Marine Drive, Bollywood", 700, "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Mumbai_Skyline_at_Night.jpg/1024px-Mumbai_Skyline_at_Night.jpg"),
            ("Pune", "Maharashtra", "Shaniwar Wada, Aga Khan Palace, Osho Ashram", 450, "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Shaniwar_wada_main_gate.jpg/1024px-Shaniwar_wada_main_gate.jpg"),
            ("Lonavala & Khandala", "Maharashtra", "Hill stations, Caves, Chikki", 550, "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Bhaja_Caves_near_Lonavla_India.jpg/1024px-Bhaja_Caves_near_Lonavla_India.jpg"),
            ("Mahabaleshwar", "Maharashtra", "Strawberry farms, Venna Lake, Viewpoints", 500, "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Connaught_Peak_in_Mahabaleshwar.jpg/1024px-Connaught_Peak_in_Mahabaleshwar.jpg"),
            ("Chhatrapati Sambhaji Nagar", "Maharashtra", "Ajanta & Ellora Caves, Bibi Ka Maqbara", 550, "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Bibi_Ka_Maqbara_Aurangabad.jpg/1024px-Bibi_Ka_Maqbara_Aurangabad.jpg"),
            ("Nashik", "Maharashtra", "Vineyards, Sula Fest, Trimbakeshwar Temple", 480, "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Sula_Vineyards_Nashik_India.jpg/1024px-Sula_Vineyards_Nashik_India.jpg"),
            ("Alibaug", "Maharashtra", "Beaches, Forts, Water sports", 420, "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Kolaba_Fort_at_Alibaug_20170313_150824.jpg/1024px-Kolaba_Fort_at_Alibaug_20170313_150824.jpg"),
            ("Shirdi", "Maharashtra", "Sai Baba Temple, Pilgrimage site", 550, "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Shirdi_Sai_Temple.jpg/1024px-Shirdi_Sai_Temple.jpg"),
            ("Tadoba National Park", "Maharashtra", "Tiger Safari, Wildlife, Jungle", 800, "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Tadoba_Tiger.jpg/1024px-Tadoba_Tiger.jpg"),
            ("Ganpatipule", "Maharashtra", "Swayambhu Ganesh Temple, Pristine Beach", 480, "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Ganpatipule_temple_and_sea_shore.jpg/1024px-Ganpatipule_temple_and_sea_shore.jpg"),
            ("Kolhapur", "Maharashtra", "Mahalakshmi Temple, Panhala Fort, Cuisine", 300, "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Mahalaxmi_temple_Kolhapur.jpg/1024px-Mahalaxmi_temple_Kolhapur.jpg"),
            ("Tarkarli", "Maharashtra", "Scuba Diving, Snorkeling, Malvan coast", 650, "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Tarkarli_Beach_2.jpg/1024px-Tarkarli_Beach_2.jpg"),
            ("Panchgani", "Maharashtra", "Table Land, Paragliding, Mapro Garden", 490, "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Table_Land_Panchgani_2.jpg/1024px-Table_Land_Panchgani_2.jpg"),
            ("Raigad Fort", "Maharashtra", "Maratha History, Trekking, Ropeway", 500, "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Raigad_Fort_Maharashtra.jpg/1024px-Raigad_Fort_Maharashtra.jpg"),
        ]
        for item in sample_data:
            add_destination(*item) # Call with 5 arguments
        print("Sample destinations populated.")
    else:
         print("Destinations DB not empty.")