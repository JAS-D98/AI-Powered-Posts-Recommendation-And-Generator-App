import streamlit as st
from few_shot import FewShotPosts
from post_generator import generate_post
import time
from datetime import datetime
import json
import os

# Constants
LENGTH_OPTIONS = ["Short", "Medium", "Long"]
LANGUAGE_OPTIONS = ["English", "Hinglish", "Hindi", "Marathi"]
TONE_OPTIONS = ["Professional", "Casual", "Inspirational", "Humorous", "Opinionated"]
SAVE_FOLDER = "saved_posts"

# Create save directory if it doesn't exist
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

def save_post(post_data):
    """Save generated post to a JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SAVE_FOLDER}/post_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(post_data, f, ensure_ascii=False, indent=4)
    
    return filename


def delete_post(filename):
    """Delete a saved post file by filename"""
    file_path = os.path.join(SAVE_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

def load_saved_posts():
    """Load all saved posts from the save directory"""
    posts = []
    for filename in os.listdir(SAVE_FOLDER):
        if filename.endswith(".json"):
            with open(os.path.join(SAVE_FOLDER, filename), "r", encoding="utf-8") as f:
                try:
                    post_data = json.load(f)
                    post_data["filename"] = filename
                    posts.append(post_data)
                except json.JSONDecodeError:
                    continue
    return sorted(posts, key=lambda x: x.get("timestamp", ""), reverse=True)

def main():
    # Initialize session state
    if "generated_posts" not in st.session_state:
        st.session_state.generated_posts = []
    if "selected_post" not in st.session_state:
        st.session_state.selected_post = None
    
    # App title and description
    st.title("🚀 Social Media Post Generator Pro")
    st.markdown("""
    Craft engaging social media posts with AI. Select your preferences below and generate high-quality content in seconds.
    """)
    
    # Sidebar for settings and history
    with st.sidebar:
        st.header("Settings")
        dark_mode = st.toggle("Dark Mode", value=False)

        st.header("Post History")
        saved_posts = load_saved_posts()
        if saved_posts:
            for post in saved_posts:
                col_hist, col_del = st.columns([4,1])
                with col_hist:
                    if st.button(f"{post.get('tag', 'Untitled')} - {post.get('timestamp', 'No date')}", key=f"hist_{post['filename']}"):
                        st.session_state.selected_post = post
                with col_del:
                    if st.button("🗑️", key=f"del_{post['filename']}"):
                        delete_post(post['filename'])
                        st.rerun()
                        return
        else:
            st.info("No saved posts yet")
    
    # Main content area
    tab1, tab2 = st.tabs(["Generate Post", "Edit Post"])
    
    with tab1:
        # Settings columns
        col1, col2, col3 = st.columns(3)
        fs = FewShotPosts()
        
        with col1:
            selected_tag = st.selectbox(
                "Topic", 
                options=fs.get_unique_tags(), 
                key="title",
                help="Select the main topic for your post"
            )
        
        with col2:
            selected_length = st.selectbox(
                "Length", 
                options=LENGTH_OPTIONS, 
                key="length",
                help="Choose how long you want the post to be"
            )
        
        with col3:
            selected_language = st.selectbox(
                "Language", 
                options=LANGUAGE_OPTIONS, 
                key="language",
                help="Select the language for your post"
            )
        
        # Additional options
        with st.expander("Advanced Options"):
            col4, col5 = st.columns(2)
            with col4:
                selected_tone = st.selectbox(
                    "Tone", 
                    options=TONE_OPTIONS,
                    help="Select the tone for your post"
                )
            with col5:
                num_variants = st.slider(
                    "Number of variants", 
                    min_value=1, 
                    max_value=5, 
                    value=1,
                    help="Generate multiple versions to choose from"
                )
        
        # Generate button with loading state
        if st.button("✨ Generate Posts", type="primary"):
            with st.spinner(f"Generating {num_variants} post variants..."):
                start_time = time.time()
                
                generated_posts = []
                for i in range(num_variants):
                    post = generate_post(
                        selected_length, 
                        selected_language, 
                        selected_tag,
                        selected_tone
                    )
                    generated_posts.append(post)
                
                st.session_state.generated_posts = generated_posts
                generation_time = time.time() - start_time
                
                # Save the first post by default
                post_data = {
                    "text": generated_posts[0],
                    "tag": selected_tag,
                    "length": selected_length,
                    "language": selected_language,
                    "tone": selected_tone,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "generation_time": f"{generation_time:.2f}s"
                }
                save_post(post_data)
                
                st.success(f"Generated {num_variants} posts in {generation_time:.2f} seconds!")
        
        # Display generated posts
        if st.session_state.generated_posts:
            st.subheader("Generated Posts")
            for i, post in enumerate(st.session_state.generated_posts, 1):
                with st.expander(f"Variant {i}", expanded=i==1):
                    st.markdown(post)
                    
                    # Post actions
                    col_copy, col_download, col_save = st.columns(3)
                    with col_copy:
                        if st.button("📋 Copy", key=f"copy_{i}"):
                            st.toast("Post copied to clipboard!")
                    with col_download:
                        st.download_button(
                            "💾 Download", 
                            data=post,
                            file_name=f"linkedin_post_{selected_tag}_{i}.txt",
                            mime="text/plain"
                        )
                    with col_save:
                        if st.button("❤️ Save", key=f"save_{i}"):
                            post_data = {
                                "text": post,
                                "tag": selected_tag,
                                "length": selected_length,
                                "language": selected_language,
                                "tone": selected_tone,
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            save_post(post_data)
                            st.toast("Post saved to history!")
    
    with tab2:
        if st.session_state.selected_post or st.session_state.generated_posts:
            post_to_edit = st.session_state.selected_post or {
                "text": st.session_state.generated_posts[0],
                "tag": selected_tag,
                "length": selected_length,
                "language": selected_language,
                "tone": selected_tone
            }
            
            edited_post = st.text_area(
                "Edit your post",
                value=post_to_edit["text"],
                height=300
            )
            
            col_save, col_analyze = st.columns(2)
            with col_save:
                if st.button("Save Edits"):
                    post_data = {
                        "text": edited_post,
                        "tag": post_to_edit.get("tag", ""),
                        "length": post_to_edit.get("length", ""),
                        "language": post_to_edit.get("language", ""),
                        "tone": post_to_edit.get("tone", ""),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "edited": True
                    }
                    save_post(post_data)
                    st.success("Edited post saved!")
            
            with col_analyze:
                if st.button("Analyze Engagement"):
                    with st.spinner("Predicting engagement..."):
                        # Simulate engagement prediction
                        time.sleep(1)
                        engagement_score = min(int(len(edited_post) * 0.5 + 100), 1000)
                        st.metric("Predicted Engagement", f"{engagement_score} reactions")
        else:
            st.info("Generate or select a post from history to edit")

if __name__ == "__main__":
    main()