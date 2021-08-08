# -*- coding: cp1251 -*-
import re

#text = u'по Русски, По фРанцузски'

def pretreatment(text):
    text = text.replace(u'\r', u'/@/')
    return text

def hypens(text):
    text = text.replace(u'что нибудь', u'что-нибудь')
    text = text.replace(u'Что нибудь', u'Что-нибудь')
    text = text.replace(u'как нибудь', u'как-нибудь')
    text = text.replace(u'Как нибудь', u'Как-нибудь')
    text = text.replace(u'кто нибудь', u'кто-нибудь')
    text = text.replace(u'Кто нибудь', u'Кто-нибудь')
    text = text.replace(u'по-крайней-мере', u'по крайней мере')
    text = text.replace(u'По-крайней-мере', u'По крайней мере')
    return text

def change_reg(obj):
    word = obj.group()
    part = word[1:].lower()
    new_word = word[0] + part
    return new_word

def in_smbs_way(text):
    text = re.sub(ur'([Пп]о) ([А-Яа-я]*ски)', u'\g<1>-\g<2>', text)
    text = re.sub(ur'([Пп]о-[А-Яа-я]*ски)', change_reg, text)
    return text

def return_line_feed(text):
    text = text.replace(u' /@/ ', u'\r')
    text = text.replace(u'/@/ ', u'\r')
    text = text.replace(u' /@/', u'\r')
    text = text.replace(u'/@/', u'\r')
    return text

def fused_and_separated(text):
    text = text.replace(u'не долюблив', u'недолюблив')
    text = text.replace(u'Не долюблив', u'Недолюблив')
    return text

def postprocessing(text):
    text = return_line_feed(text)
    text = hypens(text)
    text = in_smbs_way(text)
    text = fused_and_separated(text)
    return text

#print in_smbs_way(text)
