#! /usr/bin/env python3

from bs4 import BeautifulSoup
import requests
from crawler.database import Database
from queue import Queue
from threading  import Thread
import argparse
from os import cpu_count

headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}

ignoredWords = ['an','and','the']


class Crawler():
    """
    Object which handles crawling through webpages to pull out keywords.
    """

    # Set up some global variables
    num_fetch_threads = cpu_count() - 2 
    enclosure_queue = Queue()
    crawled_pages = []
    base_url = ""

    def __init__(self,  data: Database):
        self.db = data



    def addLinksToList(self, links):
        domainPages = []
        for link in links:
            # hash, line_found = self.db.url_in_database(link)
            # if  line_found == -1:
            #     uncrawl = self.db.build_crawled_url(link,{})
            #     self.db.add(uncrawl,True)
            #Check if link is in same domain
            if link.startswith("http://" + self.base_url + '/') or link.startswith("http://www." + self.base_url + '/'):
                domainPages.append(link)
        return domainPages

    #Searchs URL for any links located on that page
    def getPageLinks(self, link):
        self.base_url = link.split('/')[2]
        subpages = []
        try:
            req =  requests.get(link, headers = headers)

            #Only parse the data if we get a valid server response
            if req.status_code == 200:     
                soup = BeautifulSoup(req.content, 'lxml')

                _subpages = soup.find_all('a',recursive=True)

                #Go through all found links and verify valid
                for page in _subpages:
                    #Ignore if no href tag
                    if page.get('href', None) is not None:
                        _page = page['href']
                        if _page.startswith('/'):
                            _page = self.base_url + _page

                        if _page.startswith('www'):
                            _page = 'http://' + _page

                        if _page.startswith('https'):
                            _page = _page.replace("https","http")

                        #ignore non http
                        if _page.startswith('http'):
                            subpages.append(_page)

                subpages.sort

                return subpages
        except Exception:
            print('Failed to parse:\t' + link)
            return []

    #Gathers keywords from URL page.
    def indexPage(self, url, forceUpdate=False):
        if forceUpdate or self.db.url_in_database(url) == -1:
            try:
                req =  requests.get(url, headers = headers)
                #Only parse the data if we get a valid server response
                if req.status_code == 200:  
                    soup = BeautifulSoup(req.content, 'lxml')
                    keywords=[]
                    if soup.title != None:
                        title = soup.title.string
                        try:
                            keywords = title.split(" ")
                        except Exception:
                            print(Exception)
                        finally:
                            print(title)


                    h1 = soup.find_all('h1',recursive=True)
                    for heading in h1:
                        try:
                            temp = heading.get_text().strip().split(" ")
                            for word in temp:
                                if word not in keywords:
                                    keywords.append(word)
                        except Exception:
                            print(Exception)
                    
                    h2 = soup.find_all('h2',recursive=True)
                    for heading in h2:
                        try:
                            temp = heading.get_text().strip().split(" ")
                            for word in temp:
                                if word not in keywords:
                                    keywords.append(word)
                        except Exception:
                            print(Exception)

                    h3 = soup.find_all('h3',recursive=True)
                    for heading in h3:
                        try:
                            temp = heading.get_text().strip().split(" ")
                            for word in temp:
                                if word not in keywords:
                                    keywords.append(word)
                        except Exception:
                            print(Exception)

                    h4 = soup.find_all('h4',recursive=True)
                    for heading in h4:
                        try:
                            temp = heading.get_text().strip().split(" ")
                            for word in temp:
                                if word not in keywords:
                                    keywords.append(word)
                        except Exception:
                            print(Exception)
                    
                    rel = {}
                    text = soup.get_text().strip()
                    for word in keywords:
                        if (len(word)>1) and (word not in ignoredWords):
                            count = text.count(word)
                            rel.update({word:count})

                    indexed = self.db.build_crawled_url(url,rel)
                    self.db.add(indexed,forceUpdate)
            except Exception:
                print('Failed to parse:\t' + url)

    def CrawlPage(self, url, index=False, forceUpdate=True):
        subpages = self.getPageLinks(url)

        #Write pages to file
        if subpages != None:
            domainPages = self.addLinksToList(subpages)

            if index:
                #TODO Search for index keywords for page
                self.indexPage(url, forceUpdate)

            return domainPages
        else:
            return []

    
    def CrawlerThread(self,q: Queue):
        while True:
            url = q.get()
            if url not in self.crawled_pages:
                pages = self.CrawlPage(url,True,False)
                self.crawled_pages.append(url)
                for page in pages:
                    if page not in self.crawled_pages:
                        q.put(page)
            q.task_done()
            #print(f'Progress: {len(crawled_pages)} of {len(q.queue)}')

    def CrawlDomain(self,domain:str):
        """
        Function which takes a domain to crawl and adds its information to a
        database.
        Runs all secondary steps in 
        """
        # Add feeder URL
        self.enclosure_queue.put(domain)

        for i in range(self.num_fetch_threads):
            worker = Thread(target=Crawler.CrawlerThread, args=(self.enclosure_queue),daemon=True)
            worker.start()

        print('*** Main thread waiting')
        self.enclosure_queue.join()
        print('*** Done')
    
    def UpdateStale(self):
        """
        Function which takes a domain to crawl and adds its information to a
        database.
        Runs all secondary steps in 
        """

        # Crawl the top level domain
        stalePages = self.db.stale_urls()
        if len(stalePages) == 0:
            print("No Stale Pages to update")
        else:
            # Add stale URLs
            for page in stalePages:
                self.enclosure_queue.put(page) 
            #Create multiple threads
            for i in range(self.num_fetch_threads):
                worker = Thread(target=self.CrawlerThread, args=(self.enclosure_queue))
                worker.setDaemon(True)
                worker.start()
            
            print('*** Parsing Stale Pages ***')
            self.enclosure_queue.join()
            print('*** Done ***')
