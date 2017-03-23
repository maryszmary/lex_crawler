'''
this is a crawler for http://onlineslovari.com/slovar_drevnerusskogo_yazyika_vv
'''

# суперэнтри -- это обязательная составляющая?

from urllib import parse
from urllib import request
from lxml import etree
from lxml import html
import os


ROOT = 'http://onlineslovari.com/slovar_drevnerusskogo_yazyika_vv/'
with open('template.xml') as f:
    XML = f.read()
ENTRY = '''<div><superEntry><metalemma></metalemma><entry 
n='PLACEHOLDER_0' type='hom'><form></form><gramGrp></gramGrp>
<form type="inflected"></form><sense n='PLACEHOLDER_1'></sense>
<re> <!-- дериваты --></re><etym><!-- блок этимологии --></etym>
</entry></superEntry></div>'''


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
    for i in range(len(links)):
        entry = get_page_data(link)
        di[1][i] = entry
    return di


def get_page_data(link):
    # page = request.urlopen(link).read().decode('utf-8')

    with open('mock_page.html') as f:
        page = f.read()

    entry = etree.fromstring('<div></div>')
    entries = html.fromstring(page).xpath('.//div[@class="page"]')
    print([en.text for en in entries[0].getchildren()[0].getchildren()])
    print([en.tag for en in entries[0].getchildren()[0].getchildren()])
    return entry


def main():
    # links = root_walker()
    # with open('links', 'w') as f:
    #     f.write('\n'.join(links))
    xml = get_dictionary()



# if __name__ == '__main__':
#     main()
get_page_data('http://onlineslovari.com/slovar_drevnerusskogo_yazyika_vv/page/otyvty.8661/')