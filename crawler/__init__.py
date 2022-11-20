from crawler import Crawler
from database import Database
import random
import string
import threading

pagesToCrawl = []

def randomstring():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

def randomint():
    return int(random.random() * 1000000)

def append_db(db, len):
    for x in range(len):
        rel = {"tacos": randomint(), "networking":randomint(), "blah":randomint(), "data":randomint()}
        crawled = db.build_crawled_url(randomstring(), rel)
        db.add(crawled)

def main(crawler:Crawler, db:Database):
    pages = crawler.CrawlPage("http://www.ndsu.edu/",True)
    for page in pages:
        hash, index = db.url_in_database(page)
        if index == -1:
            temp = crawler.CrawlPage(page,True)
            [pages.append(x) for x in temp if x not in pages]
            
    stalePages = db.stale_urls()
    for page in stalePages:
        hash, index = db.url_in_database(page)
        if index == -1:
            temp = crawler.CrawlPage(page,True)
            [stalePages.append(x) for x in temp if x not in stalePages]

    print(len(db.data))

def cleanup(db):
    db.cleanup()

if __name__ == "__main__":
    # Actual script execution goes in here
    # Database uses input_file for output file when output_file doesn't
    # exist yet.
    db = Database(input_file="data/test_database.msgpack") # test_*.msgpack is in .gitignore
    crawler = Crawler(db)
    try:
        main(crawler, db)
    finally:
        # Ensure we always save our state before closing the program.
        cleanup(db)