from crawler import Crawler
from database import Database
import random
import string

def randomstring():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

def randomint():
    return int(random.random() * 1000000)

def append_db(db, len):
    for x in range(len):
        rel = {"tacos": randomint(), "networking":randomint(), "blah":randomint(), "data":randomint()}
        crawled = db.build_crawled_url(randomstring(), rel)
        db.add(crawled)

def main(crawler, db):
    crawler.CrawlPage("http://www.ndsu.edu/me",True)
    print(db)

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