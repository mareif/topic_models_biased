import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim import corpora,models

'''
Trains a single LDA model

Input:  ../../samples/*data-set*/*sample size*/*iteration*/*group*_training.mm
        ../../samples/*data-set*/*sample size*/*iteration*/model.dict

Output: ../../samples/*data-set*/*sample size*/*iteration*/*model*.lda
'''

def train_lda(path,namespace, num_topics):
    # Load Training Corpus + Dictionary
    dictionary = corpora.Dictionary.load(path + "model.dict")
    training_corpus = corpora.MmCorpus(path+"training.mm")

    # Feed Training Corpus to HDP
    lda = models.LdaModel(training_corpus,num_topics=num_topics, id2word=dictionary)

    # Save Model
    lda.save(path+"model_"+str(num_topics)+".lda")

    print("Finished: Building LDA ("+str(num_topics)+") - "+path)


