# -*- coding: utf-8 -*-

import codecs
import os
import sys
import csv
import re

#word = u'землетрясенiя'
#word = u'счастие'

def is_in_dict(word_try):

    is_in = 0

    w = word_try.encode('cp1251')

    with codecs.open('freq.csv', 'r') as dict0:
        freq = csv.reader(dict0, delimiter = ';')
        for line in freq:          
            lin = line[0].split()
            if w == lin[0]:
                is_in = is_in + 1

    with codecs.open('sharov.csv', 'r') as dict1:
        sharov = csv.reader(dict1, delimiter = ';')
        for line in sharov:
            if w == line[0]:
                is_in = is_in + 1

    with codecs.open('ozhegov.csv', 'r') as dict2:
        ozhegov = csv.reader(dict2, delimiter = ';')
        for line in ozhegov:
            if w == line[0]:
                is_in = is_in + 1

    with codecs.open('ushakov.csv', 'r') as dict3:
        ushakov = csv.reader(dict3, delimiter = ';')
        for line in ushakov:
            if w == line[0]:
                is_in = is_in + 1

    with codecs.open('zaliznyak.csv', 'r') as dict4:
        zaliznyak = csv.reader(dict4, delimiter = ';')
        for line in zaliznyak:
            if w == line[0]:
                is_in = is_in + 1

    if is_in > 0:
        return True
    else:
        return False
    

def ends_ie(word):
   
    word_try = word[:-2] + u'ие'

    if is_in_dict(word_try):
        word_res = word[:-2] + u'ия'
    else:
        word_try = word[:-2] + u'ия'
        if is_in_dict(word_try):
            word_res = word_try
        else:
            word_try = word[:-2] + u'ие'
            word_res = word_try

    return word_res


def is_in_sse(word):
    try:
        w = word.encode('cp1251')
        flag = 0
    except:
        return word
    point = 0
    size = 0
    point2 = 0
    with codecs.open('sse_words.csv', 'r') as dict5:
            freq = csv.reader(dict5, delimiter = ';')
            for line in freq:          
                lin = line[0]
                point = len(lin) - 2           
                if w[:point] == lin[:-2]:
                    flag = 1
                    point2 = point
    return flag, point2


def sse(word):
    try:
        w = word.encode('cp1251')
        flag = 0
    except:
        return word
    flag, point = is_in_sse(word)
    if flag == 1:
                    if len(w) >= point + 2:
                        if w[point] == u'и'.encode('cp1251'):
                            if word[point+1] == u'и' or word[point+1] == u'е' or word[point+1] == u'я' or word[point+1] == u'ю':
                                new_word = word[:point] + u'ь' + word[point+1:]
                                return new_word
                    else:
                        return word
    return word

def is_in_wrong_dict(word, name):

    try:
        w = word.encode('cp1251')
    except:
        return 0
    
    with codecs.open(name, 'r') as dict0:
        freq = csv.reader(dict0, delimiter = ';')
        for line in freq:          
            lin = line[0].split()
            if w == lin[0]:
                return 1
        return 0

def verbs_shol(word):

    if is_in_wrong_dict(word, 'verbs_shol.csv'):
        return word[:-2] + u'ел'
    else:
        return word

def adjs_ija(word):

    if is_in_wrong_dict(word, 'adjs_ija.csv'):
        return word[:-2] + u'ие'
    else:
        return word

##print sse(word)
    
