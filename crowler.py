'''
this is a crawler for http://onlineslovari.com/slovar_drevnerusskogo_yazyika_vv
'''

# проблемы:
# значение то внизу, то в шапке
# непонятно, как вытаскивать def из штук типа "причастие к бити"
# AAAAAH. the dictionary is virtually impossible tp parse! Сделать что-то с комментариями в квадратных скобках. которые распознаются как источники.
# у слов с одним значением бывает два параграфа с примером (otrblti)

from urllib import parse
from urllib import request
from lxml import etree
from lxml import html
from lxml import objectify
from bs4 import BeautifulSoup
import os
import re

ROOT = 'http://onlineslovari.com/slovar_drevnerusskogo_yazyika_vv/'
with open('template.xml') as f:
    XML = f.read()
ENTRY = '<superEntry><metalemma></metalemma><entry></entry></superEntry>'
NUM = ['1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ']
FORM = '<form>{0}<gramGrp>{1}</gramGrp></form>'
INFL_FORM = '<form type="inflected">{0}<gramGrp>{1}</gramGrp>{2}</form>'
NOUN_LEM = '<inflection><orth extent="part">{0}</orth><lbl>nom.sg</lbl></inflection>'
# NOUN = '<inflection><orth extent="part">{0}</orth><case>gen</case><num>sg</num></inflection>'
NOUN = '<inflection><orth extent="part">{0}</orth><lbl>gen.sg</lbl></inflection>'
# VERB = '<inflection><orth extent="part">{0}</orth><per>{1}</per></inflection>'
VERB = '<inflection><orth extent="part">{0}</orth><lbl>{1}</lbl></inflection>'
INFI = '<inflection><orth extent="part">{0}</orth><lbl>inf</lbl></inflection>'
DIRNAME = 'articles'


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
    articles = os.listdir(DIRNAME)

    for i in range(len(articles)):
        try:
            entry = get_page_data(articles[i])
            di[-1][0].append(entry)
        except Exception as e:
            os.system('echo "{0} : {1}" >> all_problematic_articles'.format(articles[i], str(e)))
    di[0][1].text = str(len(di[-1][0]))
    return di


def get_page_data(fname):
    '''responsible for extration of all the information from a page'''
    # print(fname)
    with open(DIRNAME + '/' + fname) as f:
        page = f.read()
    content = html.fromstring(page).xpath('.//div[@class="page"]')[0]
    lemma = content[0][0][0].text.replace(chr(747), '')

    # there are some articles without examples o_O
    # try:
    meaning, polysemic = get_meaning(content[0], fname)
    # except IndexError: # DEBUG
    #     print('no examples: ' + fname)
    #     polysemic = False
    #     meaning = []
    # except etree.XMLSyntaxError:
    #     print('etree.XMLSyntaxError: ' + fname)
    
    gram, xrs = get_gram_info(content[0][0], lemma, fname)

    # building the entry
    entry = etree.fromstring(ENTRY)
    entry[1].append(gram)
    entry[1][1:] = meaning
    entry[1][len(entry):] = xrs
    return entry


def get_gram_info(head, lemma, fname):
    try:
        pos = head.xpath('em')[-1].text.strip('. ')
    except IndexError:
        print('IndexError: ' + fname)
        # gram = etree.fromstring('<form><orth type="lemma" extent="full" >{0}</orth></form>'.format(lemma))
    xrs = []
    if pos.split(' ')[-1] in ['к', 'что']:
        pos = ' '.join(pos.split(' ')[:-1])
        xr = head.xpath('strong')[-1].text.strip('.')
        if xr != '':
            xr = '<xr><ref>' + xr + '</ref></xr>'
            xrs.append(etree.fromstring(xr))
    if '.' in pos:
        pos = pos.rsplit('.', 1)[0]
    pos_xml = '<pos>' + pos + '</pos>'
    lemma_xml = '<orth type="lemma" extent="full" >' + lemma + '</orth>'
    occ = get_freq(head)

    if pos in ['гл', 'с']:
        infl = infl_constructor(head, pos, lemma, fname)
        form = etree.fromstring(INFL_FORM.format(lemma_xml + occ, pos_xml, infl))
    else:
        form = etree.fromstring(FORM.format(lemma_xml + occ, pos_xml))
    # print('form: ' + etree.tostring(form, encoding='utf-8').decode())
    return form, xrs


