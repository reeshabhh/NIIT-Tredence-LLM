
import streamlit as st
import openai, os
import requests
from PIL import Image
from io import BytesIO

# Set up the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    # api_key=openai_api_key
)

# Define a function to generate images from text prompts
def generate_image(text, client, size="1024x1024"):
    try:
        # Send the prompt to the DALL-E API and get the generated image
        response = client.images.generate(
            model  = "dall-e-3",
            prompt = text,
            quality= "standard",
            n      = 1,
            size   = size
        )
        
        # Extract the URL of the generated image
        image_url = response.data[0].url
        
        # Fetch the image from the URL
        image_response = requests.get(image_url)
        
        # Open the image using PIL and return it
        img = Image.open(BytesIO(image_response.content))
        
        return img
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Main function to run the Streamlit app
def main():
    # Initialize the image variable
    image = None
    
    # Initialize suggestions in session state if it doesn’t exist
    if 'suggestions' not in st.session_state:
        st.session_state.suggestions = None
    
    # Streamlit UI setup
    st.title("Netflix Campaign Image Generator")
    st.write("Generate unique images for banners and posters by entering a text prompt.")

    # Structured input fields
    scene_description  = st.text_input("Scene Description",  placeholder="Describe the main scene...", value = "Space station overlooking Earth")
    style_elements     = st.text_input("Stylistic Elements", placeholder="e.g., Neon lights, dark tones, cyberpunk style", value = "Warm, golden light")
    mood               = st.text_input("Mood/Emotion",       placeholder="e.g., Mysterious, energetic", value = "Epic and powerful")
    additional_objects = st.text_input("Additional Objects", placeholder="e.g., Robot, street vendor", value  = "Futuristic astronaut exploring")
    
    # Scene Description
    # Fantasy Landscape: 
    #   "Ancient forest under a full moon," "Misty mountains at sunrise," "Enchanted garden with mystical flowers"
    # Urban Setting: 
    #   "Bustling city street in the rain," "Rooftop view over a futuristic skyline," "Deserted alleyway with graffiti"
    # Nature Scene: 
    #   "Serene beach with turquoise waters," "Snow-covered forest in winter," "Sunset over a golden wheat field"
    # Historical Setting: 
    #   "Medieval castle on a foggy hill," "Renaissance marketplace in a European town," "Victorian-era street with gas lamps"
    # Sci-Fi Environment: 
    #   "Alien planet with two suns," "Underwater futuristic city," "Space station overlooking Earth"
    
    # Stylistic Elements
    # Lighting and Color: "Warm, golden light," "Neon lights with vibrant tones," "Soft pastel hues"
    # Artistic Styles: "Impressionistic brush strokes," "Cubist shapes and colors," "Vintage sepia tones"
    # Textures and Details: "Worn-out, rustic textures," "Sharp, metallic finishes," "Soft, dreamy blurs"
    # Time of Day or Season: "Autumn colors with falling leaves," "Dawn with a misty glow," "Winter snowstorm"
    # Cultural Influences: "Japanese ink wash style," "Moroccan patterns and colors," "Mexican folk art elements"
    
    # Mood/Emotion
    # Ethereal: "Dreamlike and otherworldly," "Surreal and mystical," "Peaceful and tranquil"
    # Energetic: "Vibrant and chaotic," "Dynamic and full of life," "Upbeat with intense movement"
    # Dark/Mysterious: "Moody and suspenseful," "Ominous and foreboding," "Dark with a sense of mystery"
    # Nostalgic: "Warm and reminiscent," "Sentimental and comforting," "Evocative of a bygone era"
    # Majestic: "Grand and awe-inspiring," "Epic and powerful," "Bold with a regal presence"
    
    # Additional Objects
    # Animals: "Majestic eagle soaring above," "White wolf howling at the moon," "Colorful parrots in the trees"
    # Vehicles: "Classic car parked on a lonely road," "Spaceship landing on a distant planet," "Horse-drawn carriage on cobblestone street"
    # People or Characters: "Mystical figure cloaked in shadow," "Knight in armor on horseback," "Futuristic astronaut exploring"
    # Plants and Trees: "Cherry blossoms in full bloom," "Vines crawling over old ruins," "Ancient oak tree with twisted branches"
    # Structures or Monuments: "Ancient stone archway," "Floating lighthouse above the clouds," "Towering skyscraper with holograms"
    
    # Assemble the prompt
    assembled_prompt = f"{scene_description}, {style_elements}, {mood}, {additional_objects}"
    st.write("**Assembled Prompt**:", assembled_prompt)
    
    # Load predefined templates
    templates = {
        "Minimalist": "A simple and clean scene with soft colors and open space",
        "Vintage":    "Retro color scheme with faded tones and nostalgic elements",
        "Futuristic": "Neon-lit futuristic cityscape with flying cars and high-tech buildings"
    }
    
    # Style Templates Section
    st.subheader("Style Templates")
    style_template = st.selectbox("Choose a style template", ["Minimalist", "Vintage", "Futuristic"])

    # Apply selected template to the prompt
    if style_template:
        selected_template = templates.get(style_template)
        if selected_template:
            assembled_prompt += f", {selected_template}"
            st.write("**Template Applied:**", selected_template)
            
    #st.write("**Assembled Prompt**:", assembled_prompt)

    # Prompt enhancement suggestions
    if st.button("Get Suggestions"):
        try:
            response = client.chat.completions.create(
                 messages=[
                    {
                        "role": "user", 
                        "content": f"You are an expert in Text to Image generation models, \
                                    You will given a few key words related to marketing campaign \
                                    your task will to be generate an apt suggestion sentence using \
                                    the given keywords here {assembled_prompt}. "
                    },
                ],
                model     = "gpt-4o-mini",
                max_tokens= 50
            )
            st.session_state.suggestions = response.choices[0].message.content.strip()
            st.write("Suggestions:", st.session_state.suggestions)
        except Exception as e:
            st.error(f"Error generating suggestions: {e}")
            
    # Select image size
    size = st.selectbox("Choose image size", options=["1024x1024", "1792x1024", "1024x1792"])

    if st.session_state.suggestions:
        
        st.write("Suggestion generated : ", st.session_state.suggestions)
    
    # Generate image on button click
    if st.button("Generate Image"):
        
        if st.session_state.suggestions:
            with st.spinner("Generating image..."):
                
                image = generate_image(st.session_state.suggestions, client, size)
                
                if image:
                    st.image(image, caption="Generated Image", use_column_width=True)
        else:
            st.warning("Please get suggestions first to generate an image.")

    # Provide download functionality if image is generated
    if image:
        # Convert the image to BytesIO format
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        
        img_byte_arr = img_byte_arr.getvalue()
        
        # Enable image download
        st.download_button(
            label     = "Download Image",
            data      = img_byte_arr,
            file_name = "generated_image.png",
            mime      = "image/png"
        )

# Run the app
if __name__ == "__main__":
    main()
