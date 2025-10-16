import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os

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
    st.subheader("📸 Model Photo")
    base_photo = st.file_uploader(
        "Upload model image",
        type=['jpg', 'jpeg', 'png'],
        key="base",
        help="Photo of the person without jewelry"
    )
    if base_photo:
        st.image(base_photo, caption="Model Photo", use_container_width=True)

with col2:
    st.subheader("💍 Jewelry Photo")
    jewelry_photo = st.file_uploader(
        "Upload jewelry image",
        type=['jpg', 'jpeg', 'png'],
        key="jewelry",
        help="Image of the jewelry piece (preferably transparent PNG)"
    )
    if jewelry_photo:
        st.image(jewelry_photo, caption="Jewelry Photo", use_container_width=True)

# Generation section
st.markdown("---")

# Advanced options (collapsed by default)
with st.expander("🎨 Advanced Options"):
    custom_prompt = st.text_area(
        "Custom Instructions (Optional)",
        placeholder="e.g., 'Make the necklace silver and shiny' or 'Position earring on left ear only'",
        height=100
    )

# Generate button
if st.button("✨ Generate Virtual Try-On", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ Please enter your Google AI API key in the sidebar")
    elif not base_photo or not jewelry_photo:
        st.error("⚠️ Please upload both a model photo and jewelry photo")
    else:
        with st.spinner("🎨 Creating photorealistic image... This may take 10-30 seconds"):
            try:
                # Configure Gemini
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                
                # Load images
                base_img = Image.open(base_photo)
                jewelry_img = Image.open(jewelry_photo)
                
                # Create prompt
                base_prompt = """Place this jewelry on the model naturally and photorealistically. 
                The result must look like a real photoshoot where the person is actually wearing the jewelry.
                
                Requirements:
                - Position and scale the jewelry correctly on the appropriate body part (ear, neck, or wrist)
                - Match the lighting and create natural shadows where jewelry touches skin
                - Ensure proper depth and perspective - jewelry should follow body contours
                - Handle occlusion naturally (hair or clothing may partially cover jewelry)
                - Blend seamlessly with no harsh edges or floating appearance
                - Preserve the person's identity and features exactly
                - Make metal reflections adapt to the scene lighting
                
                Output a single photorealistic image that looks professional and natural."""
                
                if custom_prompt:
                    base_prompt += f"\n\nAdditional instructions: {custom_prompt}"
                
                # Generate
                response = model.generate_content([
                    base_prompt,
                    base_img,
                    jewelry_img
                ])
                
                # Display result
                st.success("✅ Generated successfully!")
                st.subheader("🎉 Result")
                
                # Check if response contains an image
                if hasattr(response, 'parts'):
                    for part in response.parts:
                        if hasattr(part, 'inline_data'):
                            # Extract image data
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
                            break
                    else:
                        st.warning("⚠️ No image was generated. Response: " + str(response.text))
                else:
                    st.warning("⚠️ Unexpected response format: " + str(response))
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Tip: Make sure your API key is correct and has access to Gemini 2.0")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>💎 Professional Jewelry Virtual Try-On powered by Google Gemini AI</p>
    <p>For support or questions, contact your developer</p>
    </div>
    """,
    unsafe_allow_html=True
)