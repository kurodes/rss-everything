import os
import sys
import time
import html
import json
from datetime import datetime
from typing import List, Tuple, Dict
from slack_sdk import WebClient

from rss_feed import RssFeed
from slack_client import SlackClient

TEST_LOCAL = False

if not TEST_LOCAL:
    BASE_PATH = '/home'
else:
    BASE_PATH = '/Users/kuro/Desktop/coding/rss-everything/n8n_docker'

RSS_FILE = f'{BASE_PATH}/files/slack_distsys_reading_group.rss'
TS_FILE = f'{BASE_PATH}/files/slack_distsys_reading_group.timestamp'
CACHE_FILE = f'{BASE_PATH}/files/slack_user.global.cache'

SLACK_API_TOKEN = open(f'{BASE_PATH}/scripts/slack_api_user_token').read().strip()

def generate_rss(conversations: List[Dict]):
    feed = RssFeed(
        title="Slack - DistSys Reading Group",
        link="https://distsysreadinggroup.slack.com",
        description="DistSys Reading Group",
        feed_link="https://n8n.lvwh.top/webhook/slack_distsys_reading_group.rss",
        lastBuildDate=RssFeed.now_rfc822(),
        image_url="https://a.slack-edge.com/80588/marketing/img/meta/favicon-32.png"
    )

    for conversation in conversations:
        # generate html for item description
        # message
        description_html = '<div style="margin-left: 0;"><p><b>{}</b></p><p>{}</p></div>'.format(
            conversation["messages"][0]["user"], html.escape(conversation["messages"][0]["text"]).replace('\n', '<br>'))
        description_html += '<hr>'
        # replies
        description_html += '<div style="padding-left: 20px;">'
        for reply in conversation["messages"][1:]:
            description_html += '<p><b>{}</b></p><p>{}</p>'.format(
                reply["user"], html.escape(reply["text"]).replace('\n', '<br>'))
            description_html += '<hr>'
        description_html += '</div>'


        feed.add_item(
            title=conversation["messages"][0]["text"],
            link=conversation["link"],
            guid=conversation["timestamp"],
            description=description_html,
            pubdate=RssFeed.datetime_to_rfc822(datetime.fromtimestamp(float(conversation["timestamp"])))
        )

    # print(feed.wriTEST_LOCALring("utf-8"))
    with open(RSS_FILE, 'w') as fp:
        feed.write(fp)

# load the last timestamp from filesystem
unix_timestamp = datetime(year=2023, month=10, day=8, hour=0, minute=0, second=0).timestamp()
if os.path.exists(TS_FILE):
    with open(TS_FILE, 'r') as fp:
        unix_timestamp = (float)(fp.read().strip())

slack_client = SlackClient(SLACK_API_TOKEN, CACHE_FILE)
conversations, new_unix_timestamp = slack_client.get_channel_conversations("general", unix_timestamp)

generate_rss(conversations)

with open(TS_FILE, 'w') as fp:
    fp.write(str(new_unix_timestamp))
