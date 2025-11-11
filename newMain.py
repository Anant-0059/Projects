import streamlit as st
import pandas as pd
import db_utils
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import datetime
import qrcode
from io import BytesIO
import time

# --- Page Configuration ---
st.set_page_config(page_title="Trip Wala", page_icon="🗺️", layout="wide")

# --- Constants ---
TRANSPORT_RATES_PER_KM = { "Bus": 2.5, "Car": 14.0 }
DISTANCES_FROM_HUBS = {
    "Sangli": {"Matheran": 345, "Konkan": 185, "Malshej Ghat": 390, "Mumbai": 375, "Pune": 235, "Lonavala & Khandala": 295, "Mahabaleshwar": 185, "Chhatrapati Sambhaji Nagar": 470, "Nashik": 450, "Alibaug": 375, "Shirdi": 420, "Tadoba National Park": 890, "Ganpatipule": 215, "Kolhapur": 50, "Tarkarli": 215, "Panchgani": 175, "Raigad Fort": 305},
    "Ashta": {"Matheran": 315, "Konkan": 155, "Malshej Ghat": 360, "Mumbai": 345, "Pune": 210, "Lonavala & Khandala": 270, "Mahabaleshwar": 155, "Chhatrapati Sambhaji Nagar": 445, "Nashik": 425, "Alibaug": 345, "Shirdi": 395, "Tadoba National Park": 860, "Ganpatipule": 165, "Kolhapur": 70, "Tarkarli": 185, "Panchgani": 145, "Raigad Fort": 275},
    "Islampur": {"Matheran": 320, "Konkan": 150, "Malshej Ghat": 355, "Mumbai": 340, "Pune": 200, "Lonavala & Khandala": 265, "Mahabaleshwar": 145, "Chhatrapati Sambhaji Nagar": 435, "Nashik": 415, "Alibaug": 340, "Shirdi": 385, "Tadoba National Park": 850, "Ganpatipule": 155, "Kolhapur": 60, "Tarkarli": 180, "Panchgani": 135, "Raigad Fort": 270}
}
GPAY_LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Google_Pay_Logo.svg/1200px-Google_Pay_Logo.svg.png"
PHONEPE_LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/PhonePe_Logo.svg/1200px-PhonePe_Logo.svg.png"
PLACEHOLDER_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Placeholder_view_vector.svg/681px-Placeholder_view_vector.svg.png"

# --- Database Initialization ---
# !! Delete old tripwala.db file before running !!
db_utils.create_tables()
db_utils.create_bookings_table()
db_utils.populate_database_if_empty()

# --- Functions ---
@st.cache_data
def load_data():
    """Loads destination data including image_url."""
    all_data = db_utils.get_all_destinations()
    if all_data:
        # ADDED 'image_url' to columns list
        columns = ["id", "name", "region", "highlights", "cost", "image_url"]
        df = pd.DataFrame(all_data, columns=columns)
        df = df.rename(columns={
            "id": "ID", "name": "Destination Name", "region": "Location/Region",
            "highlights": "Highlights", "cost": "Average Cost",
            "image_url": "Image URL" # Added image URL
        })
        df['DistanceLookupName'] = df['Destination Name'].apply(lambda x: 'Konkan' if x == 'Konkan' else ('Chhatrapati Sambhaji Nagar' if x == 'Chhatrapati Sambhaji Nagar' else x))
        return df
    return pd.DataFrame()

def generate_qr_code(data):
    """Generates a QR code image."""
    qr = qrcode.QRCode( version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=4, border=3)
    qr.add_data(data); qr.make(fit=True); img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
    return buf

# --- Initialize Session State ---
if 'trip_details' not in st.session_state: st.session_state.trip_details = None
if 'show_confirmation' not in st.session_state: st.session_state.show_confirmation = False
if 'show_payment_simulation' not in st.session_state: st.session_state.show_payment_simulation = False
if 'viewing_bookings' not in st.session_state: st.session_state.viewing_bookings = False

# --- USER AUTHENTICATION ---
with open('config.yaml') as file: config = yaml.load(file, Loader=SafeLoader)
authenticator = stauth.Authenticate(config['credentials'], config['cookie']['name'], config['cookie']['key'], config['cookie']['expiry_days'])
authenticator.login(location='main')
name = st.session_state.get("name"); authentication_status = st.session_state.get("authentication_status"); username = st.session_state.get("username")

