import json
import os
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob

def process_json_with_sentiment_analysis():
    current_directory = os.getcwd()
    file_name = "data.json"
    full_path = os.path.join(current_directory, file_name)

    with open(full_path, 'r') as file:
        json_data = json.load(file)

    contents = [item.get('body', {}).get('content', '') for item in json_data.get('value', [])]
    subjects = [item.get('subject', '') for item in json_data.get('value', [])]

    def convert_html_to_text(html):
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text()

    plain_texts = [convert_html_to_text(content) if any(tag for tag in BeautifulSoup(content, 'html.parser').find_all()) else content for content in contents]

    analyses = []

    for index, text in enumerate(plain_texts):
        analysis = {
            "Subject": subjects[index],
            "content": text,
        }
        analyses.append(analysis)

    # Return a JSON-compatible string
    return json.dumps(analyses)

result = process_json_with_sentiment_analysis()
print(result)
