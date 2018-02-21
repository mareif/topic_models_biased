import os
import pickle
import warnings

'''
Evaluates a single LDA model using the test documents.
Stores: Perplexity, Inference (for A,B,Complete test corpus)

Input:  ../../samples/*data-set*/*sample size*/*iteration*/*group*_test.mm
        ../../samples/*data-set*/*sample size*/*iteration*/all_test.mm
        ../../samples/*data-set*/*sample size*/*iteration*/*model*.lda

Output: ../../samples/*data-set*/*sample size*/*iteration*/eval/*eval data*
'''

warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim import corpora,models

from code.helper import *

import multiprocessing as mp
from datetime import datetime


def eval_lda(path, sample_size, namespace, num_topics):
    # Init Eval Directory
    eval_path = path + "eval/"
    if not os.path.exists(eval_path):
        os.makedirs(eval_path)

    # Load Test Corpora
    test_corpus_a = corpora.MmCorpus(path + namespace["tag_coll_a"] + "_test.mm")
    test_corpus_b = corpora.MmCorpus(path + namespace["tag_coll_b"] + "_test.mm")
    test_corpus_all = corpora.MmCorpus(path + "all_test.mm")

    # Load Model
    lda = models.LdaModel.load(path+"model_"+str(num_topics)+".lda")

    # Calculate Inference
    lda_inference_a = lda.inference(test_corpus_a)
    lda_inference_b = lda.inference(test_corpus_b)
    lda_inference_all = lda.inference(test_corpus_all)

    # Calculate Perplexity
    adj_lda_perplex_a = lda.log_perplexity(test_corpus_a, total_docs = sample_size)
    adj_lda_perplex_b = lda.log_perplexity(test_corpus_b, total_docs = sample_size)
    adj_lda_perplex_all = lda.log_perplexity(test_corpus_all, total_docs = sample_size)

    # Store Inference
    with open(eval_path + "lda_" + str(num_topics) + "_inf_a.p", "wb") as f_inf_a:
        pickle.dump(lda_inference_a, f_inf_a)
    with open(eval_path + "lda_" + str(num_topics) + "_inf_b.p", "wb") as f_inf_b:
        pickle.dump(lda_inference_b, f_inf_b)
    with open(eval_path + "lda_" + str(num_topics) + "_inf_all.p", "wb") as f_inf_all:
        pickle.dump(lda_inference_all, f_inf_all)

    # Store Perplexity
    with open(eval_path + "adj_lda_" + str(num_topics) + "_a.p", "wb") as f_perp_a:
        pickle.dump(adj_lda_perplex_a, f_perp_a)
    with open(eval_path + "adj_lda_" + str(num_topics) + "_b.p", "wb") as f_perp_b:
        pickle.dump(adj_lda_perplex_b, f_perp_b)
    with open(eval_path + "adj_lda_" + str(num_topics) + "_all.p", "wb") as f_perp_all:
        pickle.dump(adj_lda_perplex_all, f_perp_all)

    print("Finished LDA ("+str(num_topics)+") Eval "+path)


def eval_lda_logged(sample_size, path, namespace, num_topics, progress_obj, overwrite=False, ds_lock=None):
    for number_of_topics in num_topics:
        eval_lda(path, sample_size, namespace, number_of_topics)
    proglog = progress_logger(progress_obj[0], lock=progress_obj[1])
    proglog.write_log([path])
    print("Finished: " + path + " - "+str(datetime.now()))

def eval_all(relative_sizes, sample_size, iterations, namespace, num_topics, process_count=8, overwrite=False, ds_lock=None):
    # Setup Base Path
    base_path = build_basepath("samples", namespace, sample_size)

    # Init Locks for logging + dataset access
    progress_lock = mp.Lock()

    # Init Progress Log
    progress_path = base_path + "progress/adj_eval.log"
    proglog = progress_logger(progress_path, overwrite=overwrite, lock=progress_lock)
    proglog_obj = (progress_path, progress_lock)

    seen_is = set()
    # Run Logged Sample Builder
    for rel_size, i, adj_path in rel_size_iteration_loop(relative_sizes, iterations, base_path):
        if i not in seen_is:
            # make new locks when switching iterations
            seen_is.add(i)
            ds_lock = mp.Lock()
        if adj_path in proglog.get_already_written() and not overwrite:
            print("Already processed: " + str(rel_size) + " - " + str(i))
            continue

        ensure_process_count(process_count)
        p = mp.Process(target=eval_lda_logged,
                       args=(sample_size, adj_path, namespace, num_topics, proglog_obj, overwrite, ds_lock))
        p.start()
        print("Started: " + adj_path + " - " + str(datetime.now()))

    wait_for_processes()

if __name__=="__main__":
    num_topics = [64, 128, 256]
    relative_sizes = [x / 100 for x in range(10, 100, 10)]
    iterations = 50
    global_overwrite = False

    sample_size = 20000
    namespace = load_namespace("wiki")
    #eval_all(relative_sizes, sample_size, iterations, namespace, num_topics, overwrite=global_overwrite, process_count=8)

    sample_size = 10000
    namespace = load_namespace("er-UK")
    #eval_all(relative_sizes, sample_size, iterations, namespace, num_topics, overwrite=global_overwrite, process_count=8)

    sample_size = 4000
    namespace = load_namespace("er-US")
    # eval_all(relative_sizes, sample_size, iterations, namespace, num_topics, overwrite=global_overwrite,process_count=8)

    '''
    sample_size = 4000
    namespace = load_namespace("er-US")
    eval_all(relative_sizes, sample_size, iterations, namespace, num_topics, overwrite=global_overwrite, process_count=8)
    '''

