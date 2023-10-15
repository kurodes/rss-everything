from time import sleep
from slack_sdk import WebClient 
from typing import Dict, List, Tuple

class SlackClient:

    def __init__(self, slack_api_token) -> None:
        self.slack_client = WebClient(token=slack_api_token)

    def get_public_channels(self):
        """
        Returns:
            channels: dict of { name : id }
        """
        cursor = None
        channels = {}
        while True:
            # https://api.slack.com/methods/conversations.list
            response = self.slack_client.conversations_list(cursor=cursor)

            for channel in response["channels"]:
                channels[channel["name"]] = channel["id"]

            cursor = response["response_metadata"]["next_cursor"]
            if len(cursor) == 0:
                break
            else:
                print("Pagination found, getting next entries")
                sleep(3)

        return channels

    def get_thread_messages(self, channel_id, ts):
        messages = []
        cursor = None

        while True:
            # https://api.slack.com/methods/conversations.replies
            thread_replies = self.slack_client.conversations_replies(channel=channel_id, ts=ts, cursor=cursor)

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
                sleep(1.2)
        return messages

    def get_messages(self, channel_id, oldest: float) -> Tuple[List[Dict], float]:
        """
        Args:
            channel_ids: channel id
            oldest: return messages after this Unix timestamp (UTC)
        """
        new_oldest = 0.1
        messages = []
        cursor = None
        while True:
            # the maximum number of items to return is 100
            channel_history = self.slack_client.conversations_history(channel=channel_id, cursor=cursor, oldest=oldest)

            for message in channel_history["messages"]:
                if (message["type"] == "message"):
                    thread = {
                        "message": message["text"],
                        # e.g., https://distsysreadinggroup.slack.com/archives/C0114EVKRND/p1696944822508999
                        "link": "https://distsysreadinggroup.slack.com/archives/{}/{}".format(channel_id, "p" + message["ts"].replace(".", "")),
                        "timestamp": message["ts"],
                        "replies": []
                    }
                    # if reply exists
                    if ("thread_ts" in message):
                        thread["replies"] = self.get_thread_messages(channel_id, message["ts"])[1:]
                    messages.append(thread)
                    new_oldest = max(new_oldest, float(message["ts"]))

            if bool(channel_history["has_more"]):
                cursor = channel_history["response_metadata"]["next_cursor"]
            else:
                cursor = None

            if cursor is None:
                break
            else:
                sleep(1.2)

        return messages, new_oldest
    
    def get_channel_messages(self, slack_channel: str, oldest: float) -> Tuple[List[Dict], float]:
        """
        Retrieves messages from a specified Slack channel that are newer than a given timestamp.

        Args:
            slack_channel: name of the slack channel
            oldest: return messages after this Unix timestamp (UTC)
        Returns:
            `[[{"message": str, "link": str, "timestamp": unix_timestamp, "replies": [str] }], unix_timestamp]`
        """
        channels = self.get_public_channels()
        channel_id = channels[slack_channel]
        messages, new_unix_timestamp = self.get_messages(channel_id, oldest)
        return messages, new_unix_timestamp
