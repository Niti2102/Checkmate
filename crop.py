import cv2
import numpy as np
from PIL import Image
import os

def preprocess_image(image_path, crop_coords):
    """
    Preprocess an image for text extraction with error handling.

    Args:
        image_path (str): Path to the image.
        crop_coords (tuple): Coordinates for cropping (start_x, start_y, width, height).

    Returns:
        np.array: Preprocessed image or None in case of error.
    """
    # Check if the file exists
    if not os.path.exists(image_path):
        print(f"Error: The file {image_path} does not exist.")
        return None

    try:
        # Open the image using PIL
        image = Image.open(image_path).convert('RGB')
        image = np.array(image)
    except Exception as e:
        print(f"Error: Failed to load image from {image_path}. {e}")
        return None

    # Validate crop coordinates
    if not isinstance(crop_coords, tuple) or len(crop_coords) != 4:
        print("Error: Invalid crop coordinates. It should be a tuple of four values.")
        return None

    start_x, start_y, width, height = crop_coords

    # Check if cropping coordinates are within the image dimensions
    if start_x < 0 or start_y < 0 or start_x + width > image.shape[1] or start_y + height > image.shape[0]:
        print(f"Error: Crop coordinates {crop_coords} are out of bounds for the image size {image.shape}.")
        return None

    # Perform cropping
    cropped = image[start_y:start_y + height, start_x:start_x + width]

    try:
        # Convert to grayscale and then apply binary thresholding
        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    except Exception as e:
        print(f"Error: Failed to preprocess image {image_path}. {e}")
        return None

    return binary_image
