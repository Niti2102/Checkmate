import streamlit as st #getting of with streamlit
import os
import tempfile#to handle temporary files in file upload
import pandas as pd #data manipulation and tabular form display
from fpdf import FPDF #exporting pdf
from parser import parse_pdf_to_images
from crop import preprocess_image
from main import extract_cheque_details
import hashlib#for authentication passwd matching
from pymongo import MongoClient# connecting with mongodb

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017') #making the app to run in this localhost
db = client['cheque'] #database to store details
users_collection = db['cheque']#database to store user details
cheque_details_collection = db['cheque_details'] #database to store extracted details

# Helper functions for password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(hashed_password, user_password):
    return hashed_password == hash_password(user_password)

# Directory to save extracted images
output_folder = "./output_images"

# Clear the output folder at the start of a session
if os.path.exists(output_folder):  # Check if the folder exists
    for file_name in os.listdir(output_folder):  # Iterate through each file in the folder
        file_path = os.path.join(output_folder, file_name)  # Create the full path of the file
        try:
            if os.path.isfile(file_path):  # Check if it's a file (not a directory)
                os.unlink(file_path)  # Delete the file
        except Exception as e:
            st.error(f"Error deleting file {file_name}: {e}")  # Display an error if deleting fails
else:
    os.makedirs(output_folder)  # If the folder doesn't exist, create it


# Streamlit app setup
st.title("CheckMate: Automated Bank Check Processor") #displays title as check processor

