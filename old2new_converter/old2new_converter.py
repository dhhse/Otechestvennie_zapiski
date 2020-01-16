# -*- coding: utf-8 -*-
import codecs
import os
import sys
import re
import Tkinter as tk
from tkMessageBox import askyesno
from tkFileDialog import askopenfilename
from lxml import etree
import HTMLParser
from flask import Flask, render_template, request, make_response
from werkzeug import secure_filename
import rules
import old_style_words
import text_processing

app = Flask(__name__)


#signs = [u'!', u'?', u',', u'.', u':', u')', u'(', u'«', u'»', u'“', u'”', u'-', u'–',u'`', u';', u'\\', u'/', u'@', u'"', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'0', u' ']

signs = [u'!', u'?', u',', u'.', u':', u')', u'(', u'«', u'»', u'“', u'”', u'-', u'–',u'`', u';', u'\\', u'/', u'@', u'"', u' ', u'<', u'>']


prefix = [u'воз', u'вз', u'низ', u'из', u'раз', u'роз', u'без', u'через', u'чрез']

unvoiced_cons = [u'п', u'т', u'к', u'ф', u'с', u'ц', u'ч', u'щ', u'ш', u'х']

particles = [u'б', u'бы', u'ль', u'ли', u'же', u'ж', u'ведь', u'вот', u'мол', u'даже', u'дескать', u'вот', u'будто']


class Token:
    def __init__(self, word):
        self.word = word
        self.old_word = ''
        self.lemma = ''
        self.punct_prev = ''
        self.punct_next = ''

class Meta:
    def __init__(self):
        self.flag = 0
        self.res = ''
        self.log = ''
        self.filename = ''

meta = Meta()

##########TRANSLITERATOR##########

def is_roman_numeral(word):
    is_RN = 1
    for i in word:
        if i == u'i' or i == u'I':
            pass
        elif i == u'v' or i == u'V':
            pass
        elif i == u'x' or i == u'X':
            pass
        elif i == u'l' or i == u'L':
            pass
        elif i == u'c' or i == u'C':
            pass
        elif i == u'd' or i == u'D':
            pass
        elif i == u'm' or i == u'M':
            pass
        else:
            return 0
    return is_RN

def is_foreign(word):
    n = 0
    alphabet = [u'a', u'b', u'c', u'd', u'e', u'f', u'g', u'h', u'i', u'j', u'k', u'l', u'm', u'n', u'o', u'p', u'q', u'r', u's', u't', u'u', u'v', u'w', u'x', u'y', u'z']
    word = word.lower()
    for i in word:
        if i in alphabet:
            n = n + 1

    if len(word)/2 <= n:
        return 1
    else:
        return 0

def signs_end(word):
    prev = True
    end_signs = u''
    for i in range(len(word)):
        if len(word) == len(end_signs):
            return word, u''
        if word[-i-1] in signs and prev == True:
            end_signs += word[-i-1]
            prev = False
        elif word[-i-1] in signs and prev == False:
            end_signs += word[-i-1]
            if len(word) == len(end_signs):
                return word, u''
        elif word[-i-1] not in signs and prev == False:
            new_word = word[:-i]
            end_signs = end_signs[::-1]
            return new_word, end_signs
        else:
            end_signs = end_signs[::-1]
            return word, end_signs
    

def signs_begin(word):
    prev = True
    begin_signs = u''
    for i in range(len(word)):
        if len(word) == len(begin_signs):
            return word, u''
        elif word[i] in signs and prev == True:
            begin_signs += word[i]
            prev = False
        elif word[i] in signs and prev == False:
            begin_signs += word[i]
            if len(word) == len(begin_signs):
                return word, u''
        elif word[i] not in signs and prev == False:
            new_word = word[i:]
            #print 0
            return new_word, begin_signs
        else:
            #print 00
            return word, begin_signs

