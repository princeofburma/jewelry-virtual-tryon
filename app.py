import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64

# Page config
st.set_page_config(
    page_title="Jewelry Virtual Try-On",
    page_icon="💎",
    layout="centered"
)

# Title and description
st.title("💎 Jewelry Virtual Try-On")
st.markdown("Upload a model photo and jewelry image to see them combined realistically")

# API Key input (in sidebar for security)
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Google AI API Key", type="password", help="Get your key from ai.google.dev")
    
    if api_key:
        st.success("API Key configured ✓")
    else:
        st.warning("Please enter your API key to continue")

# Main interface
col1, col2 = st.columns(2)

with col1:
    st.subheader("💍 Jewelry Photo (Photo 1)")
    jewelry_photo = st.file_uploader(
        "Upload jewelry image",
        type=['jpg', 'jpeg', 'png'],
        key="jewelry",
        help="Image of the jewelry piece"
    )
    if jewelry_photo:
        st.image(jewelry_photo, caption="Jewelry Photo", use_container_width=True)

with col2:
    st.subheader("📸 Model Photo (Photo 2)")
    base_photo = st.file_uploader(
        "Upload model image",
        type=['jpg', 'jpeg', 'png'],
        key="base",
        help="Photo of the person without jewelry"
    )
    if base_photo:
        st.image(base_photo, caption="Model Photo", use_container_width=True)

# Generation section
st.markdown("---")

# Generate button
if st.button("✨ Generate Virtual Try-On", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ Please enter your Google AI API key in the sidebar")
    elif not base_photo or not jewelry_photo:
        st.error("⚠️ Please upload both a jewelry photo and model photo")
    else:
        with st.spinner("🎨 Creating photorealistic image... This may take 10-30 seconds"):
            try:
                # Configure API
                genai.configure(api_key=api_key)
                
                # Load images
                jewelry_img = Image.open(jewelry_photo)
                base_img = Image.open(base_photo)
                
                # Simple prompt like in AI Studio
                prompt = "add the necklace in photo 1 to the model in photo 2"
                
                # Use Imagen model (Nano Banana)
                model = genai.GenerativeModel('imagen-3.0-generate-001')
                
                response = model.generate_content(
                    [prompt, jewelry_img, base_img]
                )
                
                # Display result
                st.success("✅ Generated successfully!")
                st.subheader("🎉 Result")
                
                # Try to extract image from response
                image_found = False
                
                # Check for image in response
                if hasattr(response, 'candidates') and response.candidates:
                    for candidate in response.candidates:
                        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                            for part in candidate.content.parts:
                                if hasattr(part, 'inline_data') and part.inline_data:
                                    try:
                                        img_data = part.inline_data.data
                                        result_img = Image.open(io.BytesIO(img_data))
                                        
                                        # Display
                                        st.image(result_img, caption="Virtual Try-On Result", use_container_width=True)
                                        
                                        # Download button
                                        buf = io.BytesIO()
                                        result_img.save(buf, format='PNG')
                                        st.download_button(
                                            label="⬇️ Download Result",
                                            data=buf.getvalue(),
                                            file_name="jewelry_tryon_result.png",
                                            mime="image/png",
                                            use_container_width=True
                                        )
                                        image_found = True
                                        break
                                    except Exception as img_error:
                                        st.error(f"Error processing image: {str(img_error)}")
                        if image_found:
                            break
                
                if not image_found:
                    st.warning("⚠️ Could not extract image from response")
                    st.info(f"Response type: {type(response)}")
                    if hasattr(response, 'text'):
                        st.write("Text response:", response.text)
                    st.info("""
                    **Note:** Imagen/Nano Banana may not be available in all regions or API keys.
                    Make sure your API key has access to image generation models.
                    """)
                    
            except Exception as e:
                error_msg = str(e)
                st.error(f"❌ Error: {error_msg}")
                
                if "imagen" in error_msg.lower() or "not found" in error_msg.lower():
                    st.info("""
                    **Imagen/Nano Banana Access Issue:**
                    
                    The Imagen model (Nano Banana) may not be available via the API yet, or your API key doesn't have access.
                    
                    **Alternative Solutions:**
                    1. Check if Imagen is available in your region at ai.google.dev
                    2. Use Replicate with Stable Diffusion (I can rebuild the app for this)
                    3. Use OpenAI DALL-E 3 (I can rebuild the app for this)
                    4. Use a specialized jewelry API
                    
                    Let me know which alternative you'd like to try!
                    """)
                else:
                    st.info("Check your API key and make sure it has the necessary permissions.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>💎 Jewelry Virtual Try-On powered by Google Imagen (Nano Banana)</p>
    </div>
    """,
    unsafe_allow_html=True
)
