# -*- coding: cp1251 -*-
#word = u'��������������'
def osw(word):
    if word[:6]== u'������':
        new_word = u'������' + word[6:]
        return new_word
    elif word == u'�����':
        new_word = u'�����'
        return new_word
    elif word == u'������':
        new_word = u'�����'
        return new_word
    elif word == u'�������':
        new_word = u'������'
        return new_word
    elif word == u'��������':
        new_word = u'�������'
        return new_word
    elif word[:7]== u'�������':
        new_word = u'��������' + word[7:]
        return new_word
    elif word == u'�����':
        new_word = u'����'
        return new_word
    elif word == u'�������':
        new_word = u'��������'
        return new_word
    elif word[:8]== u'��������':
        new_word = u'���������' + word[8:]
        return new_word
    elif word[:4] == u'����' and word != u'����':
        new_word = u'����' + word[4:]
        return new_word
    elif word[:9]== u'���������':
        new_word = u'����������' + word[9:]
        return new_word
    elif word[:6]== u'������':
        new_word = u'�����' + word[6:]
        return new_word
    elif word[:7]== u'�������':
        new_word = u'��������' + word[7:]
        return new_word
    else:
        return word

def old_prefix(word):
    if word[:7]== u'�������' and len(word) > 7:
        new_word = u'�������' + word[7:]
        return new_word
    else:
        return word

#print osw(word)
#print old_prefix(word)