def word_checking(word):
    
    if len(word) < 1:
        return u''
    begin_signs = u''
    end_signs = u''
    new_word = u''
    begin = True

    try:
        word, end_signs = signs_end(word)
        #print word, end_signs, '**'
    except:
        #print 'end', word
        pass
    try:
        word, begin_signs = signs_begin(word)
    except:
        #print 'begin', word
        pass

    capitals = []
    j = 0

    for i in range(len(word)):

        if word[i] != u'Ъ' and word[i] != u'ъ':
            
            j += 1
            if word[i].isupper():
                capitals.append(j - 1)

    if is_roman_numeral(word) or is_foreign(word):
        return word, begin_signs, end_signs

    old = word

    word = word.lower()
    
    if word == u'ея':
        word = u'её'
    
    elif word == u'нея':
        word = u'неё'

    elif word == u'онѣ':
        word = u'они'

    elif word == u'однѣ':
        word = u'одни'
    
    elif word == u'однѣхъ':
        word = u'одних'

    elif word == u'однѣмъ':
        word = u'одним'

    elif word == u'однѣми':
        word = u'одними'

    if word[-1] != u']':
    
        if word[-1] == u'ъ':
            word = remove_er_end(word)

        if word[-1] == u'ъ':
            word = remove_er_end(word)
    else:
        if word[-2] == u'ъ':
            word = word[:-2] + word[-1]

        if word[-2] == u'ъ':
            word = word[:-2] + word[-1]
            
        if word[-2] == u'?':
            if word[-3] == u'ъ':
                word = word[:-3] + word[-2:]
            if word[-3] == u'ъ':
                word = word[:-3] + word[-2:]

    try:
        if word[-3:] == u'[?]':
            if word[-4] == u'ъ':
                word = word[:-4] + word[-3:]

            if word[-4] == u'ъ':
                word = word[:-4] + word[-3:]
    except:
        pass
            

    if u'ѣ' in word:
        word = replace_yat(word)

    if u'ѳ' in word:
        word = replace_fita(word)

    if word[-3:] in [u'аго', u'яго']:
        word = replace_adj_end(word)
    elif word[-2:] == u'ыя':
        word = replace_end_1(word)


    if re.search(u'ъи', word):
        word = word.replace(u'ъи', u'ы')

    if re.search(u'чьк', word):
        word = word.replace(u'чьк', u'чк')

    if re.search(u'чьн', word):
        word = word.replace(u'чьн', u'чн')

    
    if u'і' in word[:-2]:
        word = word.replace(u'і', u'и')

    if re.search(u'і', word[:-2]):
        ar = word[:-2].split(u'і')
        word = u'и'.join(ar) + word[-2:]       

    if word[-2:] == u'ія':      
        word = rules.ends_ie(word)

    if re.search(u'ій', word):
        ar = word.split(u'і')
        word = u'и'.join(ar)
        
    if re.search(u'іе', word):
        ar = word.split(u'і')
        word = u'и'.join(ar)

    if re.search(u'іи', word):
        ar = word.split(u'і')
        word = u'и'.join(ar)

    if re.search(u'ію', word):
        ar = word.split(u'і')
        word = u'и'.join(ar)
        
    if re.search(u'і', word):
        ar = word.split(u'і')
        word = u'и'.join(ar)


    if u'і' in word[:-2]:
        word = word.replace(u'і', u'и')
        

    if re.search(u'і', word[:-2]):
        ar = word[:-2].split(u'і')
        word = u'и'.join(ar) + word[-2:]
        

    if word[-2:] == u'ія':      
        word = rules.ends_ie(word)


    if re.search(u'ій', word):
        ar = word.split(u'і')
        word = u'и'.join(ar)
    

    if re.search(u'іе', word):
        ar = word.split(u'і')
        word = u'и'.join(ar)
    

    if re.search(u'іи', word):
        ar = word.split(u'і')
        word = u'и'.join(ar)
        

    if re.search(u'ію', word):
        ar = word.split(u'і')
        word = u'и'.join(ar)
        

    if re.search(u'і', word):
        ar = word.split(u'і')
        word = u'и'.join(ar)


    if u'i' in word[:-2]:
        word = word.replace(u'i', u'и')
        

    if re.search(u'i', word[:-2]):
        ar = word[:-2].split(u'i')
        word = u'и'.join(ar) + word[-2:]
        

    if word[-2:] == u'iя':      
        word = rules.ends_ie(word)


    if re.search(u'iй', word):
        ar = word.split(u'i')
        word = u'и'.join(ar)
    

    if re.search(u'iе', word):
        ar = word.split(u'i')
        word = u'и'.join(ar)
    

    if re.search(u'iи', word):
        ar = word.split(u'i')
        word = u'и'.join(ar)
        

    if re.search(u'iю', word):
        ar = word.split(u'і')
        word = u'и'.join(ar)
        5

    if re.search(u'i', word):
        ar = word.split(u'i')
        word = u'и'.join(ar)

    if word[-3:] == u'щию':      
        word = word[:-3] + u'щью'

    if re.search(u'[А-Я]*[а-я]*ияся', word):
        word = word.replace(u'ияся', u'иеся')

    
    word = rules.sse(word)
    word = rules.verbs_shol(word)
    word = rules.adjs_ija(word)
    word = old_style_words.osw(word)
    word = old_style_words.old_prefix(word)
    word = replace_prefix(word)


    for i in range(len(word)):
        if i in capitals:
            word = u''.join([word[:i], word[i].capitalize(), word[(i + 1):]])
           
    #return word, u''.join([begin_signs, word, end_signs])
    return word, begin_signs, end_signs, old

