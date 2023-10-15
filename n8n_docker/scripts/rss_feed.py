from datetime import datetime

class RssFeed:
    """
    Rss 2.0 Spec: https://cyber.harvard.edu/rss/rss.html
    """
    def __init__(self, title, link, description, lastBuildDate: str = None, feed_link=None, image_url=None) -> None:
        """
        Args:
            lastBuildDate: rfc822 time string
            image_url:  URL of a GIF, JPEG or PNG image 
        """

        # metadata of the feed
        self.title = title
        self.link = link
        self.description = description
        self.lastBuildDate = lastBuildDate
        self.feed_link = feed_link
        self.image_url = image_url

        # posts of the feed
        self.items = []

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
            pubdate: rfc822 time string
            creator_dublin_core: name of the creator
        """
        self.items.append({
            "title": title,
            "link": link,
            "guid": guid,
            "description": description,
            "pubdate": pubdate,
            "creator_dublin_core": creator_dublin_core,
        })

    def to_string(self) -> str:
        meta_string = f"""
        <title>
            <![CDATA[{self.title}]]>
        </title>
        <link>{self.link}</link>
        <description>
            <![CDATA[{self.description}]]>
        </description>"""

        if self.lastBuildDate is not None:
            meta_string = f"""{meta_string}
        <lastBuildDate>{self.lastBuildDate}</lastBuildDate>"""
        
        if self.feed_link is not None:
            meta_string = f"""{meta_string}
        <atom:link href=\"{self.feed_link}\" rel=\"self\" type=\"application/rss+xml\"></atom:link>"""
        
        if self.image_url is not None:
            # In practice, the image <title> and <link> should have the same value as the channel's <title> and <link>
            meta_string = f"""{meta_string}
        <image>
            <url>{self.image_url}</url>
            <title>
                <![CDATA[{self.title}]]>
            </title>
            <link>{self.link}</link>
        </image>"""

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
            <pubDate>{item["pubdate"]}</pubDate>
"""
            if item["creator_dublin_core"] is not None:
                items_string = f"""{items_string}
            <dc:creator>
                <![CDATA[{item["creator_dublin_core"]}]]>
            </dc:creator>"""
            
            items_string = f"""{items_string}
        </item>
"""
        xml_string = f"""<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>{meta_string}{items_string}
    </channel>
</rss>
"""
        return xml_string

    def write(self, fp, encoding="utf-8"):
        fp.write(self.to_string().encode(encoding).decode())
