'''
this is a crawler for http://onlineslovari.com/slovar_drevnerusskogo_yazyika_vv
'''

# проблемы:
# значение то внизу, то в шапке
# непонятно, как вытаскивать def из штук типа "причастие к бити"

from urllib import parse
from urllib import request
from lxml import etree
from lxml import html
from bs4 import BeautifulSoup
import os


ROOT = 'http://onlineslovari.com/slovar_drevnerusskogo_yazyika_vv/'
with open('template.xml') as f:
    XML = f.read()
ENTRY = '<superEntry><metalemma></metalemma><entry></entry></superEntry>'
FORM = '<form>{0}<gramGrp>{1}</gramGrp></form>'
INFL_FORM = '<form>{0}<gramGrp>{1}</gramGrp><inflection>{2}</inflection></form>'
NUM = ['1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ']


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
    # with open('links', 'r') as f:
    #     links = f.read().split('\n')

    articles = os.listdir('mock_articles')

    for i in range(len(articles)):
        entry = get_page_data(articles[i])
        di.append(entry)
    return di


def get_page_data(fname):
    # page = request.urlopen(link).read().decode('utf-8')

    with open('mock_articles/' + fname) as f:
        page = f.read()

    entry = etree.fromstring(ENTRY)
    content = html.fromstring(page).xpath('.//div[@class="page"]')[0]

    # there are some articles without examples o_O
    try:
        meanings = get_meanings(content[0])
    except IndexError:
        print('no examples: ' + fname)
        meanings = []
    except etree.XMLSyntaxError:
        print('etree.XMLSyntaxError: ' + fname)
    
    lemma = content[0][0][0].text
    try:
        gram = get_gram_info(content[0][0], lemma)
    except:
        gram = etree.fromstring('<form><orth type="lemma" extent="full" >{0}</orth></form>'.format(lemma))
    # building the entry
    entry[1].append(gram)
    entry[1][1:] = meanings
    return entry


def get_gram_info(head, lemma):
    # lemma = head[0].text
    pos = head.xpath('em')[-1].text.strip('. ')
    xr = ''
    if pos.split(' ')[-1] == 'к':
        pos = ' '.join(pos.split(' ')[:-1])
        xr = head.xpath('strong')[-1].text.strip('. ')
        xr = '<xr>' + xr + '</xr>'
        # print('XR DETECTED: ' + xr)
        # print(etree.tostring(head, encoding='utf-8').decode())
    pos_xml = '<pos>' + pos + '</pos>' + xr
    lemma_xml = '<orth type="lemma" extent="full" >' + lemma + '</orth>'
    occ = '<usg type="plev">' +  head[0].tail.strip(' (), -') + '</usg>'
    infl = infl_constructor(head, pos, lemma)
    if pos in ['гл', 'с']:
        form = etree.fromstring(INFL_FORM.format(lemma_xml + occ, pos_xml, infl))
    else:
        form = etree.fromstring(FORM.format(lemma_xml + occ, pos_xml))
    print('form: ' + etree.tostring(form, encoding='utf-8').decode())
    return form


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
    return flex + infl


def get_meanings(content):
    # supposedly, if it doesn't start with None, the word is polysemic
    if content[1].text is not None:
        senses = content.xpath('div')
        senses = [(senses[i], senses[i + 1]) for i in range(len(senses))
                  if senses[i].text in NUM]
        result = []
        for i in range(len(senses)):
            sense = etree.fromstring('<sense n="{0}"></sense>'.format(str(i)))
            defin = senses[i][0][0].text
            lbl = senses[i][0].text
            print(lbl)
            print(defin)
            defin = etree.fromstring('<def>' + defin + '</def>')
            lbl = etree.fromstring('<lbl>' + lbl + '</lbl>')
            sense = append_cits(sense, senses[i][1])
            result.append(sense)
        return result

    # let's assume that these words are not polysemic
    else:
        sense = etree.fromstring('<sense n="1"></sense>')
        defin = content[0].xpath('em')[-1].text
        defin = etree.fromstring('<def>' + defin + '</def>')
        sense.append(defin)
        sense = append_cits(sense, content)
        return [sense]
    return []


def append_cits(sense, content):
    cits = content.xpath('.//span[@class="dic_example"]')[0]
    examples = cits.xpath('.//span[@style="color: steelblue;"]')
    sources = cits.xpath('.//em/span')
    # print('len of cits: ' + str(len(examples)))
    # print('len of sources: ' + str(len(sources)))
    for pair in zip(examples, sources):
        cit = '<cit><text>{0}</text><src>{1}</src></cit>'.format(pair[0].text, pair[1].text)
        cit = etree.fromstring(cit)
        sense.append(cit)
    return sense


def main():
    # links = root_walker()
    # with open('links', 'w') as f:
    #     f.write('\n'.join(links))
    xml = get_dictionary()
    with open('old_church_slavonic.tei', 'w') as f:
        text = etree.tostring(xml, encoding='utf-8').decode()
        f.write(text)



if __name__ == '__main__':
    main()
# get_page_data('otyvty.8661.html')
# get_page_data('otymetati.8802.html')
# get_page_data('biny.592.html')
# get_page_data('bezbojno.128.html') 
# get_page_data('http://onlineslovari.com/slovar_drevnerusskogo_yazyika_vv/page/more.3677/') 