def remove_er_end(word):
    return word[:-1]

def replace_i_mid(word):
    word = word.replace(u'і', u'и')
    return word

def replace_yat(word):
    word = word.replace(u'ѣ', u'е')
    return word

def replace_fita(word):
    word = word.replace(u'ѳ', u'ф')
    return word
            
def replace_adj_end(word):
    exclusion_1 = [u'благо', u'люмбаго', u'маго', u'саго']
    exclusion_2 = [u'чужаго',u'пребольшаго']
    adj_lett_4 = [u'ч', u'щ', u'ж', u'ш']
    
    if word in exclusion_1:
        return word
    
    if word in exclusion_2:
        return u''.join([word[:-3], u'ого'])
    elif len(word) > 3 and word[-4] in adj_lett_4:
        return u''.join([word[:-3], u'его'])

    if word[-3:] == u'аго':
        return u''.join([word[:-3], u'ого'])
    elif word[-3:] == u'яго':
        return u''.join([word[:-3], u'его'])
    return word
    
def replace_end_1(word):
    return u''.join([word[:-2], u'ые'])

def replace_prefix(word):
    if word[:5] == u'восем' or word == u'восвояси' or u'низк' in word or u'низш' in word or u'возк' in word:
        return word
    
    for i in prefix:
        if word.find(i) == 0:
            if len(i) < len(word) and word[len(i)] in unvoiced_cons:
                return u''.join([word[:(len(i) - 1)], u'с', word[len(i):]])
    return word

def ends(word):
    i = 0
    e = 0
    for n in word:
        if n.isalpha():
            i = i + 1
        else:
            e = i
            return e

def get_word_without_signs(word):
    
    if len(word) < 1:
        return u''
    begin_signs = u''
    end_signs = u''
    begin = True
    try:
        word, end_signs = signs_end(word)
    except:
        #print 'end', word
        pass
    try:
        word, begin_signs = signs_begin(word)
    except:
        #print 'begin', word
        pass

    capitals = []
    j = 0

    for i in range(len(word)):       
        if word[i] != u'Ъ' and word[i] != u'ъ':
            j += 1
            if word[i].isupper():
                capitals.append(j - 1)

    if is_roman_numeral(word) or is_foreign(word):
        return word

    return word

