import PySimpleGUI as sg
import sys
import os

from queue import Queue
from threading  import Thread
import argparse
from os import cpu_count
sys.path.append(os.getcwd())

from crawler.crawler import Crawler
from crawler.database import Database

db = Database(input_file="data/database.msgpack")
crawl = Crawler(db)
data = []

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

# GUI Stuff
sg.theme('Reddit')

layout = [[sg.Text('Search Keyword or Phrase:'),
           sg.Text(size=(15,1), key='-OUTPUT-')],
          [sg.Input(key='-IN-')],
          [sg.Button('Crawl'), sg.Button('Search'), sg.Button('Exit')],
          [sg.Listbox(data, key='-TABLE-',size=(50,10))]]
  
window = sg.Window('Search Engine', layout,resizable=True)

keyword = sg.Input(key='-IN-') 

while True:
    event, values = window.read()
    crawlerControl = Thread()
    print(event, values)
      
    if event == 'Search':
        # Update the "output" text element
        # to be the value of "input" element
        data = db.urls_with_keyword(values['-IN-'])
        window.Element("-TABLE-").Update(values=data)

    if event == 'Crawl':
        crawlerControl = Thread(target=CrawlDomain,args=(crawl, db, values['-IN-']))
        window.Element("Crawl").update(disabled=True)
        crawlerControl.start()
        
    if event == sg.WINDOW_CLOSED or event == "Exit":
        raise KeyboardInterrupt  

    print(event, values)
  
window.close()