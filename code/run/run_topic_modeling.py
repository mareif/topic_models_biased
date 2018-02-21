from datetime import datetime
from os.path import exists

from code.helper import *
from code.topic_modeling.build_one_sample import build_one_sample
from code.topic_modeling.build_sample_corpus import build_sample_corpus
from code.topic_modeling.gen_sample_seed import  gen_sample_seed

'''
Requires Namespaces to be defined + Datasets to be present
Is currently setup for an 8-core machine

Runs the complete experiment on one of the data sets.

Input:  *dataset* data specified in namespace
        experiment parameters (relative sizes, sample size, number of topics)
        
Output: Trained LDA + Perplexity and Inference data of the test corpora
'''

def run_logged_sample(relative_size, sample_size, path, namespace, num_topics, progress_obj, overwrite=False, ds_lock=None):
    build_one_sample(relative_size, sample_size, path, namespace, num_topics, overwrite=overwrite, ds_lock=ds_lock)
    proglog = progress_logger(progress_obj[0], lock=progress_obj[1])
    proglog.write_log([path])
    print("Finished: " + path + " - "+str(datetime.now()))

def run_topic_modelling(relative_sizes, sample_size, iterations, namespace, num_topics, process_count=8, overwrite=False, ds_lock=None):
    # Setup Base Path
    base_path = build_basepath("samples", namespace, sample_size)

    # Init Locks for logging + dataset access
    progress_lock = mp.Lock()

    # Init Progress Log
    progress_path = base_path + "progress/model.log"
    proglog = progress_logger(progress_path, overwrite=overwrite, lock=progress_lock)
    proglog_obj = (progress_path, progress_lock)

    # Set Sample Seeds and Build According Sample Corpora
    for i in range(1,iterations+1):
        seed_path = base_path+str(i)+"/"
        if not overwrite and exists(seed_path + "sample_seed.p"):
            print("Seed already initialized: " + seed_path)
            continue
        gen_sample_seed(sample_size ,namespace, seed_path , overwrite=overwrite)
        build_sample_corpus(seed_path, namespace)

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
        p = mp.Process(target=run_logged_sample,
                       args=(rel_size, sample_size, adj_path, namespace, num_topics, proglog_obj, overwrite, ds_lock))
        p.start()
        print("Started: " + adj_path + " - " + str(datetime.now()))

    wait_for_processes()

if __name__=="__main__":
    num_topics = [64, 128, 256]
    relative_sizes = [x / 100 for x in range(10, 100, 50)]
    iterations = 1
    global_overwrite = False

    sample_size = 20000
    namespace = load_namespace("wiki")
    run_topic_modelling(relative_sizes, sample_size, iterations, namespace, num_topics, overwrite=global_overwrite, process_count=8)

    sample_size = 10000
    namespace = load_namespace("er-UK")
    run_topic_modelling(relative_sizes, sample_size, iterations, namespace, num_topics, overwrite=global_overwrite, process_count=8)

    sample_size = 4000
    namespace = load_namespace("er-US")
    run_topic_modelling(relative_sizes, sample_size, iterations, namespace, num_topics, overwrite=global_overwrite, process_count=8)