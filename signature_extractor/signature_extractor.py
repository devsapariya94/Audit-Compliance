import streamlit as st
from PIL import Image
import pytesseract
from transformers import pipeline
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import measure, morphology
from skimage.color import label2rgb
from skimage.measure import regionprops

# Function to extract text using OCR
def extract_text(image):
    text = pytesseract.image_to_string(image)
    return text

# Function to check form details using LLM
def check_form_details(text):
    # classifier = pipeline("text-classification", model="path/to/finetuned/model")
    # response = classifier(text)
    response = "Form details are compliant"
    return response

# Function to process signatures and save the processed document
def process_signatures(image_path, output_path='./outputs/processed_document.png'):
    # the parameters are used to remove small size connected pixels outliar 
    constant_parameter_1 = 84
    constant_parameter_2 = 250
    constant_parameter_3 = 100

    # the parameter is used to remove big size connected pixels outliar
    constant_parameter_4 = 18

    # read the input image
    img = cv2.imread(image_path, 0)
    img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)[1]  # ensure binary

    # connected component analysis by scikit-learn framework
    blobs = img > img.mean()
    blobs_labels = measure.label(blobs, background=1)
    image_label_overlay = label2rgb(blobs_labels, image=img)

    the_biggest_component = 0
    total_area = 0
    counter = 0

    for region in regionprops(blobs_labels):
        if (region.area > 10):
            total_area = total_area + region.area
            counter = counter + 1
        if (region.area >= 250):
            if (region.area > the_biggest_component):
                the_biggest_component = region.area

    average = (total_area / counter)
    a4_small_size_outliar_constant = ((average / constant_parameter_1) * constant_parameter_2) + constant_parameter_3
    a4_big_size_outliar_constant = a4_small_size_outliar_constant * constant_parameter_4

    pre_version = morphology.remove_small_objects(blobs_labels, a4_small_size_outliar_constant)
    component_sizes = np.bincount(pre_version.ravel())
    too_small = component_sizes > (a4_big_size_outliar_constant)
    too_small_mask = too_small[pre_version]
    pre_version[too_small_mask] = 0

    # Save the processed document
    plt.imsave('pre_version.png', pre_version)
    img = cv2.imread('pre_version.png', 0)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cv2.imwrite(output_path, img)

    return output_path

# Streamlit app
st.title("Bank Account Opening Form Compliance Check")

uploaded_file = st.file_uploader("Upload a photo of the bank account opening form", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded form", use_column_width=True)

    # Save the uploaded image for processing
    image_path = "uploaded_image.png"
    image.save(image_path)

    # Perform OCR and compliance checks
    if st.button("Perform Compliance Check"):
        text = extract_text(image)
        st.text("Extracted Text:")
        st.text(text)
        
        # Verify form details using LLM
        response = check_form_details(text)
        st.text("Form Details Check:")
        st.text(response)
        
        # Process signatures and save the processed document
        processed_document_path = process_signatures(image_path)
        st.text("Processed Document Saved At:")
        st.text(processed_document_path)
        st.image(processed_document_path, caption="Processed Document", use_column_width=True)
        
        # Perform compliance checks
        # Add any additional compliance checks here
        compliance_result = True  # Example check
        st.text(f"Compliance Check Result: {compliance_result}")
