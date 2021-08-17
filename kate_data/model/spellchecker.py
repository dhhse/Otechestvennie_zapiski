sys.path[0:0] = ['../model']
import pybktree
from Levenshtein import editops, distance
import pandas as pd
import re
from string import punctuation
from functools import reduce
from nltk import WordPunctTokenizer
from string import punctuation
from tqdm import tqdm_notebook as tqdm

import numpy as np
from collections import Counter

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as opt
from torch.utils.data.dataset import Dataset
from torch.utils.data.dataloader import DataLoader

from sklearn.utils import shuffle
import pandas as pd
import re

wpt = WordPunctTokenizer()

punct = punctuation+'«»—…“”*№–'

class CharDataset(Dataset):
    def __init__(self, data, V):
        super(Dataset).__init__()
        self.V = V
        self.chars = V.chars
        self.data = data
        self.pad_len = V.pad_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        word = self.data[idx]
        indices = self.V.transform_one(word)
        x = torch.ones((self.pad_len), dtype=torch.int64)
        y = torch.ones((self.pad_len), dtype=torch.int64)
        mask = torch.zeros((1,), dtype=torch.int64)
        word_len = min(len(indices), self.pad_len - 1)
        for idx_i, i in enumerate(indices[:word_len - 1]):
            x[idx_i + 1] = i

        for idx_i, i in enumerate(indices[:word_len]):
            y[idx_i] = i

        mask[0] = word_len + 1

        x[0] = self.V.char2idx["^"]
        y[word_len] = self.V.char2idx["$"]

        return x, y, mask

    def gen_input_tensor(self, letters):
        indices = self.V.transform_one(letters)
        tensor = torch.ones((self.pad_len), dtype=torch.int64)
        word_len = min(len(indices), self.pad_len)
        for idx_i, i in enumerate(indices[:word_len]):
            tensor[idx_i + 1] = i

        tensor[0] = 0

        return tensor

    def resized(self, new_size):
        return CharDataset(data=self.data[:new_size], V=self.V)

def read_corpus(file_path):
    """ Read file, where each word is dilineated by a `\n`.
    @param file_path (str): path to file containing vocabulary
    """
    vocabulary = open(file_path, 'r').read()
    data = [word for word in vocabulary.split('\n')]

    return data
    
device = torch.device('cpu')

def seq_prob(model, dataset, vocab):
    for i in range(len(dataset)):
        x, y, word_len = dataset[i]
        x = x.to(device)
        y = y.to(device)
        y_pred = model(x)[0]
        probs = []
        output = vocab.transform_vec(y[:word_len])
        for char_idx in range(1,word_len[0]):
            char = output[char_idx]
            if char=='<':
                break
            try:
                idx = vocab.char2idx[char]
            except KeyError:
                idx = vocab.char2idx["<unk>"]
            probs.append(y_pred[char_idx][idx])
        try:
            multiplication = reduce(lambda x, y: x*y, probs)
            final_prob = multiplied/word_len[0].float().to(device)
        except:
            final_prob = 1E-7 # костыль
        return final_prob
        
class CharLM(nn.Module):
    def __init__(self, vocab_size, emb_dim=27, hidden_size=128, n_layers=2, drop_prob=0.5, word_len=27):
        super(CharLM, self).__init__()
        self.vocab_size = vocab_size
        self.word_len = word_len
        self.emb_dim = emb_dim
        self.hidden_size = hidden_size
        self.n_layers=n_layers
        self.emb = nn.Embedding(vocab_size, emb_dim)
        self.lstm = nn.LSTM(self.emb_dim, hidden_size, num_layers=self.n_layers, batch_first=True) #,dropout=drop_prob)#, bidirectional=True)
        self.output = nn.Linear(in_features=self.word_len*self.hidden_size, out_features=self.vocab_size*word_len)
    
    def forward(self, input_word):
        # torch.Size([64, 27])
        embeded = self.emb(input_word).view(-1, self.word_len, self.emb_dim)
        # torch.Size([64, 27, 27]) or torch.Size([1, 27, 27])
        out, hidden = self.lstm(embeded)
        # torch.Size([64, 27, 1024])
        batch_size, seq_size, hidden_size = out.shape
        out = out.contiguous().view(batch_size, seq_size*hidden_size)
        # torch.Size([64, 13824])
        out = self.output(out).view(-1, self.word_len, self.vocab_size)
        # torch.Size([64, 27, 55])
        # final = F.softmax(out, dim=-1)
        # torch.Size([64, 27,55])
        return out
        