def return_brackets(word, new):
    word_list = list(word)
    new_list = list(new)

    if word_list[0] == u'[' and word_list[len(word_list)-1] == u']':
        new_bracketed = u'[' + new + u']'

    else:
        if word_list[len(word_list)-1] == u']':
            new_list.append(u']')
        if word_list[0] == u'[':
            new = u'[' + new
            new_list = list(new)

        new_bracketed = []
        i = 0
        j = 0
        for a in word_list:
            if i == len(word_list):
                break
            if word_list[i] == u']' and j == len(new_list):
                    new_bracketed.append(u']')
                    break
            elif j == len(new_list):
                break
            else:

                if word_list[i] == u'ъ' and new_list[j] != word_list[i]:
                    i = i + 1

                if word_list[i] == new_list[j] == u']' or word_list[i] == new_list[j] == u'[':
                    new_bracketed.append(new_list[j])
                    i = i + 1
                    j = j + 1
                    pass
                else:
                    if word_list[i] == new_list[j] and word_list[i] != u'[' and word_list[i] != u']':
                        new_bracketed.append(new_list[j])
                        i = i + 1
                        j = j + 1
                    else:
                        if word_list[i] == u'[':
                            new_bracketed.append(u'[')
                            i = i + 1
                        elif word_list[i] == u']':
                            new_bracketed.append(u']')
                            i = i + 1
                        else:
                            new_bracketed.append(new_list[j])
                            i = i + 1
                            j = j + 1
                    if len(word_list) == i:
                            break
        

    return ''.join(new_bracketed)

def translit_bracketed(word):
    plain_word = ''
    punct_prev = ''
    punct_next = ''
    try:
        word, punct_prev = signs_begin(word)
        word, punct_next = signs_end(word)
    except:
        pass
    
    plain_word = word.replace(u'[', u'')
    plain_word = plain_word.replace(u']', u'' )

    translit_word = check_translit(plain_word)
    plain_new = text_processing.postprocessing(translit_word)

    new = return_brackets(word, plain_new)

    return new, word, punct_prev, punct_next

    

def check_translit(i):

    translit_word = u''
    it = 0
    for k in i.split(u'-'): #'lo'-'lo,,,'-'lo'
                    it = it + 1
                    #print k
                    result = word_checking(k) #result = 'lo', '', ',,,'
                    #print result
                    if len(result) == 0: #??
                        result = [u'', u'', u'']
                    transliteration = result[0] #or 1? lo

                    if result[2] == u'.' and it != len(i.split(u'-')):
                        transliteration = transliteration + result[2]
                    
                    if translit_word == u'':
                        translit_word += transliteration #word
                    else:
                        if result[0] in particles: # space if part
                            translit_word += u' '
                        else:
                            if k != '':
                                translit_word += u'-' # or
                        #print translit_word
                        translit_word += transliteration # add new part
    return translit_word

def translit_plain(i):
    translit_word = u''
    translit_word = check_translit(i)
    word = text_processing.postprocessing(translit_word)
    old = ''
    try:
        old, punct_prev = signs_begin(i)
        old, punct_next = signs_end(old)
    except:
        pass
    
    return word, old, punct_prev, punct_next

def translit_text(in_text):

    new_text = u''
    changes = u''

    in_text = text_processing.pretreatment(in_text)

    tokens = []
        
    for i in in_text.split():
            
            translit_word = u''
            punct_prev = u''
            punct_next = u''
            
            if u'[' in i or u']' in i:
                word, old, punct_prev, punct_next = translit_bracketed(i)
            else:
                word, old, punct_prev, punct_next = translit_plain(i)

            
            token = Token(word)

            if word != old:
                if u'/@/' not in old:
                    token.old_word = old
    
            new_text += translit_word
            new_text += u' '
     
            token.punct_prev = punct_prev
            token.punct_next = punct_next

            tokens.append(token)

        
    new_text = text_processing.postprocessing(new_text) # !!!

    return tokens

##########INTERFACE##############

def clean_html(line):
    line = line.replace(u'&nbsp;', u' ')
    line = line.replace(u'&quot;', u'"')
    #line = line.replace(u'&lt;', u'\<')
    #line = line.replace(u'&gt;', u'\>')
    line = line.replace(u'&ndash;', u'-')
    line = line.replace(u'&ndash;', u'-')
    return line

