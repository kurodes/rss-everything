import json
import os
import feedparser
import feedgenerator
from datetime import datetime
from time import sleep
from typing import List

from openai import OpenAI

# OPENAI_API_KEY = "sk-xxxxx"
OPENAI_API_KEY = open("/home/scripts/openai_api_key").read().strip()
GPT3 = "gpt-3.5-turbo" 
GPT4 = "gpt-4o",

rss_file = '/home/files/arxiv.rss'
# rss_file = "/Users/kuro/Desktop/coding/rss-everything/n8n_docker/files/arxiv.rss"
history_file = '/home/files/history.json'

# +cs.NI
arxiv_urls = [
    "https://rss.arxiv.org/rss/cs.DB+cs.DC+cs.OS"
]
focus_terms = {
    "cs.DB": "Databases", 
    "cs.DC": "Distributed, Parallel, and Cluster Computing", 
    "cs.OS": "Operating Systems"
}

def getCompletion(messages, model=GPT3):
    client = OpenAI(
            api_key = OPENAI_API_KEY
    )
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages
        )
        response = completion.choices[0].message.content
    except Exception as e:
        response = str(e)
    return response


def main(urls: List[str]):
    input_feeds = []
    for url in urls:
        input_feeds.append(feedparser.parse(url))

    output_feed = feedgenerator.Rss201rev2Feed(
        title="CS updates on arXiv.org",
        link="'http://arxiv.org/'",
        description="'Computer Science updates on the arXiv.org e-print archive'",
        # lastBuildDate will be auto generated, equal to the latest item's pubdate
        lastBuildDate=None,
        image="https://arxiv.org/icons/sfx.gif"
    )

    if not os.path.exists(history_file):
        with open(history_file, 'w') as fp:
            json.dump({"links": []}, fp)
            fp.close()

    with open(history_file, 'r') as fp:
        history = json.load(fp)
        fp.close()

    for feed in input_feeds:
        for item in feed.entries:
            # check the first category
            if item.tags[0].term not in focus_terms.keys():
                continue
            # check duplication
            if item.link in history["links"]:
                continue

            history["links"].append(item.link)
            if len(history["links"]) > 1000:
                history["links"] = history["links"][-1000:]

            abstract = item.summary.split("Abstract: ")[1]
            terms = ""
            terms_list = [tag.term for tag in item.tags]
            for term in terms_list:
                if term in focus_terms.keys():
                    terms = terms + f"{term} ({focus_terms[term]})" + "<br>"
                else:
                    terms = terms + term + "<br>"

            # chatgpt
            messages = [{"role": "system", "content" : "You are a helpful assistant. You can help me by answering my questions. You can also ask me questions."}]
            # messages.append({"role": "user", "content": f"Translate this title of a computer science paper into Chinese: {item.title}"})
            # title_translation = getCompletion(messages, GPT4)
            messages.append({"role": "user", "content": f"Translate this abstract of a computer science paper into Chinese:\n\n{abstract}"})
            # messages.append({"role": "user", "content": f"As a new PhD candidate, I'm having difficulty understanding a computer science paper with the abstract provided below. Please help me by:\n1. Translating the abstract into Chinese.\n2. For each technical term used in the abstract, provide a detailed explanation in English, followed by its translation into Chinese. Organize your response in a list format, with each item containing the technical term, its explanation, and its Chinese translation.\n\n\"\"\"\n{abstract}\n\"\"\""})
            # abs_explanation = re.sub(r'\n', '<br>', getCompletion(messages))
            abs_translation = getCompletion(messages, GPT3)

            formated_description = f"<p>{item.author}</p><p>{terms}</p><p>{abstract}</p><p>{abs_translation}</p>"

            # add to feed
            output_feed.add_item(
                title=item.title,
                link=item.link,
                description=formated_description,
                author_name=item.author,
                # A string that uniquely identifies the item.
                unique_id=item.link,
            )

    # xml_string = output_feed.writeString("utf-8")
    # print(xml_string)

    with open(history_file, 'w') as fp:
        json.dump(history, fp)
        fp.close()

    with open(rss_file, 'w') as fp:
        output_feed.write(fp, 'utf-8')
        fp.close()

if __name__ == "__main__":
    main(arxiv_urls)
