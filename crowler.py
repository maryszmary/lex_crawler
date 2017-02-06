'''
this is a crawler for http://onlineslovari.com/slovar_drevnerusskogo_yazyika_vv
'''

from urllib import parse
from urllib import request
from lxml import etree
from lxml import html
import os


ROOT = 'http://onlineslovari.com/slovar_drevnerusskogo_yazyika_vv/'
XML = '''<xml><front><head><title>Словарь древнерусского языка (XI-XIV вв.)
</title><author>Перечислены авторы</author></head><dict_lang>rus</dict_lang>
</front><body></body><back></back></xml>'''


def root_walker():
    pages = [ROOT + str(i) + '/?&page=' + str(j) 
             for i in range(1, 19) for j in range(0, 5)]
    all_links = []
    for page in pages:
        root_page = request.urlopen(page).read().decode('utf-8')
        links = html.fromstring(root_page).xpath('.//div[@class="list"]')
        links = [ROOT + o[0].get('href').split('/', 2)[2] for o in links]
        all_links += links
    return all_links


def get_dictionary():
    di = etree.fromstring(XML)
    with open('links', 'r') as f:
        links = f.read().split('\n')
    for link in links:
        entry = get_page_data(link)
    return di


def get_page_data(link):
    page = request.urlopen(link).read().decode('utf-8')
    # div class="page"


def main():
    # links = root_walker()
    # with open('links', 'w') as f:
    #     f.write('\n'.join(links))
    xml = get_dictionary()



if __name__ == '__main__':
    main()
