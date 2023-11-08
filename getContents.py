import json
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.tokenize import RegexpTokenizer
from promptflow import tool
from bs4 import BeautifulSoup

email_bodies = []

with open("simpleData.json", "r") as input_file:
    data = json.load(input_file)

    email_bodies = [
        item.get("body", "") for item in data if isinstance(item, dict)
    ]
@tool
def generate_email_summary():
    summaries = []
    for i, email_body in enumerate(email_bodies):
        soup = BeautifulSoup(email_body, "html.parser")
        plain_text = soup.get_text()

        sentences = sent_tokenize(plain_text)

        tokenizer = RegexpTokenizer(r"\w+")
        words = [
            word.lower() for sentence in sentences for word in tokenizer.tokenize(sentence)
        ]

        stop_words = set(stopwords.words("english"))
        filtered_words = [word for word in words if word not in stop_words]

        word_freq = FreqDist(filtered_words)

        sentence_scores = {}
        for sentence in sentences:
            for word in tokenizer.tokenize(sentence):
                if word.lower() in word_freq:
                    if sentence not in sentence_scores:
                        sentence_scores[sentence] = word_freq[word.lower()]
                    else:
                        sentence_scores[sentence] += word_freq[word.lower()]

        summary_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:5]

        summary = TreebankWordDetokenizer().detokenize(summary_sentences)
        summaries.append(summary)
        print(f"Summary for Email {i + 1}:")
        print(summary)

    return summaries

def chat_bot(input_text):
    if "how is my emails today" in input_text.lower():
        summaries = generate_email_summary()
        return summaries
    else:
        return "I'm sorry, I cannot provide information"

input_text = "How is my emails today?"
response = chat_bot(input_text)
