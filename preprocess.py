import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from llm_helper import llm
import re

def process_post(raw_file_path, processed_file_path="./data/processed_posts.json"):
    enriched_posts=[]
    with open(raw_file_path, "r", encoding="utf-8") as file:
        posts = json.load(file)
        for post in posts:
            metadata=extract_metadata(post['text'])
            post_with_metadata= post | metadata
            enriched_posts.append(post_with_metadata)
    
    unified_tags=get_unified_tags(enriched_posts)
    for post in enriched_posts:
        current_tags=post['tags'] 
        new_tags={unified_tags[tag] for tag in current_tags if tag in unified_tags}
        post['tags']=list(new_tags)

    # clean enriched posts to remove any surrogate pairs
    for post in enriched_posts:
        if 'text' in post:
            post['text'] = clean_surrogates(post['text'])

    with open(processed_file_path, "w", encoding="utf-8") as file:
        json.dump(enriched_posts, file, ensure_ascii=False, indent=4)

def extract_json_from_response(response_text):
        # Find the first {...} JSON object in the string
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            return match.group(0)
        else:
            return None
     
def get_unified_tags(posts_with_metadata):
    unique_tags=set()
    for post in posts_with_metadata:
        unique_tags.update(post['tags'])
    unique_tags_list=', '.join(unique_tags)

    template = '''I will give you a list of tags. You need to unify tags with the following requirements,
    1. Tags are unified and merged to create a shorter list. 
       Example 1: "Jobseekers", "Job Hunting" can be all merged into a single tag "Job Search". 
       Example 2: "Motivation", "Inspiration", "Drive" can be mapped to "Motivation"
       Example 3: "Personal Growth", "Personal Development", "Self Improvement" can be mapped to "Self Improvement"
       Example 4: "Scam Alert", "Job Scam" etc. can be mapped to "Scams"
    2. Each tag should be follow title case convention. example: "Motivation", "Job Search"
    3. Output should be a JSON object, No preamble
    3. Output should have mapping of original tag and the unified tag. 
       For example: {{"Jobseekers": "Job Search",  "Job Hunting": "Job Search", "Motivation": "Motivation}}
    
    Here is the list of tags: 
    {tags}
    '''

    pt= PromptTemplate.from_template(template)
    chain= pt | llm
    # Clean unique tags to remove any surrogate pairs
    unique_tags_list = clean_surrogates(unique_tags_list)
    # Invoke the chain with the unique tags
    response=chain.invoke(input={'tags': unique_tags_list})

    try:
        json_parser = JsonOutputParser()
        response_text = response.content
        json_str = extract_json_from_response(response_text)
        if json_str:
            output = json_parser.parse(json_str)
            return output
        else:
            print("No JSON found in LLM response.")
            return {}
    except OutputParserException as e:
        print(f"Error parsing output: {e}")
        return {}

def clean_surrogates(text):
    # Remove surrogate pairs (invalid in UTF-8)
    return re.sub(r'[\ud800-\udfff]', '', text)

def extract_metadata(post):
    template = '''
        You are given a LinkedIn post. You need to extract number of lines, language of the post and tags.
        1. Return a valid JSON. No preamble. 
        2. JSON object should have exactly three keys: line_count, language and tags. 
        3. tags is an array of text tags. Extract maximum two tags.
        4. Language should be English or Hinglish (Hinglish means hindi + english)
        
        Here is the actual post on which you need to perform this task:  
        {post}
    '''
    
    pt= PromptTemplate.from_template(template)
    chain= pt | llm

    # Clean post text to remove any surrogate pairs
    post = clean_surrogates(post)
    # Invoke the chain with the post
    response=chain.invoke(input={'post': post})

    json_parser=JsonOutputParser()
    try:
        output=json_parser.parse(response.content)
        return output
    except OutputParserException as e:
        print(f"Error parsing output: {e}")
        return {}

if __name__=="__main__":
    process_post("./data/raw_post.json", "./data/processed_posts.json")
