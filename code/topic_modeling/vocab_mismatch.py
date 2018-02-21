import pickle
import warnings
import os
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim import corpora

'''
Calculates how many words in the test samples are actually covered by the dictionary (and thus known to the model)

Input:  ../../samples/*data-set*/*sample size*/*iteration*/model.dict
        ../../samples/*data-set*/*sample size*/*iteration*/*group*_test.mm

Output: ../../samples/*data-set*/*sample size*/*iteration*/eval/mismatch_a.p
        ../../samples/*data-set*/*sample size*/*iteration*/eval/mismatch_b.p
'''

def vocab_mismatch(a_sample, b_sample, path, namespace):
    tag_coll_a = namespace["tag_coll_a"]
    tag_coll_b = namespace["tag_coll_b"]

    # Go up one directory for seed and text corpus
    corpus_path = "/".join(path.split("/")[:-2]) + "/"

    # Load test document Lookups
    with open(corpus_path + tag_coll_a + "_test.p","rb") as f_a:
        a_test_dict = pickle.load(f_a)
    with open(corpus_path + tag_coll_b + "_test.p","rb") as f_b:
        b_test_dict = pickle.load(f_b)

    # Load dictionary + Get words that are known to the model
    dictionary = corpora.Dictionary.load(path + "model.dict")
    known_words = set(list(dictionary.values()))

    # Get documents per Group and count the percentage of unknown words in each document
    a_mismatch = []
    b_mismatch = []
    for a_doc in a_test_dict.values():
        doc_length = len(a_doc)
        unknown_words = 0
        for word in a_doc:
            if word not in known_words:
                unknown_words+=1
        if doc_length>0:
            a_mismatch.append(unknown_words/doc_length)

    for b_doc in b_test_dict.values():
        doc_length = len(b_doc)
        unknown_words = 0
        for word in b_doc:
            if word not in known_words:
                unknown_words += 1
        if doc_length > 0:
            b_mismatch.append(unknown_words / doc_length)

    # Store Vocabulary Mismatch
    eval_path = path + "eval/"
    if not os.path.exists(eval_path):
        os.makedirs(eval_path)

    with open(eval_path+"mismatch_a.p","wb") as f_a:
        pickle.dump(a_mismatch,f_a)

    with open(eval_path+"mismatch_b.p","wb") as f_b:
        pickle.dump(b_mismatch,f_b)