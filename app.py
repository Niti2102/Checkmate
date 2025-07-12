import streamlit as st
import os
import tempfile
import pandas as pd
from fpdf import FPDF
from parser import parse_pdf_to_images
from crop import preprocess_image
from main import extract_cheque_details
import hashlib
from pymongo import MongoClient

# ✅ Inject custom CSS for modern styling
with open("custom_styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ✅ MongoDB setup
client = MongoClient('mongodb://localhost:27017')
db = client['cheque']
users_collection = db['cheque']
cheque_details_collection = db['cheque_details']

# ✅ Password helpers
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(hashed_password, user_password):
    return hashed_password == hash_password(user_password)

# ✅ Clear output image folder
output_folder = "./output_images"
os.makedirs(output_folder, exist_ok=True)
for file_name in os.listdir(output_folder):
    file_path = os.path.join(output_folder, file_name)
    if os.path.isfile(file_path):
        os.unlink(file_path)

# ✅ Page Header
st.markdown("<h1 style='text-align: center; font-size: 3rem;'>🧠 CheckMate: Smart Cheque Reader</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #ccc;'>Upload your cheque PDFs or images and get all details extracted instantly!</h4>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ✅ Main App Logic
if "user" in st.session_state:
    st.success(f"👋 Welcome, {st.session_state.user}!")

    if "extracted_data" not in st.session_state:
        st.session_state.extracted_data = []

    uploaded_files = st.file_uploader("📤 Upload Cheque PDF/Image", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True)

    if uploaded_files:
        if not st.session_state.get("data_parsed", False):
            with st.spinner("🧠 Processing..."):
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(output_folder, uploaded_file.name)

                    if uploaded_file.type == "application/pdf":
                        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                            tmp_file.write(uploaded_file.getbuffer())
                            tmp_pdf_path = tmp_file.name

                        parse_pdf_to_images(tmp_pdf_path, output_folder)
                        st.success(f"✅ PDF '{uploaded_file.name}' parsed!")

                        images = [f for f in os.listdir(output_folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))]

                        for img_name in images:
                            img_path = os.path.join(output_folder, img_name)
                            crop_coords = (910, 340, 370, 380)
                            preprocess_image(img_path, crop_coords)
                            details = extract_cheque_details(img_path, "./extracted_data")

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
                                cheque_details_collection.insert_one(cheque_record)

                    elif uploaded_file.type.startswith("image/"):
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        crop_coords = (910, 340, 370, 380)
                        preprocess_image(file_path, crop_coords)
                        details = extract_cheque_details(file_path, "./extracted_data")
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
                            cheque_details_collection.insert_one(cheque_record)

            st.session_state["data_parsed"] = True

    if st.session_state.extracted_data:
        st.subheader("📄 Extracted Cheque Details")
        df = pd.DataFrame(st.session_state.extracted_data)
        st.table(df)

        @st.cache_data
        def generate_csv(data):
            return data.to_csv(index=False)

        csv_data = generate_csv(df)
        st.download_button("⬇️ Download as CSV", csv_data, "cheque_details.csv", "text/csv")

        @st.cache_data
        def generate_pdf(data):
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, "Cheque Details", ln=True, align="C")
            pdf.set_font("Arial", "B", 12)
            for header in list(data.columns):
                pdf.cell(40, 10, header, border=1, align="C")
            pdf.ln()
            pdf.set_font("Arial", "", 12)
            for _, row in data.iterrows():
                for value in row:
                    pdf.cell(40, 10, str(value), border=1, align="C")
                pdf.ln()
            return pdf.output(dest='S').encode('latin1')

        pdf_data = generate_pdf(df)
        st.download_button("⬇️ Download as PDF", pdf_data, "cheque_details.pdf", "application/pdf")
    else:
        st.info("📁 Upload some cheque files to begin.")

    if st.button("🚪 Logout"):
        del st.session_state.user
        del st.session_state.extracted_data
        del st.session_state["data_parsed"]
        st.success("Logged out!")
        st.rerun()

else:
    app_mode = st.radio("🔐 Choose Mode", ("Login", "Sign Up"))

    if app_mode == "Sign Up":
        st.subheader("📝 Create a New Account")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Register"):
            if users_collection.find_one({"username": new_username}):
                st.error("❌ Username already exists!")
            elif new_password != confirm_password:
                st.error("❌ Passwords do not match!")
            else:
                users_collection.insert_one({
                    "username": new_username,
                    "password": hash_password(new_password)
                })
                st.success("✅ Account created! Please login.")
                st.rerun()

    elif app_mode == "Login":
        st.subheader("🔓 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = users_collection.find_one({"username": username})
            if user and check_password(user["password"], password):
                st.success("✅ Login successful!")
                st.session_state.user = username
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