class Vocabulary:
    def __init__(self, data):
        self.AUXILIARY = ["^", "<pad>", "$", "<unk>"]
        self.data = data
        self.chars, self.char2idx, self.idx2char = self.fit(data)
        self.words, self.num_words = self.distinct_words(data)
        self.vocab_size = len(self.chars)
        self.pad_len = self.define_pad()
        
    def fit(self, data):
        """Extract unique symbols from the data, make itos (item to string) and stoi (string to index) objects"""
        chars = list(set(list(',-.0123456789í́абвгдеёжзийклмнопрстуфхцчшщъыьэюяіѣѳѵ') + \
                         [char for word in data for char in word if not self.not_russian(word)]))
        chars = self.AUXILIARY + sorted(chars)
        char2idx = {s: i for i, s in enumerate(chars)}
        idx2char = {i: s for i, s in enumerate(chars)}
        
        return chars, char2idx, idx2char
      
    def distinct_words(self, data):
        print('Estimating cospus size')
        counts = Counter(data)
        words = list(set([word for word in data if len(word)>4 and not self.not_russian(word)]))
        num_words = len(words)
        print('Done!')
        print('You can checkout the number of corpus words and the words themselves with commands .num_words, .words')
        return(words, num_words)

    def transform_all(self, words):
        """Transform list of data to list of indices
        Input:
            - data, list of strings
        Output:
            - list of lists of char indices
        """
        return [self.transform_one(word) for word in words]
    
    def transform_one(self, word):
        """Transform data to indices
        Input:
            - data, string
        Output:
            - list of char indices
        """
        return [self.char2idx[char] if char in self.chars else self.char2idx["<unk>"] for char in word.lower()]
    
    def transform_vecs(self, vecs):
        """Transform list of indices to list of data
        Input:
            - list of lists of char indices
        Output:
            - data, list of strings
        """
        return [self.transform_vec(vec) for vec in vecs]
    
    def transform_vec(self, vec):
        """Transform indices to data
        Input:
            - list of char indices
        Output:
            - data, string
        """
        return "".join([self.idx2char[int(idx)] for idx in vec])
      
    def define_pad(self):
      
        word_lens = [len(x) for x  in self.transform_all(self.words)]
        return(max(word_lens))
      
    def not_russian(self, string):
        s = re.sub("[.,:\'-]", '', string)
        charRe = re.compile(r'[a-zA-Z0-9.]')
        st = charRe.search(s)
        return bool(st) or bool(re.search(r'\d', s) or bool(re.search(r'[^a-zа-яё ]+', string)))
        
class probMaker(object):
    
    def __init__(self, error_df, counts):
        self.counts = counts
        self.error_df = error_df
        self.sub_mtrx, self.sub_labels = self.confusion_mtrx('replace')
        self.ins_mtrx, self.ins_labels = self.confusion_mtrx('insert')
        self.del_mtrx, self.del_labels = self.confusion_mtrx('delete')
        
    def P_w(self, w):
        '''Calculate P(word)'''
        N = sum(list(map(int,self.counts.values())))
        if w in self.counts:
            return (int(self.counts[w]) + 1) / (N + len(self.counts)) # лаплассовское сглаживание?
        else:
            return 1/(N + len(self.counts))

    def P_ew(self, editop, e, w):
        '''Calculate P(e|w)'''
        
        if editop=='replace':
            return self.check_cofusion_mtrx(self.sub_labels,self.sub_mtrx,e,w)
        elif editop=='insert':
            return self.check_cofusion_mtrx(self.ins_labels,self.ins_mtrx,e,w)
        elif editop=='delete':
            return self.check_cofusion_mtrx(self.del_labels,self.del_mtrx,e,w)
        else:
            return 0.0001 # костыль

    def check_cofusion_mtrx(self,labels,cm,e, w):
        if e in labels:
            if w in labels:
                e_idx = labels.index(e)
                w_idx= labels.index(w)
                return(cm[w_idx, e_idx]/(sum(cm[w_idx,:])))
        else:
            if w in labels:
                w_idx= labels.index(w)
                return(1/(sum(cm[:, w_idx])))
        return(1/(cm.shape[0]*cm.shape[1])) 

    def confusion_mtrx(self, editop):
        '''Building confusion matrices of the checked partition of data'''
        error_df = self.error_df       
        df = pd.concat([error_df[error_df['editop']==editop], \
                        error_df[error_df['editop']=='equal']], axis=0, ignore_index=True)
        correct_tokens = [list(word[:int(df.idxw.iloc[[i]])]) + \
                          [df['e|w'].iloc[[i]][i][df['e|w'].iloc[[i]][i].find('|')+1:]] + \
                          list(word[int(df.idxw.iloc[[i]]) + \
                                    len(df['e|w'].iloc[[i]][i][df['e|w'].iloc[[i]][i].find('|')+1:]):]) \
                          for i, word in enumerate(df['correction'].astype(str).tolist())]
               
        correct_elements = [el for token in correct_tokens for el in token if el]
               
        error_tokens = [list(word[:int(df.idxe.iloc[[i]])]) + \
                        [df['e|w'].iloc[[i]][i][:df['e|w'].iloc[[i]][i].find('|')]] + \
                        list(word[int(df.idxe.iloc[[i]])+len(df['e|w'].iloc[[i]][i][:df['e|w'].iloc[[i]][i].find('|')]):]) \
                        for i, word in enumerate(df['error'].astype(str).tolist())]
        error_elements = [el for token in error_tokens for el in token if el]
        return np.add(1, confusion_matrix(correct_elements, error_elements)),\
               sorted(list(set(correct_elements+error_elements))) # with smoothing

