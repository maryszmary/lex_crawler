#-*- coding: utf-8 -*-
import re

def samelettter(word):
    word = word.replace('нн', 'н')
    word = word.replace('сс', 'с')
    word = word.replace('жж', 'ж')
    word = word.replace('зз', 'з')
    word = word.replace('вв', 'в')
    word = word.replace('тт', 'т')
    word = word.replace('лл', 'л')
    word = word.replace('дд', 'д')
    return word

def tyrt(word):
    word = re.sub('([цкнгшщзхфвпрлджчмстб])ъ([рл][цкгпдчтбзжмсхнвл])', '\\1о\\2', word)
    word = re.sub('([цкнгшщзхфвпрлджчмстб])ь([рл][цкгпдчтбзжмсхнвл])', '\\1е\\2', word)
    word = re.sub('([цкнгшщзхфвпрлджчмстб][рл])ь([цкгпдчтбзжмсхнвл])', '\\1е\\2', word)
    word = re.sub('([цкнгшщзхфвпрлджчмстб][рл])ъ([цкгпдчтбзжмсхнвл])', '\\1о\\2', word)
    return word


def hawlik_low(word):
    isodd = False
    lastletter = word[-1]
    word = list(word)
    vowels = list('уеыаѣоэяию')
    for i in xrange(len(word)):
        li = len(word) - i -1
        if word[li] in vowels:
            isodd = False
        elif word[li] == 'Ь':
            isodd = True
        if word[li] == 'ь' or word[li] == 'ъ':
            if isodd == True:
                word[li] = word[li].replace('ь', 'е')
                word[li] = word[li].replace('ъ', 'о')
                isodd = False
            else:
                isodd = True
                word[li] = ''
    word = ''.join(word)
    if lastletter == 'ъ' or lastletter == 'ь':
        word += lastletter
    return word


def letterchange(word):
    newword = word
    newword = newword.replace('i', 'и')
    newword = newword.replace('і', 'и')
    newword = newword.replace('ѡ', 'о')
    newword = newword.replace('є', 'e')
    newword = newword.replace('́', '')
    newword = newword.replace('́', '')
    newword = newword.replace('ѵ', 'и')
    newword = newword.replace('̂', '')
    newword = newword.replace('ѻ', 'о')
    newword = newword.replace('ѳ', 'ф')
    newword = newword.replace('ѯ', 'кс')
    newword = newword.replace('ѱ', 'пс')
    newword = newword.replace('ѕ', 'з')
    # newword = newword.replace('ѣ', 'е')
    newword = newword.replace('ꙋ', 'у')
    newword = newword.replace('ꙗ', 'я')
    newword = newword.replace('ѧ', 'я')
    newword = newword.replace('ѹ', 'у')
    return newword


def inter_new(word):
    newword = re.sub('([цкнгшщзхфвпрлджчсмтб])(ь|ъ)([цкнгшщзхфвпрлджчсмтб])', '\\1\\3', word)
    if newword[-1] == 'ъ':
        newword = newword[:-1]
    return newword


def modernize_oslo(word2):
    # word2 = word2.replace('ѣ", u"е')
    word2 = word2.replace('кы', 'ки')
    word2 = word2.replace('гы', 'ги')
    word2 = word2.replace('хы', 'хи')
    word2 = word2.replace('ыи', 'ый')
    word2 = word2.replace('ии', 'ий')
    return word2


def cluster_yers(word2):
    word3 = word2.replace('чст', 'чест')
    word3 = word3.replace('чск', 'ческ')
    return word3


def moscow_prefix_yers(word2):
    if (word2[0] == 'в' or word2[0] == 'с') and word2[1] == 'о' and len(word2) > 4:
        word2 = word2[0] + 'ъ' + word2[2:]
    return word2


def oslo_trans(goldlemma):
    goldlemma = letterchange(goldlemma)
    goldlemma = goldlemma.replace('льн', 'лЬн')
    goldlemma = tyrt(goldlemma)
    goldlemma = hawlik_low(goldlemma)
    goldlemma = cluster_yers(goldlemma)
    goldlemma = goldlemma.replace('лЬн', 'льн')
    # goldlemma = samelettter(goldlemma)
    goldlemma = modernize_oslo(goldlemma)
    consonants = 'кнгзхвпрлджмтб'.split()
    if goldlemma[-1] in consonants:
        goldlemma += 'ъ'
    return goldlemma

def indent(goldlemma, unilemma):
    unilemma = letterchange(unilemma)
    unilemma = moscow_prefix_yers(unilemma)
    unilemma = inter_new(unilemma)
    unilemma = unilemma.replace('зс', 'сс')
    unilemma = samelettter(unilemma)
    unilemma = unilemma.replace('жде', 'же')
    if unilemma == 'сеи':
        unilemma = 'сии'
    if unilemma == 'тои':
        unilemma = 'тыи'
    if unilemma == 'перед':
        unilemma = 'пред'
    if unilemma == 'писати':
        unilemma = 'псати'
    if unilemma == goldlemma:
        return True
    return False

# word = 'сьрдьце'
# print(hawlik_low(word))
# word = 'отьць'
# print(hawlik_low(word))
# word = 'отьца'
# print(hawlik_low(word))
# print(indent('отьць', 'отець'))
# print(moscow_prefix_yers('состояние'))

# print(oslo_trans('съмьрть'))
# print(oslo_trans('вълкъ'))
# print(oslo_trans('дългота'))
# print(oslo_trans('кръвопиица'))
# print(oslo_trans('довъльныи'))
# print(oslo_trans('обьльныи'))
