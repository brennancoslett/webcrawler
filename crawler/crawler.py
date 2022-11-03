#! /usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import lxml
import os

headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}


class Crawler:
    def __init__(self, database="data/database.json"):
        self.database = database

    def addLinksToList(self, links, filename="data/links.dat"):
        with open(filename, "r+") as f:
            for link in links:
                line_found = any(link in line for line in f)
                if not line_found:
                    f.seek(0, os.SEEK_END)
                    f.write(link.strip() + "\n") 
            f.close()

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
            print(title)
            h1 = soup.find_all('h1',recursive=True)
            for heading in h1:
                print(heading.get_text().strip())

            h2 = soup.find_all('h2',recursive=True)
            for heading in h2:
                print(heading.get_text().strip())

            h3 = soup.find_all('h3',recursive=True)
            for heading in h3:
                print(heading.get_text().strip())

            h4 = soup.find_all('h4',recursive=True)
            for heading in h4:
                print(heading.get_text().strip())


    def crawlPage(self, url, index=False):
        subpages = []

        subpages = self.getPageLinks(url)

        #Write pages to file
        #TODO make it a DB to pull pages from.
        self.addLinksToList(subpages,"data/links.dat")

        if index:
            #TODO Search for index keywords for page
            self.indexPage(url)