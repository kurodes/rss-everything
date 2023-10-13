import feedparser
import feedgenerator
from datetime import datetime

rss_file = '/home/files/hacker_news.rss'

hn_urls = [
    "https://hnrss.org/frontpage",
    "https://hnrss.org/active",
    "https://hnrss.org/best",
    "https://hnrss.org/newest?points=100",
    "https://hnrss.org/bestcomments"
]

def main(urls: list[str] = hn_urls):
    input_feeds = []
    for url in urls:
        input_feeds.append(feedparser.parse(url))

    output_feed = feedgenerator.Rss201rev2Feed(
        title=input_feeds[0].feed.title,
        link=input_feeds[0].feed.link,
        description=input_feeds[0].feed.subtitle,
        # will not cause item duplication
        lastBuildDate=datetime.now()
    )

    # deduplicate inside each excution
    unique_ids = set()

    for feed in input_feeds:
        for item in feed.entries:
            if item.id not in unique_ids:
                output_feed.add_item(
                    title=item.title,
                    link=item.id,
                    description=item.title + "<br>" + item.summary,
                    # Indicates when the item was published.
                    pubdate=datetime.strptime(
                        item.published, "%a, %d %b %Y %H:%M:%S %z"
                    ),
                    author_name=item.author,
                    # URL of a page for comments relating to the item.
                    comments=item.comments,
                    # A string that uniquely identifies the item.
                    unique_id=item.id,
                )
                unique_ids.add(item.id)

    # xml_string = output_feed.writeString("utf-8")
    # print(xml_string)
    
    with open(rss_file, 'w') as fp:
        output_feed.write(fp, 'utf-8')

if __name__ == "__main__":
    main(hn_urls)
