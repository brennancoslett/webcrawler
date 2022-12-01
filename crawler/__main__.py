from crawler import Crawler
from database import Database

import threading
import argparse

def CrawlDomain(crawler: Crawler, db: Database, domain:str):
    """
    Function which takes a domain to crawl and adds its information to a
    database.
    Runs all secondary steps in 
    """
    threads = []

    # Crawl the top level domain
    pages = crawler.CrawlPage(domain, True)
    # Kick off a thread for each page.
    for page in pages:
        tmp_thread = threading.Thread(target=crawler.CrawlPage,args=[page, True])
        tmp_thread.start()
        threads.append(tmp_thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

def UpdateStale(crawler: Crawler, db: Database):
    """
    Function which takes a domain to crawl and adds its information to a
    database.
    Runs all secondary steps in 
    """
    threads = []

    # Crawl the top level domain
    stalePages = db.stale_urls()
    if len(stalePages) == 0:
        print("No Stale Pages to update")
    # Kick off a thread for each page.
    for page in stalePages:
        tmp_thread = threading.Thread(target=crawler.CrawlPage,args=[page, True])
        tmp_thread.start()
        threads.append(tmp_thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

def cleanup(db):
    db.cleanup()

if __name__ == "__main__":
    # Actual script execution goes in here
    # Database uses input_file for output file when output_file doesn't
    # exist yet.
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--crawl", help="Domain to crawl and add to database")
    parser.add_argument("-k", "--keyword", help="Keyword to search for in the database")
    parser.add_argument("-s", "--stale", action="store_true", help="Keyword to update stale urls in the database")
    args = parser.parse_args()

    if args.crawl is None and args.keyword is None and args.stale is False:
        print("args required, try `crawler -h`")
        exit(1)

    db = Database(input_file="data/database.msgpack")
    crawler = Crawler(db)

    try:
        if args.crawl:
            CrawlDomain(crawler, db, args.crawl)
        if args.stale:
            UpdateStale(crawler, db)
        if args.keyword:
            list = db.urls_with_keyword(args.keyword)
            for item in list:
                print(item)
    finally:
        # Ensure we always save our state before closing the program.
        cleanup(db)