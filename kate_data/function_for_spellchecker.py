


def load_model():
    data = read_corpus('/model/vocabulary.txt')
    V = Vocabulary(data)
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    model = CharLM(V.vocab_size, word_len=V.pad_len, emb_dim=128, hidden_size=64)
    model_filename = "/model/old_rus_lm.pth"
    model.load_state_dict(torch.load(model_filename, map_location={'cuda:0': 'cpu'}))
    correct = spellCorrect(V=V, model=model)
    return model


def check_p(d, corrected):
    p = d['p'].split('\n')
    p, corrected = '\n'.join(check(text, corrected) for text in p)
    d['p'] = p
    return d, corrected

corrected = []