# If the user has already logged in
if "user" in st.session_state:
    st.write(f"Hello {st.session_state.user}, Welcome to the Cheque Data Extraction Tool!")
    # Check if data is already extracted, prevent re-extraction
    if "extracted_data" not in st.session_state:
        st.session_state.extracted_data = []  # Initialize extracted_data if not already available

    # File upload section with multiple file selection
    uploaded_files = st.file_uploader("Upload PDF files or Images", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True)

    # When files are uploaded
    if uploaded_files:
        if not st.session_state.get("data_parsed", False):  # Prevent re-parsing if data already exists
            with st.spinner("Sit Back, Relax!"):
                # Process each uploaded file
                for uploaded_file in uploaded_files:
                    if uploaded_file.type == "application/pdf":
                        # Create a temporary file to save the uploaded PDF
                        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                            tmp_file.write(uploaded_file.getbuffer())
                            tmp_pdf_path = tmp_file.name
                    
                        # Parse the PDF into images
                        st.spinner("Parsing PDF...")
                        parse_pdf_to_images(tmp_pdf_path, output_folder)
                        st.success(f"PDF '{uploaded_file.name}' parsed successfully!")

                        # Get the list of images from the output folder
                        images = [f for f in os.listdir(output_folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))]

                        # Process each image
                        for img_name in images:
                            img_path = os.path.join(output_folder, img_name)

                            # Preprocess the image (optional if you need cropping)
                            crop_coords = (1280 - 370, 720 - 380, 370, 380)  # Example coordinates
                            preprocessed_image = preprocess_image(img_path, crop_coords)

                            # Extract cheque details from the image
                            details = extract_cheque_details(img_path, "./extracted_data")

                            # Store the details in the extracted_data list
                            if details:
                                cheque_record = {
                                    "username": st.session_state.user,
                                    "Payee Name": details.get("Payee Name", "Not Found"),
                                    "Bank Name": details.get("Bank Name", "Not Found"),
                                    "Amount": details.get("Amount", "Not Found"),
                                    "Cheque Number": details.get("Cheque Number", "Not Found"),
                                    "Account Number": details.get("Account Number", "Not Found"),
                                    "Date": details.get("Date", "Not Found")
                                }
                                st.session_state.extracted_data.append(cheque_record)

                                # Insert into MongoDB
                                cheque_details_collection.insert_one({key: value for key, value in cheque_record.items()})

                    elif uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
                        # Process the image directly if it's not a PDF
                        st.spinner(f"Processing image '{uploaded_file.name}'...")
                        img_path = os.path.join(output_folder, uploaded_file.name)

                        # Save the uploaded image
                        with open(img_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        # Preprocess the image (optional if you need cropping)
                        crop_coords = (1280 - 370, 720 - 380, 370, 380)  # Example coordinates
                        preprocessed_image = preprocess_image(img_path, crop_coords)

                        # Extract cheque details from the image
                        details = extract_cheque_details(img_path, "./extracted_data")

                        # Store the details in the extracted_data list
                        if details:
                            cheque_record = {
                                "username": st.session_state.user,
                                "Payee Name": details.get("Payee Name", "Not Found"),
                                "Bank Name": details.get("Bank Name", "Not Found"),
                                "Amount": details.get("Amount", "Not Found"),
                                "Cheque Number": details.get("Cheque Number", "Not Found"),
                                "Account Number": details.get("Account Number", "Not Found"),
                                "Date": details.get("Date", "Not Found")
                            }
                            st.session_state.extracted_data.append(cheque_record)

                            # Insert into MongoDB
                            cheque_details_collection.insert_one({key: value for key, value in cheque_record.items()})

            # Mark data as parsed to prevent re-parsing
            st.session_state["data_parsed"] = True

        # If data is available, display it in a tabular format
        if st.session_state.extracted_data:
            st.subheader("Extracted Cheque Details:")
            df = pd.DataFrame(st.session_state.extracted_data)

            st.table(df)

            # Generate CSV
            @st.cache_data
            def generate_csv(data):
                return data.to_csv(index=False)

            csv_data = generate_csv(df)
            st.download_button(
                label="Download as CSV",
                data=csv_data,
                file_name="cheque_details.csv",
                mime="text/csv"
            )

            # Generate PDF
            @st.cache_data
            def generate_pdf(data):
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()

                # Set title
                pdf.set_font("Arial", "B", 16)
                pdf.cell(200, 10, "Cheque Details", ln=True, align="C")

                # Set table headers
                pdf.set_font("Arial", "B", 12)
                headers = list(data.columns)
                for header in headers:
                    pdf.cell(40, 10, header, border=1, align="C")
                pdf.ln()

                # Add data to the table
                pdf.set_font("Arial", "", 12)
                for _, row in data.iterrows():
                    for value in row:
                        pdf.cell(40, 10, str(value), border=1, align="C")
                    pdf.ln()

                return pdf.output(dest='S').encode('latin1')

            # Create a download button for the PDF
            pdf_data = generate_pdf(df)
            st.download_button(
                label="Download as PDF",
                data=pdf_data,
                file_name="cheque_details.pdf",
                mime="application/pdf"
            )

        else:
            st.warning("No cheque details found. Please upload files first.")
    else:
        st.warning("Please upload a PDF file or image to extract details.")

    # Logout button
    if st.button("Logout"):
        del st.session_state.user
        del st.session_state.extracted_data  # Clear the extracted data when logging out
        del st.session_state["data_parsed"]  # Reset the parsing flag
  # Reset the parsing flag
        st.success("Logged out successfully!")
        st.rerun()

else:
    # Display registration or login form based on the app_mode
    app_mode = st.radio("Choose an option", ("Login", "Sign Up"))

    if app_mode == "Sign Up":
        st.subheader("Create a New Account")

        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Register"):
            existing_user = users_collection.find_one({"username": new_username})
            if existing_user:
                st.error("Username already exists!")
            elif new_password != confirm_password:
                st.error("Passwords do not match!")
            else:
                hashed_password = hash_password(new_password)

                users_collection.insert_one({
                    "username": new_username,
                    "password": hashed_password
                })

                st.success("Account created successfully! You can now log in.")
                st.rerun()

    elif app_mode == "Login":
        st.subheader("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = users_collection.find_one({"username": username})
            if user and check_password(user["password"], password):
                st.success("Login successful!")
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid username or password")