def get_freq(head):
    '''getting the number of occurencies'''
    pssbl_occ = head[0].tail
    if pssbl_occ is not None:
        occ = '<usg type="plev">' + head[0].tail.strip(' (), -') + '</usg>'
    else:
        # this is made, because in some articles the location of freq is not typical
        occ = '<usg type="plev">' + head[1][0].text + '</usg>'
        # print('untypical location of OCC: ' + occ)
    return occ


def infl_constructor(head, pos, lemma, fname):
    '''builds the part "inflection"'''
    gram = etree.Element('root')
    gram[:] = head[1:-1]
    gram = etree.tostring(gram, encoding='utf-8').decode()
    gram = BeautifulSoup(gram, 'html.parser').get_text()
    if pos == 'гл':
        infl = [INFI.format(lemma.split('|')[-1])]
        morph = gram.split(', ')
        infl += [VERB.format(morph[0], '1sg'), VERB.format(morph[1], '3sg')]
    elif pos == 'с':
        infl = [NOUN_LEM.format(lemma.split('|')[-1])]
        infl += [NOUN.format(gram.strip())]
    return ''.join(infl)


def get_meaning(content, fname):
    # supposedly, if it doesn't start with None, the word is polysemic
    if content[1].text is not None:
        senses = content.xpath('div')
        senses = [(senses[i], senses[i + 1]) for i in range(len(senses))
                  if senses[i].text in NUM]
        result = []
        for i in range(len(senses)):
            sense = etree.fromstring('<sense n="{0}"></sense>'.format(str(i + 1)))
            lbl = senses[i][0].text
            lbl = etree.fromstring('<lbl>' + lbl + '</lbl>')
            defin = senses[i][0][0].text
            if '.' in defin:
                defin = defin.rsplit('.', 1)[-1].strip(' ')
            defin = etree.fromstring('<def>' + defin + '</def>')
            sense.append(lbl)
            sense.append(defin)
            sense = append_cits(sense, senses[i][1], fname)
            result.append(sense)
        return result, True

    # let's assume that these words are not polysemic
    else:
        sense = etree.fromstring('<sense n="1"></sense>')
        defin = content[0].xpath('em')[-1].text
        if '.' in defin:
            defin = defin.rsplit('.', 1)[-1].strip(' ')
        defin = etree.fromstring('<def>' + defin + '</def>')
        sense.append(defin)
        sense = append_cits(sense, content, fname)
        return [sense], False


def append_cits(sense, content, fname):
    cits = content.xpath('.//span[@class="dic_example"]')[0]
    examples = cits.xpath('.//span[@style="color: steelblue;"]')
    examples = [example for example in examples if example.text is not None]
    pairs = source_example_pairs(examples)
    for pair in pairs:
        cit = '<cit><text>{0}</text><src>{1}</src></cit>'.format(pair[0], pair[1])
        cit = etree.fromstring(cit)
        sense.append(cit)
    return sense


def source_example_pairs(examples):
    pairs = []
    i = 0
    while i < len(examples):
        example = examples[i]
        text = example.text
        if example.text[-1] == '[':
            ntag = example.getnext()
            text += ntag[0].text + examples[i + 1].text
            source = examples[i + 1].getnext()[0].text
            i += 1
        elif example.text in [' (', '. ('] and i != 0:
            pairs[-1][1] += ' (' + example.getnext()[0].text + ')'
            i += 1
            continue
        elif example.text in [', ', '–', '—', '/', ' ', '.–'] and i != 0:
            pairs[-1][1] += example.text + example.getnext()[0].text
            i += 1
            continue
        elif examples[i].getnext() is None: # the end of examples
            break
        else:
            source = examples[i].getnext()[0].text
        text = re.sub('^\\)?; ?', '', text)
        pairs.append([text, source])
        i += 1
    return pairs


def main():
    # links = root_walker()
    # with open('links', 'w') as f:
    #     f.write('\n'.join(links))
    xml = get_dictionary()
    with open('old_russian.tei', 'w') as f:
        text = etree.tostring(xml, encoding='utf-8').decode()
        xml = objectify.fromstring(text)
        text = etree.tostring(xml, encoding='utf-8', pretty_print=True).decode()
        f.write(text)


if __name__ == '__main__':
    main()
