import re
import json
import multiprocessing as mp
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize

'''
Stem all articles and remove stopwords
Store the stems together with their position in the document and the overall doc length

Input:  *dataset@outpath*_nodup.tsv
        ../../data/stopwords/*stoplists*
Output: *dataset@outpath*_processed.tsv
'''

# Helper
def loadStopwords():
    from nltk.corpus import stopwords
    # Load default nltk stopwords
    custom_stopwords = set(stopwords.words("english"))

    # Load custom stopwordlists
    # ENGLISH: http://xpo6.com/list-of-english-stop-words/
    with open("../../data/stopwords/stopwords_en.txt","r",encoding = "utf8") as f_in:
        for line in f_in:
            custom_stopwords.add(line.strip().lower())
    return custom_stopwords

# Restrictions
def meets_percentage_length_difference(len_a, len_b, perc_difference):
    return perc_difference == None or max(len_a, len_b) / min(len_a, len_b) <= perc_difference

def meets_general_length_restriction(len_a, len_b, length_restrict):
    return len_a >= length_restrict and len_b >= length_restrict

def stem_document(text, stoplist):
    global stemmer_en

    # Remove everything that isn't alphanumeric
    article_text = re.sub(r"[^\w]", ' ', text)

    # Replace abbreviation of not
    article_text = re.sub(r"n't", ' not', article_text)

    # Reduce all whitespace to one
    article_text = re.sub(r"\s+", ' ', article_text)

    tokens = word_tokenize(article_text, language="english")

    # Remove the following cases for proper stopword filtering: ["'ve", "'s", "'m", "'re", "'d", "'ll", "'n'"]
    abbrevation_rest = {"ve", "s", "m", "re", "d", "ll", "n"}
    tokens = [word.lower() for word in tokens if re.match("\w+", word) and word not in abbrevation_rest]

    # Add Position identifier
    total_length = len(tokens)
    tokens = [(word,position) for position, word in enumerate(tokens)]

    tokens = [token for token in tokens if (len(token[0])>1 and token[0].isalpha() and (token[0] not in stoplist))]

    tokens = [(stemmer_en.stem(token[0]),token[1]) for token in tokens]

    return {"tokens":tokens, "length":total_length}

# Run over corpora, lemmatize and store
def process_article_text(outpath, inpath, min_length_restrict, perc_difference=None):

    print("Started: "+inpath+" -> "+outpath+"; min_len: "+ str(min_length_restrict)+"; perc_diff: "+str(perc_difference))

    global stemmer_en
    stemmer_en = SnowballStemmer("english")
    stoplist = loadStopwords()

    with open(inpath, "r", encoding="utf8") as f_in:
        with open(outpath, "w", encoding="utf8") as f_out:
            # Copy first line and read the field tags
            first_line = f_in.readline()
            f_out.write(first_line)
            fields = first_line.strip().split("\t")
            dropped = 0
            amount_lines = 0

            # Parse document, transform text to json representation, write
            for line_nr, line in enumerate(f_in):
                amount_lines = line_nr
                splits = line.strip().split("\t")
                data = dict(zip(fields, splits))

                data_left = stem_document(data["left_text"], stoplist)
                data_right = stem_document(data["right_text"], stoplist)

                # Check if the pair meets the length restrictions
                if not (meets_percentage_length_difference(data_left["length"],
                                                           data_right["length"],
                                                           perc_difference)
                        and
                            meets_general_length_restriction(data_left["length"],
                                                             data_right["length"],
                                                             min_length_restrict)
                        ):
                    dropped += 1
                    continue

                data["left_text"] = json.dumps(data_left)
                data["right_text"] = json.dumps(data_right)
                f_out.write("\t".join([data[field] for field in fields]) + "\n")

    print("Dropped: " + str(dropped) + " out of " + str(amount_lines) + " - " + str(
        (((dropped / amount_lines)) // 0.0001) / 100) + "%")


if __name__ == "__main__":
    dataset_path = "../../data/final/"

    pool = mp.Pool(processes = 2)
    tasks = [(dataset_path+"US_rand_pairs_processed.tsv",
              dataset_path+"US_rand_pairs_nodup.tsv",
              50,
              2),
            (dataset_path+"UK_rand_pairs_processed.tsv",
             dataset_path+"UK_rand_pairs_nodup.tsv",
             50,
              2)]
    pool.starmap(process_article_text,tasks)
    print("Finished")