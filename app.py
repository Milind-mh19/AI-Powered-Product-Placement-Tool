import streamlit as st
from rembg import remove
import requests
from PIL import Image
from io import BytesIO
import os

# Streamlit app title and description
st.title("🛍 AI-Powered Product Placement Tool🖼")
st.write("A Generative AI tool that seamlessly integrates e-commerce product images into lifestyle backgrounds,ensuring realistic lighting, perspective.")

# Create directories for original and masked images
os.makedirs('original', exist_ok=True)
os.makedirs('masked', exist_ok=True)

# Upload image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Save the uploaded image
    img_name = uploaded_file.name
    img = Image.open(uploaded_file)
    img.save(f'original/{img_name}', format='jpeg' if img_name.lower().endswith('.jpg') else 'png')

    # Remove the background
    with open(f'original/{img_name}', 'rb') as f:
        input_image = f.read()
        output_image = remove(input_image, alpha_matting=True, alpha_matting_foreground_threshold=240)

    # Save the image with the background removed
    output_path = f'masked/{img_name}'
    with open(output_path, 'wb') as f:
        f.write(output_image)

    
    st.write("### Paste onto a Background")
    background_option = st.radio("Choose a background:", ["Default Background", "Upload Your Own Background"])

    if background_option == "Default Background":
        # default background image
        background_img_url = 'https://img.freepik.com/free-photo/3d-wooden-table-looking-out-defocussed-modern-living-room_1048-9817.jpg'
        background_img = Image.open(BytesIO(requests.get(background_img_url).content))
    else:
        # Allow the user to upload a custom background
        uploaded_background = st.file_uploader("Upload a background image", type=["jpg", "jpeg", "png"])
        if uploaded_background is not None:
            background_img = Image.open(uploaded_background)
        else:
            st.warning("Please upload a background image.")
            st.stop()

    # Open the foreground image (with background removed)
    foreground_img = Image.open(output_path)

    # Resize the foreground image to a smaller size (e.g., 50% of its original size)
    scale_factor = st.slider("Resize Foreground Image", 0.1, 1.0, 0.5)  # Adjust scale factor
    new_size = (int(foreground_img.width * scale_factor), int(foreground_img.height * scale_factor))
    foreground_img = foreground_img.resize(new_size, Image.Resampling.LANCZOS)

    # Calculate the position to paste the foreground image (e.g., center of the background image)
    position = (
        (background_img.width - foreground_img.width) // 2,  # Centered horizontally
        (background_img.height - foreground_img.height) // 2  # Centered vertically
    )

    # Composite the foreground image onto the background image
    background_img.paste(foreground_img, position, foreground_img)

    # Display the final composited image
    st.image(background_img, caption="Final Composited Image", use_column_width=True)

    # Save the final composited image
    final_output_path = f'masked/composited_{img_name}'
    background_img.save(final_output_path, format='jpeg' if img_name.lower().endswith('.jpg') else 'png')
    st.success(f"Final image saved as {final_output_path}")