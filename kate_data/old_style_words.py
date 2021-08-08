# -*- coding: cp1251 -*-
#word = u'противустояние'
def osw(word):
    if word[:6]== u'сватьб':
        new_word = u'свадьб' + word[6:]
        return new_word
    elif word == u'отцем':
        new_word = u'отцом'
        return new_word
    elif word == u'найдти':
        new_word = u'найти'
        return new_word
    elif word == u'прийдти':
        new_word = u'прийти'
        return new_word
    elif word == u'перейдти':
        new_word = u'перейти'
        return new_word
    elif word[:7]== u'искуств':
        new_word = u'искусств' + word[7:]
        return new_word
    elif word == u'плечь':
        new_word = u'плеч'
        return new_word
    elif word == u'прогрес':
        new_word = u'прогресс'
        return new_word
    elif word[:8]== u'прогреси':
        new_word = u'прогресси' + word[8:]
        return new_word
    elif word[:4] == u'учон' and word != u'учон':
        new_word = u'учен' + word[4:]
        return new_word
    elif word[:9]== u'внимателн':
        new_word = u'внимательн' + word[9:]
        return new_word
    elif word[:6]== u'оффици':
        new_word = u'офици' + word[6:]
        return new_word
    elif word[:7]== u'симетри':
        new_word = u'симметри' + word[7:]
        return new_word
    else:
        return word

def old_prefix(word):
    if word[:7]== u'противу' and len(word) > 7:
        new_word = u'противо' + word[7:]
        return new_word
    else:
        return word

#print osw(word)
#print old_prefix(word)
