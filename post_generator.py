from llm_helper import llm
from few_shot import FewShotPosts
import re
from langchain_core.prompts import PromptTemplate

few_shot = FewShotPosts()

def get_length_str(length):
    """Convert length category to word count range"""
    length_mapping = {
        "Short": "1 to 5 lines (50-100 words)",
        "Medium": "6 to 10 lines (100-200 words)",
        "Long": "11 to 15 lines (200-300 words)"
    }
    return length_mapping.get(length, "6 to 10 lines (100-200 words)")

def generate_post(length, language, tag, tone="Professional"):
    """Generate a LinkedIn post with given parameters"""
    prompt = build_prompt(length, language, tag, tone)
    
    try:
        response = llm.invoke(prompt)
        return extract_post_content(response.content)
    except Exception as e:
        print(f"Error generating post: {e}")
        return "Sorry, there was an error generating your post. Please try again."

def extract_post_content(response_content):
    """Extract the post content from the LLM response"""
    # Clean the response
    response_content = re.sub(r'[\ud800-\udfff]', '', response_content)  # Remove surrogate pairs
    
    # If <think>...</think> is present, extract only the post content
    if '</think>' in response_content:
        return response_content.split('</think>')[-1].strip()
    
    # Remove any remaining XML/HTML tags
    response_content = re.sub(r'<[^>]+>', '', response_content)
    
    return response_content.strip()

def build_prompt(length, language, tag, tone):
    """Construct the prompt for the LLM"""
    length_str = get_length_str(length)
    
    prompt_template = """
    Generate a high-quality LinkedIn post with the following specifications:
    
    1) Topic: {tag}
    2) Length: {length_str}
    3) Language: {language}
    4) Tone: {tone}
    
    Additional Guidelines:
    - If Language is Hinglish, use a natural mix of Hindi and English words
    - Include appropriate line breaks for readability
    - Use emojis sparingly (2-3 per post)
    - Make the post engaging and valuable for professionals
    - Avoid overly promotional language
    
    {examples_section}
    """
    
    # Get relevant examples
    examples = few_shot.get_filtered_posts(length, language, tag)
    examples_section = ""
    
    if examples:
        examples_section = "Here are some example posts for reference:\n\n"
        for i, post in enumerate(examples, 1):
            examples_section += f"Example {i}:\n{post['text']}\n\n"
    
    prompt = PromptTemplate.from_template(prompt_template).format(
        tag=tag,
        length_str=length_str,
        language=language,
        tone=tone,
        examples_section=examples_section
    )
    
    return prompt