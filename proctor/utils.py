from wonderwords import RandomWord

r = RandomWord()

def generate_clientname():
    clientname = ".".join(r.random_words(3, word_max_length=10))
    return clientname