# --- MAIN APP LOGIC (IF LOGGED IN) ---
if authentication_status:

    # --- Sidebar ---
    with st.sidebar:
        st.write(f'👋 Welcome *{name}*')
        authenticator.logout('Logout', 'main')
        st.divider()
        if st.button("📅 Plan New Trip"):
            st.session_state.viewing_bookings = False; st.session_state.trip_details = None
            st.session_state.show_confirmation = False; st.session_state.show_payment_simulation = False
            st.rerun()
        if st.button("🧾 My Bookings"): st.session_state.viewing_bookings = True; st.rerun()
        st.divider()

    # --- Header ---
    st.markdown("# 🗺️ Trip Wala 🏖️"); st.markdown("##### *Explore, plan, manage trips.*"); st.divider()

    # --- Load Data ---
    with st.spinner("Loading data... ⏳"): df = load_data()

    # --- VIEW MY BOOKINGS ---
    if st.session_state.viewing_bookings:
        # (This section is unchanged)
        st.markdown("## 🧾 My Bookings")
        with st.spinner("Loading your bookings..."): user_bookings = db_utils.get_user_bookings(username)
        if not user_bookings: st.info("ℹ️ You haven't booked any trips yet.")
        else:
            st.write(f"Found {len(user_bookings)} booking(s):")
            for booking in user_bookings:
                try: dt_obj = datetime.datetime.fromisoformat(booking['booking_timestamp']); formatted_date = dt_obj.strftime("%d %b %Y, %I:%M %p")
                except: formatted_date = str(booking.get('booking_timestamp', 'N/A'))
                with st.expander(f"**{booking.get('destination_name','N/A')}** (Booked: {formatted_date})"):
                    col_b1, col_b2 = st.columns(2)
                    with col_b1: st.write(f"**From:** {booking.get('start_city','N/A')}"); st.write(f"**Persons:** {booking.get('num_people','N/A')}"); st.write(f"**Duration:** {booking.get('stay_days','N/A')}d")
                    with col_b2: st.write(f"**Transport:** {booking.get('transport_mode','N/A')}"); st.write(f"**Cost:** ₹{booking.get('total_budget', 0):,.2f}")

    # --- PLAN NEW TRIP (DEFAULT VIEW) ---
    else:
        # --- TRIP PLANNER SECTION ---
        st.markdown("## 📅 Plan Your Trip")
        if not df.empty:
            # (Planner Inputs remain the same)
            col1, col2, col3 = st.columns(3)
            with col1: start_city = st.selectbox("📍 Start City", options=sorted(DISTANCES_FROM_HUBS.keys()), key="start_city"); num_people = st.number_input("👥 Persons", min_value=1, value=1, step=1, key="num_people")
            with col2: destination_list = sorted(df["Destination Name"].unique().tolist()); destination_name = st.selectbox("🎯 Destination", options=destination_list, key="destination_name"); stay_days = st.number_input("⏳ Stay Days", min_value=1, value=2, step=1, key="stay_days")
            with col3: transport_mode = st.selectbox("🚌/🚗 Transport", options=sorted(TRANSPORT_RATES_PER_KM.keys()), key="transport_mode")

            # --- Budget Calculation Button ---
            # (Logic is unchanged)
            if st.button("💰 Calculate Estimated Budget"):
                st.session_state.show_confirmation = False; st.session_state.show_payment_simulation = False; st.session_state.trip_details = None
                try:
                    dest_row = df.loc[df["Destination Name"] == destination_name].iloc[0]; base_per_person_per_day_cost = dest_row["Average Cost"]; distance_lookup_key = dest_row['DistanceLookupName']
                    distance_km = DISTANCES_FROM_HUBS[start_city].get(distance_lookup_key)
                    if distance_km is None: st.error(f"❌ Distance data unavailable."); st.session_state.trip_details = None
                    else:
                        total_base_cost = base_per_person_per_day_cost * num_people * stay_days; rate = TRANSPORT_RATES_PER_KM[transport_mode]; round_trip_distance = distance_km * 2
                        total_transport_cost = (round_trip_distance * rate) if transport_mode == "Car" else (round_trip_distance * rate * num_people); total_budget = total_base_cost + total_transport_cost
                        st.session_state.trip_details = { "start_city": start_city, "destination_name": destination_name, "num_people": num_people, "stay_days": stay_days, "transport_mode": transport_mode, "distance_km": distance_km, "round_trip_distance": round_trip_distance, "base_per_person_per_day_cost": base_per_person_per_day_cost, "total_base_cost": total_base_cost, "transport_rate": rate, "total_transport_cost": total_transport_cost, "total_budget": total_budget }
                except Exception as e: st.error(f"❌ Calc error."); st.session_state.trip_details = None; print(f"Calc Error: {e}")

            # --- Display Budget, Confirm Button ---
            if st.session_state.trip_details and not st.session_state.show_confirmation and not st.session_state.show_payment_simulation:
                # (Logic is unchanged)
                trip = st.session_state.trip_details
                st.subheader(f"📊 Budget Estimate: {trip['num_people']}p, {trip['stay_days']}d"); st.info(f"From **{trip['start_city']}** to **{trip['destination_name']}**"); st.metric("💸 Total Estimated Budget", f"₹{trip['total_budget']:,.2f}")
                st.divider()
                st.markdown("#### Cost Breakdown")
                st.markdown(f"**🏨 Base Cost:** ₹{trip['base_per_person_per_day_cost']:,.2f} x {trip['num_people']}p x {trip['stay_days']}d = **₹{trip['total_base_cost']:,.2f}**")
                st.markdown(f"**{'🚗' if trip['transport_mode'] == 'Car' else '🚌'} Transport ({trip['transport_mode']}):**"); st.markdown(f"&nbsp;&nbsp;- One-Way: **{trip['distance_km']} km**")
                if trip['distance_km'] >= 0:
                    if trip['transport_mode'] == "Car": st.markdown(f"&nbsp;&nbsp;- Round Trip ({trip['round_trip_distance']} km) @ ₹{trip['transport_rate']:.2f}/km = **₹{trip['total_transport_cost']:,.2f}**")
                    else: st.markdown(f"&nbsp;&nbsp;- Round Trip ({trip['round_trip_distance']} km) @ ₹{trip['transport_rate']:.2f}/km x {trip['num_people']}p = **₹{trip['total_transport_cost']:,.2f}**")
                st.divider()
                if st.button("✅ Confirm Trip Details"): st.session_state.show_confirmation = True; st.rerun()

            # --- CONFIRMATION SECTION ---
            if st.session_state.show_confirmation and st.session_state.trip_details and not st.session_state.show_payment_simulation:
                # (Logic is unchanged)
                trip = st.session_state.trip_details
                st.divider(); st.markdown("## ✔️ Confirm Your Trip")
                col_d1, col_d2 = st.columns(2);
                with col_d1: st.markdown("#### Trip Summary"); st.write(f"**Dest:** {trip['destination_name']}"); st.write(f"**From:** {trip['start_city']}"); st.write(f"**Duration:** {trip['stay_days']}d"); st.write(f"**Persons:** {trip['num_people']}"); st.write(f"**Transport:** {trip['transport_mode']}"); st.write(f"**Distance:** {trip['distance_km']} km")
                with col_d2: st.markdown("#### Estimated Costs"); st.write(f"**Base:** ₹{trip['total_base_cost']:,.2f}"); st.write(f"**Transport:** ₹{trip['total_transport_cost']:,.2f}"); st.markdown(f"**Total:** **₹{trip['total_budget']:,.2f}**")
                st.divider(); st.markdown("#### Enter Your Details (Optional)")
                user_name_input = st.text_input("Your Name", value=name, key="user_name_confirm"); user_contact_input = st.text_input("Email or Phone", key="user_contact_confirm")
                if st.button("➡️ Proceed to Payment Simulation"): st.session_state.show_payment_simulation = True; st.rerun()

            # --- PAYMENT SIMULATION SECTION ---
            if st.session_state.show_payment_simulation and st.session_state.trip_details:
                # (Logic is unchanged, includes balloons + delay)
                trip = st.session_state.trip_details
                st.divider(); st.markdown("## 💳 Payment Simulation"); st.info("Scan QR code using UPI app (Simulation).")
                qr_data = f"upi://pay?pa=dummy-payee@okbank&pn=TripWala&am={trip['total_budget']:.2f}&cu=INR&tn=Trip to {trip['destination_name']}"
                qr_image = generate_qr_code(qr_data)
                col_qr, col_logos = st.columns([1, 2])
                with col_qr: st.image(qr_image, caption="Scan to Pay (Simulated)", width=150)
                with col_logos:
                    st.write("**Pay Using:**"); logo_col1, logo_col2, _ = st.columns(3)
                    with logo_col1: st.image(GPAY_LOGO_URL, width=60)
                    with logo_col2: st.image(PHONEPE_LOGO_URL, width=60)
                st.markdown("---")
                if st.button("✅ Payment Complete (Simulation)"):
                    booking_saved = db_utils.save_booking(username, trip)
                    if booking_saved: st.success(f"🎉 Payment Received & Trip Booked! (Simulation).")
                    else: st.error("⚠️ Payment simulation complete, but failed to save booking.")
                    st.balloons()
                    time.sleep(3) # Delay for balloons
                    st.session_state.trip_details = None; st.session_state.show_confirmation = False; st.session_state.show_payment_simulation = False
                    st.rerun()

        # --- Sidebar Filters ---
        # (Logic is unchanged)
        st.sidebar.markdown("## 🔍 Search & Filter")
        search_text = st.sidebar.text_input("Search by Destination Name")
        if not df.empty:
            region_filter = st.sidebar.selectbox("Filter by Region", options=["All"] + sorted(df['Location/Region'].unique()))
            min_cost_val = int(df["Average Cost"].min()) if not df.empty and not df["Average Cost"].isnull().all() else 0; max_cost_val = int(df["Average Cost"].max()) if not df.empty and not df["Average Cost"].isnull().all() else 1000
            step_val = 50; min_slider_val = (min_cost_val // step_val) * step_val; max_slider_val = ((max_cost_val // step_val) + 1) * step_val
            if max_slider_val <= min_slider_val: max_slider_val = min_slider_val + step_val
            options_range = range(min_slider_val, max_slider_val + step_val, step_val);
            if not list(options_range): options_range = [min_slider_val] if min_slider_val == max_slider_val else range(min_slider_val, min_slider_val + step_val, step_val)
            default_min = min(options_range); default_max = max(options_range);
            min_budget, max_budget = st.sidebar.select_slider("Filter by Base Budget (₹/day)", options=list(options_range), value=(default_min, default_max))
        else: st.sidebar.warning("⚠️ No data."); region_filter = "All"; min_budget, max_budget = 0, 1000

        # --- ROLE-BASED ADMIN SECTION ---
        if username == 'admin':
            st.sidebar.divider(); st.sidebar.markdown("## 🛠️ Admin Actions")
            if 'action' not in st.session_state: st.session_state.action = None
            if st.sidebar.button("➕ Add New"): st.session_state.action = "add"
            if st.sidebar.button("✏️ Update"): st.session_state.action = "update"
            if st.sidebar.button("🗑️ Delete"): st.session_state.action = "delete"
        else: st.session_state.action = None

        # --- Filter Logic ---
        # (Logic is unchanged)
        filtered_df = df.copy();
        if not filtered_df.empty:
            if search_text: filtered_df = filtered_df[filtered_df["Destination Name"].str.contains(search_text, case=False)]
            if region_filter != "All": filtered_df = filtered_df[filtered_df["Location/Region"] == region_filter]
            filtered_df = filtered_df[(filtered_df["Average Cost"] >= min_budget) & (filtered_df["Average Cost"] <= max_budget)]

        # --- ADMIN ACTION UI ---
        if username == 'admin':
            st.divider()
            if st.session_state.action == "add":
                st.markdown("### ➕ Add New Destination")
                with st.form("add_form", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        new_name = st.text_input("Name*")
                        new_region = st.text_input("Region*", "Maharashtra")
                        new_cost = st.number_input("Cost* (₹ p.p./day)", min_value=0, step=50)
                        # ADDED Image URL input
                        new_image_url = st.text_input("Image URL (Optional)", placeholder="https://.../image.jpg")
                    with c2:
                        new_highlights = st.text_area("Highlights*", height=150)
                    submitted = st.form_submit_button("✅ Add Destination");
                    if submitted:
                        if not all([new_name, new_region, new_highlights]) or new_cost < 0: st.error("❌ Fill required fields *.")
                        else:
                            # Pass 5 arguments
                            if db_utils.add_destination(new_name, new_region, new_highlights, new_cost, new_image_url):
                                st.toast(f"✅ Added {new_name}!", icon="🎉"); st.session_state.action = None; st.cache_data.clear(); st.rerun()
                            else: st.error("❌ Failed to add.")
            elif st.session_state.action == "update":
                st.markdown("### ✏️ Update Destination")
                if not df.empty:
                    all_dest_dict = df.drop_duplicates(subset=["Destination Name"]).set_index("Destination Name")["ID"].to_dict(); select_options = ["--Select--"] + sorted(all_dest_dict.keys()); selected_name = st.selectbox("Select destination", options=select_options)
                    if selected_name != "--Select--":
                        all_dest_details = db_utils.get_all_destinations(); dest_details_df = pd.DataFrame(all_dest_details); dest_row = dest_details_df[dest_details_df["name"] == selected_name].iloc[0]; st.session_state.edit_id = int(dest_row["id"])
                        with st.form("update_form"):
                             c1, c2 = st.columns(2)
                             with c1:
                                 up_name = st.text_input("Name*", dest_row["name"])
                                 up_region = st.text_input("Region*", dest_row["region"])
                                 up_cost = st.number_input("Cost* (₹ p.p./day)", min_value=0, step=50, value=int(dest_row["cost"]))
                                 # ADDED Image URL input
                                 up_image_url = st.text_input("Image URL", value=dest_row.get("image_url", ""))
                             with c2:
                                 up_highlights = st.text_area("Highlights*", dest_row["highlights"], height=150)
                             submitted = st.form_submit_button("💾 Update");
                             if submitted:
                                 if not all([up_name, up_region, up_highlights]) or up_cost < 0: st.error("❌ Fill required fields *.")
                                 else:
                                     # Pass 6 arguments
                                     if db_utils.update_destination(st.session_state.edit_id, up_name, up_region, up_highlights, up_cost, up_image_url):
                                         st.toast(f"✅ Updated {up_name}!", icon="👍"); st.session_state.action = None; st.session_state.edit_id = None; st.cache_data.clear(); st.rerun()
                                     else: st.error("❌ Failed to update.")
                else: st.warning("⚠️ No destinations to update.")
            elif st.session_state.action == "delete":
                 # (Logic is unchanged)
                 st.markdown("### 🗑️ Delete Destination")
                 if not df.empty:
                    all_dest_dict = df.drop_duplicates(subset=["Destination Name"]).set_index("Destination Name")["ID"].to_dict(); select_options = ["--Select--"] + sorted(all_dest_dict.keys()); selected_name = st.selectbox("Select destination", options=select_options)
                    if selected_name != "--Select--":
                        delete_id = all_dest_dict[selected_name]; st.warning(f"🚨 Delete **{selected_name}**?")
                        col_del1, col_del2 = st.columns([1, 4]);
                        with col_del1:
                            if st.button("Yes, Delete", type="primary"):
                                if db_utils.delete_destination(delete_id): st.toast(f"🗑️ Deleted {selected_name}.", icon="✅"); st.session_state.action = None; st.cache_data.clear(); st.rerun()
                                else: st.error("❌ Failed to delete.")
                        with col_del2:
                             if st.button("Cancel"): st.session_state.action = None; st.rerun()
                 else: st.warning("⚠️ No destinations to delete.")

        # --- Available Destinations Display ---
        st.divider(); st.markdown("### 📌 Available Destinations"); st.write("_Matching filters._"); st.caption("Cost ₹ p.p./day.")
        if filtered_df.empty: st.info("ℹ️ No matches.")
        else:
            displayed_names = set(); cols = st.columns(3); col_index = 0
            for index, row in filtered_df.iterrows():
                if row['Destination Name'] not in displayed_names:
                    with cols[col_index % 3]:
                        with st.container(border=True):
                            
                            # --- ROBUST IMAGE DISPLAY ---
                            image_url = row.get("Image URL")
                            if image_url and isinstance(image_url, str) and image_url.startswith("http"):
                                st.image(image_url, caption=f"{row['Destination Name']}")
                            else:
                                st.image(PLACEHOLDER_IMAGE_URL, caption="Image not available")
                            # --- END IMAGE DISPLAY ---

                            st.subheader(f"{row['Destination Name']}"); st.caption(f"{row['Location/Region']}")
                            st.write(f"**Highlights:** {row['Highlights']}")
                            st.metric(label="Base Cost", value=f"₹{row['Average Cost']}")
                    displayed_names.add(row['Destination Name']); col_index += 1


# --- LOGIN FAILURES / REGISTRATION ---
# (Logic is unchanged)
elif authentication_status is False: st.error('⚠️ Username/password incorrect')
elif authentication_status is None:
    st.warning('🔒 Please enter username and password')
    try:
        with st.expander("👤 New user? Register here!"):
            email, username_reg, name_reg = authenticator.register_user(location='main', fields={'Form name': 'Register New User'}, pre_authorized=None)
            if email:
                st.success('✅ User registered! Please log in.');
                try: 
                    with open('config.yaml', 'w') as file: yaml.dump(config, file, default_flow_style=False)
                except Exception as yaml_err: st.error(f"Failed to update config: {yaml_err}")
    except Exception as e: st.error(f"Reg error: {e}")