import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def extract_cheque_details(image_path, output_folder):
    """
    Extracts cheque details using Google Generative AI.

    Args:
        image_path (str): Path to the image.
        output_folder (str): Folder to save extracted JSON.

    Returns:
        dict: Extracted cheque details.
    """
    input_prompt = """
    Extract the following details from the cheque image:
    1. Bank Name
    2. Payee Name
    3. Amount
    4. Date
    5. Account Number
    6. Cheque Number
    Return the details as a JSON object.
    """
   
    try:
        image = Image.open(image_path)
        response = model.generate_content([input_prompt, image])
        cheque_data = json.loads(response.text.strip(" ```json"))
        json_path = os.path.join(output_folder, f"{cheque_data['Cheque Number']}_details.json")
        with open(json_path, 'w') as json_file:
            json.dump(cheque_data, json_file, indent=2)
        return cheque_data
    except Exception as e:
        return {"error": str(e)}
