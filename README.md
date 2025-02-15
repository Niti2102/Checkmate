🏦💰 Bank Cheque Processing Automation 🏦💰

📌 Overview
An advanced system designed to 🤖 automate the 🏦 cheque processing task. By leveraging cutting-edge technologies like 🔍 Optical Character Recognition (OCR), 🖼️ image preprocessing, and 🤖 machine learning, this system efficiently extracts key cheque details and stores them in structured formats for easy access and analysis.

✨ Features
- **📄 Automated Cheque Scanning**: Processes scanned cheque images and extracts relevant details.
- **🎨 Image Preprocessing**: Enhances image quality for better extraction accuracy.
- **📊 Key Data Extraction**: Extracts essential details such as:
  - 🏦 Bank Name
  - 👤 Payee Name
  - 💲 Amount
  - 📆 Date
  - 🔢 Account Number
  - 🔖 Cheque Number
- **📂 Multi-Format Export**: Saves extracted data in:
  - 📄 PDF
  - 📑 CSV
- **🗄️ MongoDB Storage**: Stores structured cheque details in a MongoDB database.
- **🌟 Gemini API Integration**: Uses the Gemini API for enhanced cheque detail extraction accuracy.

🛠️ Technologies Used
- 🐍 **Python**
- 🎭 **OpenCV** (🖼️ Image Processing)
- 🔮 **Gemini API** (🔍 For detail extraction)
- 🤖 **Machine Learning** (📈 For enhanced accuracy)
- 📊 **Pandas** (📄 Data Handling)
- 📝 **FPDF** (📄 PDF Generation)
- 🗄️ **MongoDB** (💾 Database Storage)

## 🔧 Installation
### 📌 Prerequisites
Ensure you have the following installed:
- 🐍 Python 3.x
- 🗄️ MongoDB

🚀 Setup
1. 📥 Clone the repository:
   ```bash
   git clone https://github.com/yourusername/bank-cheque-automation.git
   cd bank-cheque-automation
   ```
2. 📦 Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. 🔧 Configure MongoDB connection in `config.py`.
4. 🔑 Set up the Gemini API key in `config.py`.
5. ▶️ Run the application:
   ```bash
   python main.py
   ```

📌 Usage
1. 📤 Upload scanned cheque images to the system.
2. 🖥️ The system processes the cheque, extracts details using the Gemini API, and saves them in 🗄️ MongoDB.
3. 📥 Download extracted data in 📄 PDF or 📑 CSV format.
   
🤝 Contributing
1. 🍴 Fork the repository.
2. 🌿 Create a new branch (`feature-branch`).
3. 💾 Commit your changes.
4. 🚀 Push to your branch and create a Pull Request.

## 📜 License
This project is licensed under the 🏛️ MIT License.

## 📞 Contact
For any 🛠️ issues or ✨ feature requests, feel free to raise an issue or contact the maintainer. 😊

