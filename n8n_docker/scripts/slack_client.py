from time import sleep
from slack_sdk import WebClient 
from typing import Dict, List, Tuple

class SlackClient:

    def __init__(self, slack_api_token) -> None:
        self.slack_client = WebClient(token=slack_api_token)

    def get_user_name(self, user_id) -> str:
        response = self.slack_client.users_info(user=user_id)
        if response["ok"]:
            return response["user"]["real_name"]
        else:
            return "Failed to get user name"

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
                sleep(3)

        return channels

    def get_thread_messages(self, channel_id, ts):
        messages = []
        cursor = None

        while True:
            # https://api.slack.com/methods/conversations.replies
            thread_replies = self.slack_client.conversations_replies(channel=channel_id, ts=ts, cursor=cursor)

            for iter in thread_replies["messages"]:
                if (iter["type"] == "message"):
                    messages.append({"user": iter["user"], "text": iter["text"]})

            if bool(thread_replies["has_more"]):
                cursor = thread_replies["response_metadata"]["next_cursor"]
            else:
                cursor = None

            if cursor is None:
                break
            else:
                sleep(1.2)
        return messages

    def get_conversations(self, channel_id, oldest: float) -> Tuple[List[Dict], float]:
        """
        Args:
            channel_ids: channel id
            oldest: return conversations after this Unix timestamp (UTC)
        """
        new_oldest = 0.1
        conversations = []
        cursor = None
        while True:
            # the maximum number of items to return is 100
            # https://api.slack.com/methods/conversations.history
            channel_history = self.slack_client.conversations_history(channel=channel_id, cursor=cursor, oldest=oldest)

            for iter in channel_history["messages"]:
                if (iter["type"] == "message"):
                    conversation = {
                        "link": "https://distsysreadinggroup.slack.com/archives/{}/{}".format(channel_id, "p" + iter["ts"].replace(".", "")),
                        "timestamp": iter["ts"],
                        "messages": [{"user": iter["user"], "text": iter["text"]}]
                    }
                    # get all replies
                    if ("thread_ts" in iter):
                        conversation["messages"] = self.get_thread_messages(channel_id, iter["ts"])
                    # get user name of each text
                    for msg_iter in conversation["messages"]:
                        msg_iter["user"] = self.get_user_name(msg_iter["user"])
                        sleep(1.2)
                    
                    conversations.append(conversation)
                    new_oldest = max(new_oldest, float(iter["ts"]))

            if bool(channel_history["has_more"]):
                cursor = channel_history["response_metadata"]["next_cursor"]
            else:
                cursor = None

            if cursor is None:
                break
            else:
                sleep(1.2)

        return conversations, new_oldest
    
    def get_channel_conversations(self, slack_channel: str, oldest: float) -> Tuple[List[Dict], float]:
        """
        Retrieves conversations from a specified Slack channel that are newer than a given timestamp.

        Args:
            slack_channel: name of the slack channel
            oldest: return conversations after this Unix timestamp (UTC)
        Returns:
            `[{"link": str, "timestamp": unix_timestamp, "messages": [{"message": str, "user": str}] }], unix_timestamp`
        """
        channels = self.get_public_channels()
        channel_id = channels[slack_channel]
        conversations, new_unix_timestamp = self.get_conversations(channel_id, oldest)
        return conversations, new_unix_timestamp
