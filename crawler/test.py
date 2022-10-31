#! /usr/bin/env python3
#NOTE: WIP -- This is only for me to test the current crawler without the use of a class.

from bs4 import BeautifulSoup
import requests
import lxml

headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}

url = "https://www.ndsu.edu/me/"
baseURL = url.split('/')[2]
subPages = []

req =  requests.get(url, headers = headers)

#Only parse the data if we get a valid server response
if req.status_code == 200:     
        soup = BeautifulSoup(req.content, 'lxml')

        _subPages = soup.find_all('a')


        for page in _subPages:
            _page = page['href']
            if _page.startswith('/'):
                _page = baseURL + _page

            if _page.startswith('www'):
                _page = 'http://' + _page

            #ignore non http
            if _page.startswith('http'):
              subPages.append(_page)

        subPages.sort
        f = open("data/pages.txt", "a")
        for page in subPages:
          f.write(page +'\n')

        f.close()