def get_temp(content):
    suffix = os.path.splitext(meta.filename)[1]
    temp_name = 'temp' + suffix
    with codecs.open(temp_name, 'w', 'utf-8') as temp:
        for line in content:
            new_line = clean_html(line)
            temp.write(new_line)
    return temp_name

def extra():
    text = u''
    tokens = translit_text(text)
    new_text = ''
    for token in tokens:
        if token.old_word != '':
            new_text = new_text + token.punct_prev + '<choice><reg>' +\
                token.word + '</reg><orig>' + token.old_word + '</orig></choice>'\
                + token.punct_next + ' '
        else:
            new_text = new_text + token.punct_prev +\
            token.word + token.punct_next + ' '
    new_text.rstrip()
    print new_text
    print ('*******************')

#extra()

def translit_xml(show, content, left_n, right_n, left_o, right_o):
            temp_filename = get_temp(content)                   
            #tree = etree.parse(meta.filename)
            tree = etree.parse(temp_filename)
            root = tree.getroot()
            log_arr = []
            markers = u'іѣъiѢЪIѣъѣіі'
            for child in root.iter():
                        #print child.tag, '&&&', child.text, '*****\n', child.tail, '^^^^^\n'
                        try:
                                if u'i' in child.text or u'I' in child.text or u'і' in child.text or u'ѣ' in child.text or u'Ѣ' in child.text or u'ъ' in child.text or u'Ъ' in child.text or u'ѣ' in child.text or u'і' in child.text:
                                    old = child.text
                                    tokens = translit_text(child.text)
                                    new_text = ''
                                    if show:
                                        for token in tokens:
                                            if token.old_word != '':
                                                #print token.old_word
                                                new_text = new_text + token.punct_prev + left_n +\
                                                    token.word + right_n + left_o + token.old_word + right_o\
                                                    + token.punct_next + ' '
                                                log_str = token.word + '  <--  ' + token.old_word + '\n'
                                                log_arr.append(log_str)
                                                #print new_text
                                            else:
                                                new_text = new_text + token.punct_prev +\
                                                    token.word + token.punct_next + ' '
                                    else:
                                        for token in tokens:
                                                new_text = new_text + token.punct_prev +\
                                                    token.word + token.punct_next + ' '

                                    new_text.rstrip()
                                    child.text = new_text
                        except:
                            pass
                        try:
                                #for marker in markers:
                                if u'i' in child.tail or u'I' in child.tail or u'і' in child.tail or u'ѣ' in child.tail or u'Ѣ' in child.tail or u'ъ' in child.tail or u'Ъ' in child.tail or u'ѣ' in child.tail or u'і' in child.tail:
                                    old = child.tail
                                    tokens = translit_text(child.tail)
                                    new_text = ''
                                    if show:
                                        for token in tokens:
                                            if token.old_word != '':
                                                #print token.old_word
                                                new_text = new_text + token.punct_prev + left_n +\
                                                    token.word + right_n + left_o + token.old_word + right_o\
                                                    + token.punct_next + ' '
                                                log_str = token.word + '  <--  ' + token.old_word + '\n'
                                                log_arr.append(log_str)
                                                #print new_text
                                            else:
                                                new_text = new_text + token.punct_prev +\
                                                    token.word + token.punct_next + ' '
                                    else:
                                        for token in tokens:
                                                new_text = new_text + token.punct_prev +\
                                                    token.word + token.punct_next + ' '            
                                    new_text.rstrip()
                                    child.tail = new_text
                        except:
                            pass
                            
                
            new_text = etree.tostring(root)

            #new_text = new_text.replace('&lt;', '<')
            #new_text = new_text.replace('&gt;', '>')

            h = HTMLParser.HTMLParser()
            new_text = h.unescape(new_text)

            return new_text

