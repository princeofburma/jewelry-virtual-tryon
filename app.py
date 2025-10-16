import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

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
    
    # Model selection
    model_choice = st.selectbox(
        "Select Model",
        ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash-exp"],
        index=0
    )
    
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
                
                # Load images
                base_img = Image.open(base_photo)
                jewelry_img = Image.open(jewelry_photo)
                
                # Create prompt - simplified for better results
                base_prompt = """Create a photorealistic image showing this person wearing this jewelry naturally.

Instructions:
- Place the jewelry on the appropriate body part (neck for necklace, ear for earring, wrist for bracelet)
- Match the lighting of the original photo
- Add natural shadows where the jewelry touches skin
- Make it look like a real photograph, not edited
- Keep the person's face and features exactly the same
- Blend the jewelry seamlessly with proper depth and perspective"""
                
                if custom_prompt:
                    base_prompt += f"\n\nAdditional: {custom_prompt}"
                
                base_prompt += "\n\nGenerate only the final image with the person wearing the jewelry."
                
                # Try generation with the selected model
                model = genai.GenerativeModel(model_choice)
                
                response = model.generate_content(
                    [base_prompt, base_img, jewelry_img],
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.4,
                    )
                )
                
                # Display result
                st.success("✅ Generated successfully!")
                st.subheader("🎉 Result")
                
                # Try to extract image from response
                image_found = False
                
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
                    # If no image found, show the text response
                    st.warning("⚠️ The model returned a text response instead of an image.")
                    st.info("**Model Response:**")
                    st.write(response.text if hasattr(response, 'text') else str(response))
                    st.info("""
                    **Troubleshooting Tips:**
                    1. Make sure you're using an API key with image generation enabled
                    2. Try using 'gemini-1.5-pro' model (select in sidebar)
                    3. Gemini models may have varying image generation capabilities
                    4. Consider using a dedicated image generation API like Stable Diffusion or DALL-E
                    """)
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("""
                **Common Issues:**
                - API key may not have access to the selected model
                - Image generation may not be available in your region
                - Try a different model from the sidebar
                - Check your API quota at ai.google.dev
                """)

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