class spellCorrect(object):
    """A class to correct non-dictionary words in Google Ngrams using Noisy Channel Model, Error Confusion Matrix, Damerau-Levenshtein Edit Distance and a Char Language model to help define real-word non-dictionary tokens
Usage:
Input: 'астроном1я'
Response: астрономія"""
    def __init__(self, V=None, model=None):
        """Constructor method to load external probMaker class, load dictionary and words counts """
        self.vocab = self.load_vocab()
        self.counts = self.load_counts()
        self.trie = pybktree.BKTree(distance, self.vocab)
        self.error_df = self.load_error_df()
        self.pm = probMaker(self.error_df, self.counts)
        self.V = V
        self.model = model
    
    def load_vocab(self):
        """Method to load dictionary from external data file."""
        print ("Loading dictionary from data file")
        vocabulary = open('vocabulary.txt', 'r').read()  # pre-reform word forms
        return list(set([word.lower() for word in vocabulary.split("\n") if len(word)>4]))

    def load_counts(self):
        """Method to load counts from external data file."""
        print("Loading counts")
        counts = {}
        lines = open('counts.txt', 'r').read().split("\n")
        for line in lines:
            if line:
                l = line.split()
                if len(l) > 1:
                    key, value = l[0],l[1]
                    counts[key] = value
        return counts

    def load_error_df(self):
        """Method to load a dataframe containing  from external data file."""
        print("Loading error dataframe")
        error_df = pd.read_csv('error_df.csv', error_bad_lines=False)
        return error_df

    def gen_candidates(self, word):
        """Method to generate set of candidates for a given word using Damerau-Levenshtein Edit Distance of 1 and 2"""
        return self.trie.find(word.lower(), 2)
    
    def get_best(self, error):
        """Method to calculate channel model probability for errors."""
        candidates = self.gen_candidates(error.lower())
        p = [0]*len(candidates)
        for i, candidate_ in enumerate(candidates):
            candidate = candidate_[-1]
            p_ew_candidate = []
            for res in editops(candidate,error):
                editop, w_idx, e_idx = res
                if editop == 'replace':
                    e=error[e_idx]
                    w=candidate[w_idx]
                elif editop == 'insert':
                    e=error[e_idx-1:e_idx+1]
                    w=candidate[w_idx-1]
                elif editop == 'delete':
                    if e_idx!=0:
                        e=error[e_idx-1]
                        w=candidate[w_idx-1:w_idx+1]
                    else:
                        e=error[e_idx]
                        w=candidate[w_idx:w_idx+2]
                else:
                    print(editops(candidate,error))
                    return error 
                p_ew_candidate.append(self.pm.P_ew(editop,e,w))
            if p_ew_candidate:
                p[i] = self.pm.P_w(candidate)*reduce(lambda x, y: x*y, p_ew_candidate)/len(p_ew_candidate)
            else:
                return error
        try:    
            best_idx = p.index(max(p))
            return(candidates[best_idx][-1])
        except ValueError:
            return error
            print(editops(candidate,error))


    def to_check(self, string, seqprob, upper_boundary=0, lower_boundary=0):
        '''Rid of non-cyrilic words, 
        words with len < 5, 
        dictionary words 
        and words with probability>? of being a non-error word given by the language model'''

        if len(string)<5:
            return string
        # alphanumeric words stay the same
        s = re.sub("[.,:\'-]", '', string)
        charRe = re.compile(r'[^a-zA-Z0-9.]')
        st = charRe.search(s)

        if not bool(st):
            return string
        else:
            # vocab words stay the same
            if self.trie.find(s.lower(), 0):
                return string
            else:
                if upper_boundary>0 and lower_boundary>0:
                    if not seqprob:
                        dataset = CharDataset([string], V=self.V)
                        seqprob = seq_prob(self.model, dataset, self.V)
                        
                    if seqprob<=upper_boundary or seqprob>=lower_boundary:
                        self.correction = self.return_upper(self.get_best(string),string)
                        return self.correction
                    else:
                        self.correction = self.return_upper(self.get_best(string),string)
                        if self.rules(self.correction, string):
                            return self.correction
                        else:
                            return string
                else:
                    return self.return_upper(self.get_best(string),string)


    def return_upper(self,w,e):
        if e.isupper():
            return w.upper()
        else:
            if e[0].isupper():
                return w[0].upper()+w[1:]
            else:
                return w


    def rules(self, w, e):
        if len(e)>4:
            rule1 = e[-1] in 'шщцЦШЩ'
            rule2 = any(i.isdigit() for i in e)
            rule3 = e[-2] in 'щшцЩШЦ' and e[-1] in 'июяИЮЯ'
            rule4 = 'ѣ' or 'Ѣ'  in w
            if rule1 or rule2 or rule3 or rule4:
              return True
        return False


def check(text):
    text = wpt.tokenize(text)
    corrected_text = []
    corrected = {}
    for word in text:
        if word in corrected:
            corrected_text.append(' ' + corrected[word])
        elif word in punct and word not in """“<«[(""":
            corrected_text.append(word)
        else:
            new_word = correct.to_check(word, seqprob=False)
            corrected_text.append(' ' + new_word)
            corrected[word] = new_word
    return ''.join(corrected_text)


    
    
