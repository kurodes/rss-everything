import os
import sys
import time
import html
from datetime import datetime
from typing import List, Tuple, Dict
from slack_sdk import WebClient

from rss_feed import RssFeed

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

slack_client = WebClient(token=SLACK_API_TOKEN)

def get_public_channels():
    """
    Returns:
        channels: dict of { name : id }
    """
    cursor = None
    channels = {}
    while True:
        # https://api.slack.com/methods/conversations.list
        response = slack_client.conversations_list(cursor=cursor)

        for channel in response["channels"]:
            channels[channel["name"]] = channel["id"]

        cursor = response["response_metadata"]["next_cursor"]
        if len(cursor) == 0:
            break
        else:
            print("Pagination found, getting next entries")
            time.sleep(3)

    return channels

def get_thread_messages(slack_channel, ts):
    messages = []
    cursor = None

    while True:
        # https://api.slack.com/methods/conversations.replies
        thread_replies = slack_client.conversations_replies(channel=slack_channel, ts=ts, cursor=cursor)

        for message in thread_replies["messages"]:
            if (message["type"] == "message"):
                messages.append(message["text"])

        if bool(thread_replies["has_more"]):
            cursor = thread_replies["response_metadata"]["next_cursor"]
        else:
            cursor = None

        if cursor is None:
            break
        else:
            print("Pagination found, getting next entries")
            time.sleep(1.2)
    return messages

def get_channel_messages(slack_channel, oldest: float) -> Tuple[Dict, float]:
    """
    Args:
        slack_channels: channel id
        curosr: iterator
        oldest: return messages after this Unix timestamp (UTC)
    """
    new_oldest = 0.1
    messages = []
    cursor = None
    while True:
        # the maximum number of items to return is 100
        channel_history = slack_client.conversations_history(channel=slack_channel, cursor=cursor, oldest=oldest)

        for message in channel_history["messages"]:
            if (message["type"] == "message"):
                thread = {
                    "message": message["text"],
                    # e.g., https://distsysreadinggroup.slack.com/archives/C0114EVKRND/p1696944822508999
                    "link": "https://distsysreadinggroup.slack.com/archives/{}/{}".format(slack_channel, "p" + message["ts"].replace(".", "")),
                    "timestamp": message["ts"],
                    "replies": []
                }
                # if reply exists
                if ("thread_ts" in message):
                    thread["replies"] = get_thread_messages(slack_channel, message["ts"])[1:]
                messages.append(thread)
                new_oldest = max(new_oldest, float(message["ts"]))

        if bool(channel_history["has_more"]):
            cursor = channel_history["response_metadata"]["next_cursor"]
        else:
            cursor = None

        if cursor is None:
            break
        else:
            time.sleep(1.2)

    return messages, new_oldest

def generate_rss(messages: List[List[str]]):
    """
    Args:
        messages: list of thread
    """
    feed = RssFeed(
        title="Slack - DistSys Reading Group",
        link="distsysreadinggroup.slack.com",
        description="DistSys Reading Group",
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
            title = thread["message"],
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

general_channel_id = get_public_channels()["general"]

messages, new_unix_timestamp = get_channel_messages(general_channel_id, unix_timestamp)

generate_rss(messages)

with open(timestamp_file, 'w') as fp:
    fp.write(str(new_unix_timestamp))