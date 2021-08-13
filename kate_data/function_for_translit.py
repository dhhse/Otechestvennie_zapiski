from transliterator.translit import translit_text


def translit(text):
    tokens = translit_text(text)
    new_text = ''
    for token in tokens:
        new_text = new_text + token.punct_prev +\
            token.word + token.punct_next + ' '
    return new_text