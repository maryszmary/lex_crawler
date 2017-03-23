'''
this is a crawler for http://onlineslovari.com/slovar_drevnerusskogo_yazyika_vv
'''

# суперэнтри -- это обязательная составляющая?

from urllib import parse
from urllib import request
from lxml import etree
from lxml import html
from bs4 import BeautifulSoup
import os


ROOT = 'http://onlineslovari.com/slovar_drevnerusskogo_yazyika_vv/'
with open('template.xml') as f:
    XML = f.read()
ENTRY = '''<superEntry><metalemma></metalemma><entry 
n='PLACEHOLDER_0' type='hom'><sense n='PLACEHOLDER_1'></sense></re><etym></etym>
</entry></superEntry>'''
FORM = '<form>{0}<gramGrp>{1}</gramGrp><inflection>{2}</inflection></form>'


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
    page = request.urlopen(link).read().decode('utf-8')

    # with open('mock_page.html') as f:
    #     page = f.read()

    entry = etree.fromstring('<superEntry></superEntry>')
    content = html.fromstring(page).xpath('.//div[@class="page"]')[0]
    gram = get_gram_info(content[0][0])
    # meanings = get_meanings(content[1:])
    # building the entry
    return entry


def get_gram_info(head):
    print([tag.tag for tag in head])
    lemma = head[0].text
    pos = head.xpath('em')[-1].text.strip('. ')
    if pos.split(' ')[-1] == 'к':
        xr = head.xpath('strong')[-1].text.strip('. ')
        pos = ' '.join(pos.split(' ')[:-1])
        print('XR DETECTED: ' + xr)
        # print(etree.tostring(head, encoding='utf-8').decode())
    lemma_xml = '<orth type="lemma" extent="full" >' + lemma + '</orth>'
    pos_xml = '<pos>' + pos + '</pos>'
    occ = '<usg type="plev">' +  head[0].tail.strip(' (), -') + '</usg>'
    infl = infl_constructor(head, pos, lemma)
    gram = etree.fromstring(FORM.format(lemma_xml + occ, pos_xml, infl))
    print(etree.tostring(gram, encoding='utf-8').decode())
    return gram


def infl_constructor(head, pos, lemma):
    flex = ''
    if '|' in lemma:
        flex = '<orth  extent="part">' + lemma.split('|')[-1] + '</orth>'
    gram = etree.Element('root')
    gram[:] = head[1:-1]
    gram = etree.tostring(gram, encoding='utf-8').decode()
    gram = BeautifulSoup(gram, 'html.parser').get_text()
    infl = ''
    if pos == 'гл':
        morph = gram.split(', ')
        infl = '<pers><sg1>' + morph[0] + '</sg1><sg3>'\
               + morph[1] + '</sg3></pers>'
    elif pos == 'с':
        infl = '<case><gen>' + gram + '</gen></case>' 
        etree.fromstring(infl)
    print('gram: ' + flex + infl)
    return flex + infl


def get_meanings(content):
    return meanings


def main():
    # links = root_walker()
    # with open('links', 'w') as f:
    #     f.write('\n'.join(links))
    xml = get_dictionary()



# if __name__ == '__main__':
#     main()
get_page_data('http://onlineslovari.com/slovar_drevnerusskogo_yazyika_vv/page/otyvty.8661/')
get_page_data('http://onlineslovari.com/slovar_drevnerusskogo_yazyika_vv/page/otymetati.8802/')
get_page_data('http://onlineslovari.com/slovar_drevnerusskogo_yazyika_vv/page/otylpiti.8799/')
get_page_data('http://onlineslovari.com/slovar_drevnerusskogo_yazyika_vv/page/more.3677/')
get_page_data('http://onlineslovari.com/slovar_drevnerusskogo_yazyika_vv/page/biny.592/')
