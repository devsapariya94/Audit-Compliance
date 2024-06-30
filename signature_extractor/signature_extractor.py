import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pytesseract
import os

def verify_signatures(image):
    # Convert PIL Image to OpenCV format
    opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Get image dimensions
    height, width = opencv_image.shape[:2]
    
    # Preprocessing
    gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours based on area (adjust these values based on your form)
    signature_contours = [cnt for cnt in contours if 1000 < cv2.contourArea(cnt) < 20000]
    
    customer_signature = None
    officer_signature = None
    
    for cnt in signature_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if x < width // 2:  # Left half (customer)
            customer_signature = opencv_image[y:y+h, x:x+w]
        else:  # Right half (officer)
            officer_signature = opencv_image[y:y+h, x:x+w]
    
    # Create a directory to save signatures if it doesn't exist
    os.makedirs("signatures", exist_ok=True)
    
    customer_signed = False
    officer_signed = False
    
    if customer_signature is not None:
        cv2.imwrite("signatures/customer_signature.png", customer_signature)
        customer_signed = True
    
    if officer_signature is not None:
        cv2.imwrite("signatures/officer_signature.png", officer_signature)
        officer_signed = True
    
    # Draw rectangles around detected signatures
    result_image = opencv_image.copy()
    for cnt in signature_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if x < width // 2:
            cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green for customer
        else:
            cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red for officer
    
    return customer_signed, officer_signed, result_image

# Streamlit app
def main():
    st.title("Bank Account Opening Form Compliance Check")

    # File uploader
    uploaded_file = st.file_uploader("Upload a photo of the bank account opening form", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Form", use_column_width=True)

        # Verify signatures
        customer_signed, officer_signed, result_image = verify_signatures(image)

        # Display result image with detected signatures
        st.image(result_image, caption="Detected Signatures", use_column_width=True)

        # Display results
        st.subheader("Signature Check Results")
        st.write(f"Customer signature detected: {'Yes' if customer_signed else 'No'}")
        st.write(f"Officer signature detected: {'Yes' if officer_signed else 'No'}")

        # Display saved signatures
        if customer_signed:
            customer_sig = Image.open("signatures/customer_signature.png")
            st.image(customer_sig, caption="Customer Signature", width=200)
        
        if officer_signed:
            officer_sig = Image.open("signatures/officer_signature.png")
            st.image(officer_sig, caption="Officer Signature", width=200)

if __name__ == "__main__":
    main()