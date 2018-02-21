import pickle
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim import corpora

'''
Creates the dictionary, training and test corpora based on the sample seed and the article sets.
Directly transforms them into market matrices such that they can be used by the LDA model.

Input:  ../../samples/*data-set*/*sample size*/*group*_training.p
        ../../samples/*data-set*/*sample size*/*group*_test.p

Output: ../../samples/*data-set*/*sample size*/*iteration*/*group*_training.mm
        ../../samples/*data-set*/*sample size*/*iteration*/*group*_test.mm
        ../../samples/*data-set*/*sample size*/*iteration*/all_test.mm
        ../../samples/*data-set*/*sample size*/*iteration*/model.dict
'''

class Document_Stream(object):
    # NOTE: Can't handle header lines right now
    def __init__(self,a_lookup, b_lookup, a_sample, b_sample, dictionary=None):
        self.a_lookup = a_lookup
        self.b_lookup = b_lookup
        self.sample = sorted(list(zip(["a"] * len(a_sample), a_sample)) +
                             list(zip(["b"] * len(b_sample), b_sample)), key= lambda x: x[1])
        self.dictionary = dictionary

    def __iter__(self):
        for group, pair_id in self.sample:
            if self.dictionary!=None:
                if group=="a":
                    yield self.dictionary.doc2bow(self.a_lookup[pair_id])
                else:
                    yield self.dictionary.doc2bow(self.b_lookup[pair_id])
            else:
                if group=="a":
                    yield self.a_lookup[pair_id]
                else:
                    yield self.b_lookup[pair_id]

def load_dictionary(path, training_stream, no_below, overwrite=False):
    dictionary = corpora.Dictionary(documents=training_stream)
    dictionary_pre = str(len(dictionary))
    dictionary.filter_extremes(no_below=no_below)
    dictionary_post = str(len(dictionary))
    print("Reduced dict: "+str(dictionary_pre)+" -> "+str(dictionary_post))
    dictionary.save(path+"model.dict")

    return dictionary


def text_to_matrix(a_sample, b_sample, path, namespace, no_below, overwrite=False):

    corpus_path = "/".join(path.split("/")[:-2]) + "/"
    tag_coll_a = namespace["tag_coll_a"]
    tag_coll_b = namespace["tag_coll_b"]

    with open(corpus_path + tag_coll_a + "_training.p","rb") as f_a:
        a_train_dict = pickle.load(f_a)
    with open(corpus_path + tag_coll_b + "_training.p","rb") as f_b:
        b_train_dict = pickle.load(f_b)

    with open(corpus_path + tag_coll_a + "_test.p","rb") as f_a:
        a_test_dict = pickle.load(f_a)
    with open(corpus_path + tag_coll_b + "_test.p","rb") as f_b:
        b_test_dict = pickle.load(f_b)

    # Load/create dictionary
    training_stream = Document_Stream(a_train_dict, b_train_dict, a_sample, b_sample)
    dictionary = load_dictionary(path,training_stream,no_below,overwrite=overwrite)

    # Translate training
    translated_training_stream = Document_Stream(a_train_dict, b_train_dict, a_sample, b_sample, dictionary=dictionary)
    corpora.MmCorpus.serialize(path + "training.mm", translated_training_stream)

    # Translate tests
    test_a_stream = Document_Stream(a_test_dict, dict(), a_sample, [], dictionary=dictionary)
    test_b_stream = Document_Stream(dict(), b_test_dict, [], b_sample, dictionary=dictionary)
    test_all_stream = Document_Stream(a_test_dict, b_test_dict, a_sample, b_sample, dictionary=dictionary)

    corpora.MmCorpus.serialize(path + namespace["tag_coll_a"] + "_test.mm", test_a_stream)
    corpora.MmCorpus.serialize(path + namespace["tag_coll_b"] + "_test.mm", test_b_stream)
    corpora.MmCorpus.serialize(path + "all_test.mm", test_all_stream)

    print("Finished: Building Dictionary and Transforming Test + Training Corpora on "+path)

