import pickle
import random

'''
Based on the sample seed, selects the articles necessary during this iteration.
Additionally, sets training and test part of each documents.

Input:  ../../samples/*data-set*/*sample size*/*iteration*/sample_seed.p

Output: ../../samples/*data-set*/*sample size*/*iteration*/*group*_training.tsv
'''

def line_to_data(line, a_title_index, a_text_index, b_title_index, b_text_index):
    splits = line.strip().split("\t")
    return splits[a_title_index], eval(splits[a_text_index]),splits[b_title_index], eval(splits[b_text_index])

def format_outline(pair_index, title, data):
    return "\t".join([str(pair_index),title,data]) + "\n"

def train_test_split(document, train_ratio=0.7):
    # Size of test interval
    test_ratio = 1-train_ratio
    doc_length = document["length"]
    test_length = int(doc_length*test_ratio)

    # Place test interval in document
    start_index = random.randrange(0,doc_length-test_length)
    end_index = start_index + test_length
    assert(end_index < doc_length)

    # Assign words
    training = []
    test = []
    doc_tokens = document["tokens"]
    for word, position in doc_tokens:
        if position < start_index or position > end_index:
            training.append(word)
        else:
            test.append(word)

    return training, test

def build_sample_corpus(seed_path, namespace):
    # Get group identifiers
    tag_coll_a = namespace["tag_coll_a"]
    tag_coll_b = namespace["tag_coll_b"]

    # Load Seed
    with open(seed_path + "sample_seed.p","rb") as f_seed:
        seed = pickle.load(f_seed)
    seed.sort()
    seed_index = 0

    # Init data positions in data set
    a_text_index = namespace["main_dataset"]["index_a"]
    a_title_index = namespace["main_dataset"]["title_a"]
    b_text_index = namespace["main_dataset"]["index_b"]
    b_title_index = namespace["main_dataset"]["title_b"]

    # Init Lookups
    a_train_lu = dict()
    b_train_lu = dict()
    a_test_lu = dict()
    b_test_lu = dict()

    # Init Corpora
    training_a = []
    training_b = []
    test_a = []
    test_b = []

    # Iterate data set and build sample corpus
    corpus_path = namespace["main_dataset"]["path"]
    with open(corpus_path,"r",encoding="utf8") as f_data:
        f_data.readline()
        for pair_index, line in enumerate(f_data,start=1):
            # If we found all data break
            if seed_index >= len(seed):
                break

            # if we hit a sample pair
            if pair_index==seed[seed_index]:
                # Get data and split
                a_title, a_text, b_title, b_text = line_to_data(line, a_title_index, a_text_index, b_title_index, b_text_index)
                a_train, a_test = train_test_split(a_text)
                b_train, b_test = train_test_split(b_text)

                # Add to lookup
                a_train_lu[pair_index]=a_train
                b_train_lu[pair_index]=b_train
                a_test_lu[pair_index] = a_test
                b_test_lu[pair_index] = b_test

                # Format output
                a_train_out = format_outline(pair_index, a_title, " ".join(a_train))
                b_train_out = format_outline(pair_index, b_title, " ".join(b_train))
                a_test_out = format_outline(pair_index, a_title, " ".join(a_test))
                b_test_out = format_outline(pair_index, b_title, " ".join(b_test))

                # Append to corpus
                training_a.append(a_train_out)
                training_b.append(b_train_out)
                test_a.append(a_test_out)
                test_b.append(b_test_out)

                seed_index+=1

    # Store Corpora
    with open(seed_path + tag_coll_a + "_training.tsv","wb") as f_a_train:
        for train_line in training_a:
            f_a_train.write(train_line.encode("utf8","ignore"))

    with open(seed_path + tag_coll_b + "_training.tsv","wb") as f_b_train:
        for train_line in training_b:
            f_b_train.write(train_line.encode("utf8","ignore"))

    with open(seed_path + tag_coll_a + "_test.tsv","wb") as f_a_test:
        for test_line in test_a:
            f_a_test.write(test_line.encode("utf8","ignore"))

    with open(seed_path + tag_coll_b + "_test.tsv","wb") as f_b_test:
        for test_line in test_b:
            f_b_test.write(test_line.encode("utf8","ignore"))

    # Store Lookups
    with open(seed_path + tag_coll_a + "_training.p","wb") as f_a_lu:
        pickle.dump(a_train_lu,f_a_lu)
    with open(seed_path + tag_coll_b + "_training.p","wb") as f_b_lu:
        pickle.dump(b_train_lu,f_b_lu)
    with open(seed_path + tag_coll_a + "_test.p","wb") as f_a_lu:
        pickle.dump(a_test_lu,f_a_lu)
    with open(seed_path + tag_coll_b + "_test.p","wb") as f_b_lu:
        pickle.dump(b_test_lu,f_b_lu)

    print("Created Training and Test Sets + Lookups")