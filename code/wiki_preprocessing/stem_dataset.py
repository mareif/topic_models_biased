import sys
import time
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize
import re
import json
import multiprocessing as mp
from code.helper.Timer import Timer

'''
Apply the pair length restrictions.
Stem the articles and remove the stopwords.
Format the stemmed.

Input: ../../data/final/wiki_dataset_cleaned.tsv

Output: ../../data/final/wiki_dataset_stemmed.tsv
'''

# Helper
def loadStopwords():
    from nltk.corpus import stopwords
    # Load default nltk stopwords
    custom_stopwords = set(stopwords.words("english")).union(set(stopwords.words("german")))

    # Load custom stopwordlists
    # GERMAN: https://github.com/solariz/german_stopwords/blob/master/german_stopwords_full.txt
    # ENGLISH: http://xpo6.com/list-of-english-stop-words/
    with open("../../data/stopwords/stopwords_de.txt","r",encoding = "utf8") as f_in:
        for line in f_in:
            custom_stopwords.add(line.strip().lower())

    with open("../../data/stopwords/stopwords_en.txt","r",encoding = "utf8") as f_in:
        for line in f_in:
            custom_stopwords.add(line.strip().lower())
    return custom_stopwords

def meets_percentage_length_difference(len_a,len_b,perc_difference):
    return perc_difference==None or max(len_a,len_b)/min(len_a,len_b) <= perc_difference

def meets_total_length_difference(len_a, len_b, difference):
    return difference==None or abs(len_a-len_b) <= difference

def meets_general_length_restriction(len_a, len_b, length_restrict):
    return len_a >= length_restrict and len_b >= length_restrict

def stem_document(text, language, stoplist):
    global stemmer_en
    global stemmer_de

    # Remove everything that isn't alphanumeric
    article_text = re.sub(r"[^\w]", ' ', text)

    # Replace abbreviation of not
    article_text = re.sub(r"n't", ' not', article_text)

    # Reduce all whitespace to one
    article_text = re.sub(r"\s+", ' ', article_text)

    tokens = word_tokenize(article_text, language=language)

    # Remove the following cases for proper stopword filtering: ["'ve", "'s", "'m", "'re", "'d", "'ll", "'n'"]
    abbrevation_rest = {"ve", "s", "m", "re", "d", "ll", "n"}
    tokens = [word.lower() for word in tokens if re.match("\w+", word) and word not in abbrevation_rest]

    # Add Position identifier
    total_length = len(tokens)
    tokens = [(word,position) for position, word in enumerate(tokens)]

    tokens = [token for token in tokens if (len(token[0])>1 and token[0].isalpha() and (token[0] not in stoplist))]

    if language=="german":
        tokens = [(stemmer_de.stem(token[0]),token[1]) for token in tokens]
    elif language=="english":
        tokens = [(stemmer_en.stem(token[0]),token[1]) for token in tokens]
    else:
        raise ValueError("Language is not known: "+str(language))

    return {"tokens":tokens, "length":total_length}

def stem_chunk(lines, stoplist, lock, offset=0, len_restrict_min=0, perc_diff_restrict=None, total_diff_restrict=None):
    global stemmer_en
    global stemmer_de

    stemmer_en = SnowballStemmer("english")
    stemmer_de = SnowballStemmer("german")

    i = offset+1
    out_string = ""

    dropped = 0
    for line in lines:
        splits = line.split("\t")
        en_text = splits[2]
        de_text = splits[5]

        # Stem data
        en_text = stem_document(en_text, "english", stoplist)
        de_text = stem_document(de_text, "german", stoplist)

        if not (meets_general_length_restriction(en_text["length"], de_text["length"], len_restrict_min) and
                meets_percentage_length_difference(en_text["length"], de_text["length"], perc_diff_restrict) and
                meets_total_length_difference(en_text["length"], de_text["length"], total_diff_restrict)):
            dropped += 1
            continue

        splits[2] = json.dumps(en_text)
        splits[5] = json.dumps(de_text)

        out_string += "\t".join(splits) + "\n"
        # print("Processed Line: " + str(i))
        i += 1

    with lock:
        with open("../../data/final/wiki_dataset_stemmed.tsv", "a", encoding="utf8") as f_out:
            f_out.write(out_string)
        print("Chunk " + str(offset) + " dropped: " + str(dropped))


def stem_dataset(ds_path, chunksize = 1000, process_count=mp.cpu_count()-1, len_restrict_min=0, perc_diff_restrict=None, total_diff_restrict=None):
    timer = Timer()
    lock = mp.Lock()

    stoplist = loadStopwords()

    with open(ds_path, "r", encoding="utf8") as f_in:
        with open("../../data/final/wiki_dataset_stemmed.tsv", "w", encoding="utf8") as f_out:
            f_out.write(f_in.readline())

        chunk_id = 1
        chunk_text = []
        for line in f_in:
            chunk_text.append(line)
            if len(chunk_text) >= chunksize:
                while len(mp.active_children())>=process_count-1:
                    print("All processes active - WAITING - "+str(len(chunk_text)))
                    time.sleep(5)

                print("Starting Process on Chunk: "+str(((chunk_id-1) * chunksize)+1) + " - " + str(chunk_id * chunksize))
                timer.timestamp()

                p = mp.Process(target=stem_chunk,args=(chunk_text,
                                                       stoplist,
                                                       lock,
                                                       (chunk_id-1) * chunksize,
                                                       len_restrict_min,
                                                       perc_diff_restrict,
                                                       total_diff_restrict))
                p.start()
                chunk_id+=1
                chunk_text=[]

        if len(chunk_text)>0:
            p = mp.Process(target=stem_chunk, args=(chunk_text,
                                                    stoplist,
                                                    lock,
                                                    (chunk_id-1) * chunksize,
                                                    len_restrict_min,
                                                    perc_diff_restrict,
                                                    total_diff_restrict))
            p.start()

        while len(mp.active_children()) > 0:
            print("Finalizing")
            time.sleep(5)

    timer.timestamp()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        raise IOError("Overspecified")

    print("STARTED")

    stem_dataset("../../data/final/wiki_dataset_cleaned.tsv", len_restrict_min=50, perc_diff_restrict=2, process_count=12, chunksize=5000)

    print("FINISHED")