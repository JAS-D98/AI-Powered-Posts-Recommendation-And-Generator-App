import json
import pandas as pd
import re
from pathlib import Path

class FewShotPosts:
    def __init__(self, file_path='./data/processed_posts.json'):
        self.df = None
        self.unique_tags = None
        self.tag_categories = None
        self.load_posts(file_path)
    
    def load_posts(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                posts = json.load(file)
                df = pd.json_normalize(posts)
                
                # Clean and standardize data
                df["text"] = df["text"].apply(self.clean_text)
                df["length"] = df["line_count"].apply(self.categorize_length)
                
                # Extract and unify tags
                all_tags = df["tags"].explode().dropna()
                self.unique_tags = sorted(set(all_tags))
                self.tag_categories = self.categorize_tags(self.unique_tags)
                
                self.df = df
        except FileNotFoundError:
            raise Exception(f"Posts data file not found at {file_path}")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON format in {file_path}")
    
    def clean_text(self, text):
        """Clean text by removing special characters and extra whitespace"""
        if not isinstance(text, str):
            return ""
        text = re.sub(r'[\ud800-\udfff]', '', text)  # Remove surrogate pairs
        text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace
        return text
    
    def categorize_length(self, line_count):
        """Categorize post length"""
        try:
            line_count = int(line_count)
            if line_count < 5:
                return "Short"
            elif 5 <= line_count <= 10:
                return "Medium"
            else:
                return "Long"
        except (ValueError, TypeError):
            return "Medium"
    
    def categorize_tags(self, tags):
        """Group tags into categories for better organization"""
        categories = {
            "Career": ["Job Search", "Career Advice", "Interview Tips"],
            "Mental Health": ["Mental Health", "Wellbeing", "Work-Life Balance"],
            "Productivity": ["Productivity", "Time Management"],
            "Motivation": ["Motivation", "Inspiration"],
            "Scams": ["Scams", "Fraud Alerts"],
            "Other": []
        }
        
        categorized = {}
        for tag in tags:
            found = False
            for category, keywords in categories.items():
                if any(keyword.lower() in tag.lower() for keyword in keywords):
                    if category not in categorized:
                        categorized[category] = []
                    categorized[category].append(tag)
                    found = True
                    break
            if not found:
                if "Other" not in categorized:
                    categorized["Other"] = []
                categorized["Other"].append(tag)
        
        return categorized
    
    def get_unique_tags(self):
        """Return sorted unique tags"""
        return self.unique_tags
    
    def get_tag_categories(self):
        """Return tags organized by categories"""
        return self.tag_categories
    
    def get_filtered_posts(self, length, language, tag, limit=3):
        """Get filtered posts with error handling"""
        try:
            df_filtered = self.df[
                (self.df["length"] == length) &
                (self.df["language"] == language) &
                (self.df["tags"].apply(lambda x: tag in x if isinstance(x, list) else False))
            ]
            return df_filtered.head(limit).to_dict(orient='records')
        except Exception as e:
            print(f"Error filtering posts: {e}")
            return []