def load_html():
    if askyesno(u"Открыть файл", u"Открыть новый файл?"):
        meta.filename = askopenfilename()
        text.config(state = 'normal')
        text.delete("1.0", "end")
        text.insert("end", u"В обработке...\n")
        text.config(state = 'disabled')
        #print meta.filename
        name = os.path.splitext(os.path.basename(meta.filename))[0]
        #print meta.res
        if meta.filename == '':
            text.config(state = 'normal')
            text.delete("1.0", "end")
            text.insert("end", u"Пожалуйста, выберите файл.\n")
            text.config(state = 'disabled')
        else:

            new_text = translit_xml(1, '<choice><reg>', '</reg>', '<orig>', '</orig></choice>')


            suffix = os.path.splitext(meta.filename)[1]

            #meta.res = name + '_transliterated.html'
            meta.res = name + '_transliterated' + suffix
            
            with codecs.open(meta.res, 'w', 'utf-8') as inf:
                inf.write(new_text)

            log_name = name + '_log.txt'
            with codecs.open(log_name, 'w', 'utf-8') as logf:
                for el in log_arr:
                    logf.write(el)
            
            

def get_new_text(tokens):
    new_text = ''
    for token in tokens:
        new_text = new_text + token.punct_prev + token.word + token.punct_next + ' '
    new_text.rstrip()
    return new_text

def get_new_text_both(tokens, left_n, right_n, left_o, right_o):
    new_text = ''
    for token in tokens:
        if token.old_word != '':
            new_text = new_text + token.punct_prev + left_n + token.word + right_n + left_o + token.old_word + right_o + token.punct_next + ' '
        else:
            new_text = new_text + token.punct_prev + token.word + token.punct_next + ' '
    new_text.rstrip()
    return new_text

#@app.route('/')
def index():
    new_text = ''
    input_text = ''
    return render_template("old2new_converter.html", output_text = new_text, input_text = input_text)

@app.route("/", methods=['GET', 'POST'])
def web_converter():
    #filename = request.values.get('filename')
    #text = read_file(fname)
    input_text = ''
    output_text = ''
    new_text = ''
    
    if request.method == 'POST':
        input_text = request.values.get('inp_text')
        #app.logger.info(input_text)
        both = request.form.getlist('both')
        if 'go' in request.values:
            #if 'go' in request.args:
            tokens = translit_text(input_text)
            new_text = ''
            if 'show' in both:
                new_text = get_new_text_both(tokens, '', '', '{', '}')
            else:
                new_text = get_new_text(tokens)
        if 'clean' in request.values:
            #if 'clean' in request.args:
            input_text = ''
            output_text = ''

        if 'download_txt' in request.values:
            #if 'download_txt' in request.args:
            ftxt = request.files['f_txt']
            filename = secure_filename(ftxt.filename)
            meta.filename = filename
            text = ftxt.read().decode('utf-8')
            tokens = translit_text(text)
            if 'show' in both:
                new_text_txt = get_new_text_both(tokens, '', '', '{', '}')
            else:
                new_text_txt = get_new_text(tokens)
            name = os.path.splitext(meta.filename)[0]
            suffix = os.path.splitext(meta.filename)[1]
            command = "attachment; filename=" + name + "_transliterated" + suffix
            response = make_response(new_text_txt)
            response.headers["Content-Disposition"] = command
            return response

        if 'download_xml' in request.values:
            #if 'download_xml' in request.args:
            fxml = request.files['f_xml']
            filename = secure_filename(fxml.filename)
            meta.filename = filename
            text = fxml.read().decode('utf-8')
            
            if 'show' in both:
                new_text_xml = translit_xml(1, text, '<choice><reg>', '</reg>', '<orig>', '</orig></choice>')
            else:
                new_text_xml = translit_xml(0, text, '', '', '', '')
            name = os.path.splitext(meta.filename)[0]
            suffix = os.path.splitext(meta.filename)[1]
            command = "attachment; filename=" + name + "_transliterated" + suffix
            response = make_response(new_text_xml)
            response.headers["Content-Disposition"] = command
            return response

                
        return render_template("old2new_converter.html", output_text = new_text, input_text = input_text)
            

    
    
    return render_template("old2new_converter.html", output_text = new_text, input_text = input_text)






if __name__ == '__main__':

    #app.run(host='0.0.0.0', port=2031, debug=True)
    app.run(debug=True)
    

