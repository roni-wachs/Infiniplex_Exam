import sys
import cv2
import pytesseract
import numpy as np

"""
    Function to preprocess input image.
    Args: image_path (str) - path to the input image (JPG or PNG).
    Returns: image (numpy.ndarray) - processed image (binary format) ready for digit detection.
"""
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    #Convert the image to grayscale for better processing
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #Apply adaptive thresholding to binarize the image for better digit recognition.
    image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    return image

"""
    Function to detect number from a preprocessed image using OCR model (Tesseract).
    Args: image (numpy.ndarray) - preprocessed binary image containing potential digits.
    Returns: number (str) - detected number as string, or "none" if no number is found.
"""
def detect_number(image):
    number = pytesseract.image_to_string(image, config="--psm 7 -c tessedit_char_whitelist=0123456789.")
    number = number.strip()
    if number:
        for char in number:
            if char.isdigit():
                return number
    return "none"


def main():
    #Check if correct number of arguments is provided
    if len(sys.argv) != 2:
        print("Error: Please provide exactly one image file (JPG or PNG) as input")
        sys.exit(1)

    #Extract image path from command-line argument
    image_path = sys.argv[1]
    #Preprocess image
    image = preprocess_image(image_path)
    #Detect the number in preprocessed image
    detected_number = detect_number(image)
    print(detected_number)

if __name__ == "__main__":
    main()
