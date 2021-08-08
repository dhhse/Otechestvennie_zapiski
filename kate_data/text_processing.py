# -*- coding: cp1251 -*-
import re

#text = u'�� ������, �� ����������'

def pretreatment(text):
    text = text.replace(u'\r', u'/@/')
    return text

def hypens(text):
    text = text.replace(u'��� ������', u'���-������')
    text = text.replace(u'��� ������', u'���-������')
    text = text.replace(u'��� ������', u'���-������')
    text = text.replace(u'��� ������', u'���-������')
    text = text.replace(u'��� ������', u'���-������')
    text = text.replace(u'��� ������', u'���-������')
    text = text.replace(u'��-�������-����', u'�� ������� ����')
    text = text.replace(u'��-�������-����', u'�� ������� ����')
    return text

def change_reg(obj):
    word = obj.group()
    part = word[1:].lower()
    new_word = word[0] + part
    return new_word

def in_smbs_way(text):
    text = re.sub(ur'([��]�) ([�-��-�]*���)', u'\g<1>-\g<2>', text)
    text = re.sub(ur'([��]�-[�-��-�]*���)', change_reg, text)
    return text

def return_line_feed(text):
    text = text.replace(u' /@/ ', u'\r')
    text = text.replace(u'/@/ ', u'\r')
    text = text.replace(u' /@/', u'\r')
    text = text.replace(u'/@/', u'\r')
    return text

def fused_and_separated(text):
    text = text.replace(u'�� ��������', u'����������')
    text = text.replace(u'�� ��������', u'����������')
    return text

def postprocessing(text):
    text = return_line_feed(text)
    text = hypens(text)
    text = in_smbs_way(text)
    text = fused_and_separated(text)
    return text

#print in_smbs_way(text)
