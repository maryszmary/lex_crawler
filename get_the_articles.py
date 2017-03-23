from urllib import error
from urllib import request
import time


def crawl_them():
    '''just in case, downloading all the articles'''
    with open('links_left') as f:
        links = f.read().split('\n')
    for link in links:
        fname = link.split('/')[-2] + '.html'
        try:
            page = request.urlopen(link).read().decode('utf-8')
        except OSError:
            time.sleep(10)
            page = request.urlopen(link).read().decode('utf-8')
        with open('articles/' + fname, 'w') as f:
            f.write(page)
        print('article '  + fname + ' is wittten')

if __name__ == '__main__':
    crawl_them()
