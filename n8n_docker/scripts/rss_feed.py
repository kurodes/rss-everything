from datetime import datetime

class RssFeed:
    def __init__(self, title, link, description, feed_link, lastBuildDate: str = None, image_url=None) -> None:
        """
        Args:
            title: not support html
            link: https://
            description: not support html
            feed_link: https://
            lastBuildDate: rfc822 time string
            image_url: https:// to gif, jpeg or png

        Rss 2.0 Spec: https://cyber.harvard.edu/rss/rss.html
        RSS Advisory Board's Best Practices Profile: https://www.rssboard.org/rss-profile
        """

        self.flag_dublin_ns = False

        # metadata of the feed
        self.title = self.remove_special_chars(title)
        self.link = link
        self.feed_link = feed_link
        self.description = self.remove_special_chars(description)
        self.lastBuildDate = lastBuildDate
        self.image_url = image_url

        # posts of the feed
        self.items = []

    def remove_special_chars(self, string):
        """
        Better not contain HTML or HTML escapes in elements other than items' <description>.

        https://www.rssboard.org/rss-validator/docs/warning/CharacterData.html
        https://www.rssboard.org/rss-validator/docs/warning/ContainsHTML.html
        """
        special_chars = ["&", "<", ">"]
        for char in special_chars:
            string = string.replace(char, ' ')
        return string

    def now_rfc822() -> str:
        """
        Returns:
            str: Current time in RFC 822 format, here we use UTC.
        """
        now = datetime.utcnow()
        rfc822 = now.strftime("%a, %d %b %Y %H:%M:%S +0000")
        return rfc822

    def datetime_to_rfc822(dt: datetime) -> str:
        rfc822 = dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
        return rfc822

    def add_item(self, title, link, guid, description, pubdate : str = None, creator_dublin_core=None):
        """
        Args:
            title: not support html
            link: https://
            guid:
            description: support html, `html.escape(html_str)`
            pubdate: rfc822 time string
            creator_dublin_core: name of the creator
        """
        self.items.append({
            "title": self.remove_special_chars(title),
            "link": link,
            "guid": guid,
            "description": description,
            "pubdate": pubdate,
            "creator_dublin_core": creator_dublin_core,
        })

    def to_string(self) -> str:
        # generate channel string
        channel_string = f"""
        <title>
            <![CDATA[{self.title}]]>
        </title>
        <link>{self.link}</link>
        <description>
            <![CDATA[{self.description}]]>
        </description>"""

        if self.lastBuildDate is not None:
            channel_string = f"""{channel_string}
        <lastBuildDate>{self.lastBuildDate}</lastBuildDate>"""

        if self.feed_link is not None:
            channel_string = f"""{channel_string}
        <atom:link href=\"{self.feed_link}\" rel=\"self\" type=\"application/rss+xml\"></atom:link>"""

        if self.image_url is not None:
            # In practice, the image <title> and <link> should have the same value as the channel's <title> and <link>
            channel_string = f"""{channel_string}
        <image>
            <url>{self.image_url}</url>
            <title>
                <![CDATA[{self.title}]]>
            </title>
            <link>{self.link}</link>
        </image>"""

        # generate item string
        items_string = ""
        for item in self.items:
            items_string = f"""{items_string}
        <item>
            <title>
                <![CDATA[{item["title"]}]]>
            </title>
            <link>{item["link"]}</link>
            <guid isPermaLink="false">{item["guid"]}</guid>
            <description>
                <![CDATA[{item["description"]}]]>
            </description>"""

            if item["pubdate"] is not None:
                items_string = f"""{items_string}
            <pubDate>{item["pubdate"]}</pubDate>"""

            if item["creator_dublin_core"] is not None:
                items_string = f"""{items_string}
            <dc:creator>
                <![CDATA[{item["creator_dublin_core"]}]]>
            </dc:creator>"""
                self.flag_dublin_ns = True

            items_string = f"""{items_string}
        </item>"""

        # generate rss string
        dublin_ns_string = " xmlns:dc=\"http://purl.org/dc/elements/1.1/\" " if self.flag_dublin_ns else ""
        xml_string = f"""<rss version=\"2.0\" xmlns:atom=\"http://www.w3.org/2005/Atom\" {dublin_ns_string}>
    <channel>{channel_string}{items_string}
    </channel>
</rss>
"""
        return xml_string

    def write(self, fp, encoding="utf-8"):
        fp.write(self.to_string().encode(encoding).decode())
