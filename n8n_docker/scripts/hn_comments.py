#! /usr/bin/env python3
# %%
import sys
import json
import requests
from bs4 import BeautifulSoup

item = {
    "id": None,
    "link": None,
    "title": None,
    "description" : None,
    "date_published": None,
    "last_updated": None
}

# parse event json from stdin
input_json = json.load(sys.stdin)

item = {
    "id": input_json["id"],
    "link": input_json["url"],
    "title": input_json["title"],
    "description" : input_json["description"],
    "date_published": input_json["date_published"],
    "last_updated": input_json["last_updated"]
}

# send GET request 
response_html = requests.get(item["id"]).text
# use BeautifulSoup to parse html
soup = BeautifulSoup(response_html, "html.parser")
element = soup.find(class_='comment-tree')
comments_html = element.prettify()
# print(comments_html)

item["description"] = \
    input_json["description"] + \
    "<![CDATA[" + \
    '<center><hr size="5" width="80%"></center>' + \
    comments_html + \
    "]]>"

print(json.dumps(item))
