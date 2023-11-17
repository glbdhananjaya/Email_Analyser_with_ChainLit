import json
import os
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
import re

def process_json_with_sentiment_analysis(batch_size=100):
    current_directory = os.getcwd()
    file_name = "data.json"
    full_path = os.path.join(current_directory, file_name)

    with open(full_path, 'r') as file:
        json_data = json.load(file)

    contents = [item.get('body', {}).get('content', '') for item in json_data.get('value', [])]
    subjects = [item.get('subject', '') for item in json_data.get('value', [])]

    def convert_html_to_text(html):
        soup = BeautifulSoup(html, 'html.parser')
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()

        for img in soup.find_all('img', 'svg'):
            img.decompose()

        text_with_emojis = soup.get_text()
        text_without_emojis = re.sub(r'[\U00010000-\U0010ffff]', '', text_with_emojis)
        
        return text_without_emojis.strip()

    plain_texts = [convert_html_to_text(content) if any(tag for tag in BeautifulSoup(content, 'html.parser').find_all()) else content for content in contents]

    analyses = []

    for i in range(0, len(plain_texts), batch_size):
        batch_texts = plain_texts[i:i + batch_size]
        batch_subjects = subjects[i:i + batch_size]

        for index, text in enumerate(batch_texts):
            analysis = {
                "Subject": batch_subjects[index],
                "content": text,
            }
            analyses.append(analysis)

    return json.dumps(analyses)

result = process_json_with_sentiment_analysis()
print(result)
