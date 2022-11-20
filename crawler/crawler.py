#! /usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import lxml
import os
from database import Database

headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}

ignoredWords = ['an','and','the']


class Crawler:
    def __init__(self,  data: Database):
        self.db = data

    def addLinksToList(self, links):
        for link in links:
            print(link)
            hash, line_found = self.db.url_in_database(link)
            print(line_found)
            if  line_found == -1:
                uncrawl = self.db.build_crawled_url(link,{})
                self.db.add(uncrawl,True)

    #Searchs URL for any links located on that page
    def getPageLinks(self, link):
        base_url = link.split('/')[2]
        subpages = []

        req =  requests.get(link, headers = headers)

        #Only parse the data if we get a valid server response
        if req.status_code == 200:     
            soup = BeautifulSoup(req.content, 'lxml')

            _subpages = soup.find_all('a',recursive=True)

            #Go through all found links and verify valid
            for page in _subpages:
                #Ignore if no href tag
                if 'href' in str(page):
                    _page = page['href']
                    if _page.startswith('/'):
                        _page = base_url + _page

                    if _page.startswith('www'):
                        _page = 'http://' + _page

                    if _page.startswith('https'):
                        _page = _page.replace("https","http")

                    #ignore non http
                    if _page.startswith('http'):
                        subpages.append(_page)

            subpages.sort

            return subpages

    #Gathers keywords from URL page.
    def indexPage(self, url):
        req =  requests.get(url, headers = headers)
        #Only parse the data if we get a valid server response
        if req.status_code == 200:  
            soup = BeautifulSoup(req.content, 'lxml')

            title = soup.title.string
            keywords = title.split(" ")
            print(title)
            h1 = soup.find_all('h1',recursive=True)
            for heading in h1:
                temp = heading.get_text().strip().split(" ")
                for word in temp:
                    if word not in keywords:
                        keywords.append(word)
                print(temp)

            h2 = soup.find_all('h2',recursive=True)
            for heading in h2:
                temp = heading.get_text().strip().split(" ")
                for word in temp:
                    if word not in keywords:
                        keywords.append(word)
                print(temp)

            h3 = soup.find_all('h3',recursive=True)
            for heading in h3:
                temp = heading.get_text().strip().split(" ")
                for word in temp:
                    if word not in keywords:
                        keywords.append(word)
                print(temp)

            h4 = soup.find_all('h4',recursive=True)
            for heading in h4:
                temp = heading.get_text().strip().split(" ")
                for word in temp:
                    if word not in keywords:
                        keywords.append(word)
                print(temp)
            
            print(keywords)

            rel = {}
            text = soup.get_text().strip()
            for word in keywords:
                if (len(word)>1) and (word not in ignoredWords):
                    count = text.count(word)
                    rel.update({word:count})

            indexed = self.db.build_crawled_url(url,rel)
            self.db.add(indexed)




    def CrawlPage(self, url, index=False):
        subpages = []

        subpages = self.getPageLinks(url)

        #Write pages to file
        #TODO make it a DB to pull pages from.
        self.addLinksToList(subpages)

        if index:
            #TODO Search for index keywords for page
            self.indexPage(url)