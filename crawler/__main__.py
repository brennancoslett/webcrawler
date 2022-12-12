from crawler import Crawler
from database import Database

from queue import Queue
from threading  import Thread
import argparse
from os import cpu_count


# Set up some global variables
num_fetch_threads = cpu_count() - 2 
enclosure_queue = Queue()
crawled_pages = []

def CrawlerThread(crawler: Crawler, db: Database, q: Queue):
    while True:
        url = q.get()
        if url not in crawled_pages:
            pages = crawler.CrawlPage(url,True,False)
            crawled_pages.append(url)
            for page in pages:
                if page not in crawled_pages:
                    q.put(page)
        q.task_done()
        #print(f'Progress: {len(crawled_pages)} of {len(q.queue)}')


def CrawlDomain(crawler: Crawler, db: Database, domain:str):
    """
    Function which takes a domain to crawl and adds its information to a
    database.
    Runs all secondary steps in 
    """
    # Add feeder URL
    enclosure_queue.put(domain)

    for i in range(num_fetch_threads):
        worker = Thread(target=CrawlerThread, args=(crawler,db,enclosure_queue),daemon=True)
        worker.start()

    print('*** Main thread waiting')
    enclosure_queue.join()
    print('*** Done')
 
def UpdateStale(crawler: Crawler, db: Database):
    """
    Function which takes a domain to crawl and adds its information to a
    database.
    Runs all secondary steps in 
    """

    # Crawl the top level domain
    stalePages = db.stale_urls()
    if len(stalePages) == 0:
        print("No Stale Pages to update")
    else:
        # Add stale URLs
        for page in stalePages:
            enclosure_queue.put(page) 
        #Create multiple threads
        for i in range(num_fetch_threads):
            worker = Thread(target=CrawlerThread, args=(crawler,db,enclosure_queue))
            worker.setDaemon(True)
            worker.start()
        
        print('*** Parsing Stale Pages ***')
        enclosure_queue.join()
        print('*** Done ***')

def ListInfo(db: Database):
    print(f"Database filename: '{db.input_file}'")
    print(f"Number of entries: {len(db)}")
    print(f"Number of keywords: {len(db.keyword_dict)}")
    print(f"Database load time: {db.load_time * 1000:.04f} ms")

def cleanup(db):
    db.cleanup()

if __name__ == "__main__":
    # Actual script execution goes in here
    # Database uses input_file for output file when output_file doesn't
    # exist yet.
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--crawl", help="Domain to crawl and add to database")
    parser.add_argument("-k", "--keyword", help="Keyword to search for in the database")
    parser.add_argument("-l", "--list", action="store_true", help="Display information about the Database")
    parser.add_argument("-s", "--stale", action="store_true", help="Keyword to update stale urls in the database")
    args = parser.parse_args()

    if args.crawl is None and args.keyword is None and args.stale is False and args.list is False:
        print("args required, try `crawler -h`")
        exit(1)

    db = Database(input_file="data/database.msgpack")
    crawler = Crawler(db)

    try:
        if args.list:
            ListInfo(db)
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