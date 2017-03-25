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
FORM = '<form>{0}<gramGrp>{1}</gramGrp>{2}</form>'
INFL_FORM = '<form type="inflected">{0}<gramGrp>{1}</gramGrp></form>'
NUM = ['1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ']


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
    '''the main func for extracting the dictionaary data'''
    di = etree.fromstring(XML)
    articles = os.listdir('mock_articles')

    for i in range(len(articles)):
        entry = get_page_data(articles[i])
        di[-1][0].append(entry)
    return di


def get_page_data(fname):
    '''responsible for extration of all the information from a page'''
    with open('mock_articles/' + fname) as f:
        page = f.read()
    content = html.fromstring(page).xpath('.//div[@class="page"]')[0]
    lemma = content[0][0][0].text

    # there are some articles without examples o_O
    # try:
    meaning, polysemic = get_meaning(content[0])
    # except IndexError: # DEBUG
    #     print('no examples: ' + fname)
    #     polysemic = False
    #     meaning = []
    # except etree.XMLSyntaxError:
    #     print('etree.XMLSyntaxError: ' + fname)
    

    # DEBUG
    gram = get_gram_info(content[0][0], lemma, fname)
    # except Exception as e:
    #     print(str(e) + ': ' + fname)
    #     raise e

    # building the entry
    entry = etree.fromstring(ENTRY)
    entry[1].append(gram)
    entry[1][1:] = meaning
    return entry


def get_gram_info(head, lemma, fname):
    try:
        pos = head.xpath('em')[-1].text.strip('. ')
    except IndexError:
        print('IndexError: ' + fname)
        # gram = etree.fromstring('<form><orth type="lemma" extent="full" >{0}</orth></form>'.format(lemma))
    xr = ''
    if pos.split(' ')[-1] == 'к':
        pos = ' '.join(pos.split(' ')[:-1])
        xr = head.xpath('strong')[-1].text.strip('. ')
        xr = '<xr>' + xr + '</xr>'
        # print('XR DETECTED: ' + xr)
    pos_xml = '<pos>' + pos + '</pos>' + xr
    lemma_xml = '<orth type="lemma" extent="full" >' + lemma + '</orth>'
    occ = get_freq(head)

    infl = infl_constructor(head, pos, lemma)
    if pos in ['гл', 'с']:
        form = etree.fromstring(INFL_FORM.format(lemma_xml + occ, pos_xml, infl))
    else:
        form = etree.fromstring(INFL_FORM.format(lemma_xml + occ, pos_xml))
    print('form: ' + etree.tostring(form, encoding='utf-8').decode())
    return form


def get_freq(head):
    '''getting the number of occurencies'''
    pssbl_occ = head[0].tail
    if pssbl_occ is not None:
        occ = '<usg type="plev">' + head[0].tail.strip(' (), -') + '</usg>'
    else:
        # this is made, because in some articles the location of freq is not typical
        occ = '<usg type="plev">' + head[1][0].text + '</usg>'
        print('untypical location of OCC: ' + occ)
    return occ


def infl_constructor(head, pos, lemma):
    infl = []
    gram = etree.Element('root')
    gram[:] = head[1:-1]
    gram = etree.tostring(gram, encoding='utf-8').decode()
    gram = BeautifulSoup(gram, 'html.parser').get_text()
    if pos == 'гл':
        if '|' in lemma:
            infl = ['<orth  extent="part">' + lemma.split('|')[-1] + '</orth>']
            # flex = '<inflection>' + flex + '</inflection>'
        morph = gram.split(', ')
        infl += ['<per><sg1>' + morph[0] + '</sg1></per>', '<per><sg3>'\
                 + morph[1] + '</sg3></per>']
        infl = ['<inflection>' + f + '</inflection>' for f in infl]
    elif pos == 'с':
        if '|' in lemma:
            infl = ['<case><orth  extent="part">' + lemma.split('|')[-1] + '</orth>']
        infl += ['<case><gen>' + gram + '</gen></case>'] 
        infl = ['<inflection>' + f + '</inflection>' for f in infl]
    return ''.join(infl)


def get_meaning(content):
    # supposedly, if it doesn't start with None, the word is polysemic
    if content[1].text is not None:
        senses = content.xpath('div')
        senses = [(senses[i], senses[i + 1]) for i in range(len(senses))
                  if senses[i].text in NUM]
        result = []
        for i in range(len(senses)):
            sense = etree.fromstring('<sense n="{0}"></sense>'.format(str(i)))
            lbl = senses[i][0].text
            lbl = etree.fromstring('<lbl>' + lbl + '</lbl>')
            defin = senses[i][0][0].text
            defin = etree.fromstring('<def>' + defin + '</def>')
            sense.append(lbl)
            sense.append(defin)
            sense = append_cits(sense, senses[i][1])
            result.append(sense)
        return result, True

    # let's assume that these words are not polysemic
    else:
        sense = etree.fromstring('<sense n="1"></sense>')
        defin = content[0].xpath('em')[-1].text
        defin = etree.fromstring('<def>' + defin + '</def>')
        sense.append(defin)
        sense = append_cits(sense, content)
        return [sense], False


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
    with open('old_russian.tei', 'w') as f:
        text = etree.tostring(xml, encoding='utf-8').decode()
        f.write(text)


if __name__ == '__main__':
    main()
# get_page_data('otyvty.8661.html')
# get_page_data('otymetati.8802.html')
# get_page_data('biny.592.html')
# get_page_data('bezbojno.128.html') 
