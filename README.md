# 🚀 Social Media Post Generator Pro

Craft engaging, AI-powered social media posts for LinkedIn and beyond. This app leverages advanced LLMs to generate, edit, and manage high-quality posts with customizable options for tone, length, language, and more.

## Features

- **AI-Powered Post Generation:**
  - Select topic, length, language, and tone
  - Generate multiple post variants at once
- **Post Editing:**
  - Edit generated or saved posts directly in the app
  - Save edited versions to your post history
- **Engagement Prediction:**
  - Simulate engagement metrics for your posts
- **Post History Management:**
  - View, save, and delete posts from your sidebar history
  - Download or copy posts with one click
- **Dark Mode:**
  - Toggle dark mode for comfortable viewing

## Usage

1. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up API Keys**
   - Place your LLM API key in a `.env` file as required by `llm_helper.py`.

3. **Run the App**
   ```bash
   streamlit run app.py
   ```

4. **Generate and Manage Posts**
   - Use the sidebar to select settings and view post history
   - Generate, edit, save, download, or delete posts as needed

## File Structure

- `app.py` — Main Streamlit app (UI, post management, history)
- `post_generator.py` — LLM prompt construction and post generation
- `few_shot.py` — Few-shot example management and filtering
- `llm_helper.py` — LLM API integration
- `data/` — Processed and raw post data
- `saved_posts/` — All saved/generated posts
- `user_posts/` — (Reserved for user-specific posts)

## Customization
- Add new topics/tags in your data files for more variety
- Adjust tone, length, and language options in `app.py` as needed

## License
MIT License

---
*Built with Streamlit, Python, and LLMs for content creators and professionals.*
