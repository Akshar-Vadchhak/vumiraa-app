import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- CONNECT TO GOOGLE SHEETS (THE CLOUD) ---
# This allows the app to work from ANY device (Phone or Laptop) and see the same data
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
# NEW CODE (PASTE THIS)
# We use st.secrets to read the data you pasted in the cloud settings
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)

# Open the Google Sheet
SHEET_NAME = "VumiraaDB" # Make sure this matches your Sheet name exactly
sheet = client.open(SHEET_NAME).sheet1

st.set_page_config(page_title="Vumiraa App", layout="wide")

# --- FUNCTIONS ---
def load_data():
    # Get all records from the cloud
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def add_data(row_data):
    # Add a row to the cloud
    sheet.append_row(row_data)

# --- APP INTERFACE ---
st.title("Vumiraa Inventory ☁️")

# Navigation
menu = st.sidebar.radio("Menu", ["Search", "Add Product"])

if menu == "Search":
    st.header("Search Database")
    df = load_data()
    
    search = st.text_input("Enter SKU ID")
    if search:
        # Filter data
        results = df[df['SKU ID'].astype(str).str.contains(search, case=False)]
        if not results.empty:
            for idx, row in results.iterrows():
                st.info(f"Product: {row['Product name']}")
                st.write(f"Price: {row['Flipkart Price']} | Stock: {row['Stock Unit']}")
                # Display image from URL if available
                if str(row['Image URL']).startswith("http"):
                    st.image(row['Image URL'], width=200)
                st.markdown("---")
        else:
            st.warning("Not found.")
    else:
        st.dataframe(df)

elif menu == "Add Product":
    st.header("Add to Cloud")
    with st.form("add_form"):
        sku = st.text_input("SKU ID")
        name = st.text_input("Product Name")
        price = st.number_input("Price")
        stock = st.number_input("Stock")
        img_url = st.text_input("Image Link (Paste URL)")
        
        if st.form_submit_button("Save to Cloud"):
            if sku:
                # Save to Google Sheets
                add_data([sku, name, price, stock, "Live", img_url])
                st.success("Saved! Check your other devices.")
            else:

                st.error("SKU required")
