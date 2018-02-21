import os
import pickle

from code.helper import load_namespace
from code.topic_modeling.text_to_matrix import text_to_matrix
from code.topic_modeling.train_lda import train_lda
from code.topic_modeling.vocab_mismatch import vocab_mismatch
from code.topic_modeling.eval_lda import eval_lda

'''
Build and Evaluate all desired LDA topic models for one sample seed

Input:  ../../samples/*data-set*/*sample size*/*iteration*/sample_seed.p
        ../../samples/*data-set*/*sample size*/*iteration*/*group*_training.tsv
        
Output: ../../samples/*data-set*/*sample size*/*iteration*/*relative_size*/*everything* (multiple)
'''

def seed_to_sample_ids(seed_path, relative_size):
    with open(seed_path + "sample_seed.p","rb") as f_seed:
        seed = pickle.load(f_seed)

    split_threshold = int(len(seed)*relative_size)
    a_sample = seed[:split_threshold]
    b_sample = seed[split_threshold:]
    print("Adjusted Seed Threshold for: "+seed_path)
    return sorted(a_sample), sorted(b_sample)

def build_one_sample(relative_size, sample_size, path, namespace, num_topics, overwrite=False, ds_lock=None):

    # Go up one directory for seed and text corpus
    seed_path = "/".join(path.split("/")[:-2]) + "/"

    # Load Seed and adjust to relative size
    a_sample, b_sample = seed_to_sample_ids(seed_path, relative_size)
    assert(len(a_sample) / (len(a_sample) + len(b_sample)) < relative_size + 0.01 and
           len(a_sample) / (len(a_sample) + len(b_sample)) > relative_size - 0.01)

    # Get data from sample corpus and build Traings and Test Corpora
    if ds_lock:
        ds_lock.acquire()
    text_to_matrix(a_sample, b_sample, path, namespace, no_below=int(max(5,sample_size*0.001)), overwrite=overwrite)
    if ds_lock:
        ds_lock.release()

    # Calculate Vocabulary mismatch
    vocab_mismatch(a_sample, b_sample, path, namespace)

    # Train Model
    # train_hdp(path, namespace)
    for number_of_topics in num_topics:
        train_lda(path, namespace, num_topics=number_of_topics)

    # Evaluate Model
    # eval_hdp(path, sample_size, namespace)
    for number_of_topics in num_topics:
        eval_lda(path, sample_size, namespace, num_topics=number_of_topics)


if __name__=="__main__":
    relative_size = 0.5
    sample_size = 1000
    iteration = 1
    namespace = load_namespace("wiki")
    overwrite=True

    path = "../../samples/"+namespace["global_namespace"]+"/"+str(sample_size)+"/"+str(iteration)+"/"+str(int(relative_size*100))+"/"
    if not os.path.exists(path):
        os.makedirs(path)

    build_one_sample(relative_size, sample_size, path, namespace, num_topics=[128], overwrite= overwrite)