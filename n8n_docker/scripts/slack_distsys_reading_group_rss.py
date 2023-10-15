import os
import sys
import time
import html
from datetime import datetime
from typing import List, Tuple, Dict
from slack_sdk import WebClient

from rss_feed import RssFeed
from slack_client import SlackClient

TEST_LOCAL = False
if len(sys.argv) > 1 and sys.argv[1] == "test":
    TEST_LOCAL = True

if not TEST_LOCAL:
    rss_file = '/home/files/slack_distsys_reading_group.rss'
    timestamp_file = '/home/files/slack_distsys_reading_group.timestamp'
else:
    rss_file = '/Users/kuro/Desktop/coding/rss-everything/n8n_docker/files/slack_distsys_reading_group.rss'
    timestamp_file = '/Users/kuro/Desktop/coding/rss-everything/n8n_docker/files/slack_distsys_reading_group.timestamp'

if not TEST_LOCAL:
    SLACK_API_TOKEN = open("/home/scripts/slack_api_user_token").read().strip()
else:
    SLACK_API_TOKEN = open("/Users/kuro/Desktop/coding/rss-everything/n8n_docker/scripts/slack_api_user_token").read().strip()

def generate_rss(messages: List[List[str]]):
    """
    Args:
        messages: list of thread
    """
    feed = RssFeed(
        title="Slack - DistSys Reading Group",
        link="https://distsysreadinggroup.slack.com",
        description="DistSys Reading Group",
        feed_link="https://n8n.lvwh.top/webhook/slack_distsys_reading_group.rss",
        lastBuildDate=RssFeed.now_rfc822(),
        image_url="https://a.slack-edge.com/80588/marketing/img/meta/favicon-32.png"
    )

    for thread in messages:
        # escape special char
        description_html = '<p style="margin-left: 0;"><b>{}</b></p>'.format(html.escape(thread["message"]))
        description_html += '<ul style="margin-left: 20px;">'
        for reply in thread["replies"]:
            description_html += '<li>{}</li>'.format(html.escape(reply))
        description_html += '</ul>'

        feed.add_item(
            title=thread["message"],
            # title=html.escape(thread["message"]),
            # title=RssFeed.excape_to_hexadecimal_references(thread["message"]),
            link=thread["link"],
            guid=thread["timestamp"],
            description=description_html,
            pubdate=RssFeed.datetime_to_rfc822(datetime.fromtimestamp(float(thread["timestamp"])))
        )

    # print(feed.wriTEST_LOCALring("utf-8"))
    with open(rss_file, 'w') as fp:
        feed.write(fp)

# load/store last timestamp in filesystem
unix_timestamp = datetime(year=2023, month=10, day=8, hour=0, minute=0, second=0).timestamp()
if os.path.exists(timestamp_file):
    with open(timestamp_file, 'r') as fp:
        unix_timestamp = (float)(fp.read().strip())

slack_client = SlackClient(SLACK_API_TOKEN)
messages, new_unix_timestamp = slack_client.get_channel_messages("general", unix_timestamp)

generate_rss(messages)

with open(timestamp_file, 'w') as fp:
    fp.write(str(new_unix_timestamp))
