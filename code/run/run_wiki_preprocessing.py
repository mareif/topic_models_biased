import sys
from code.wiki_preprocessing import *
from code.helper import Timer

'''
Requires WikiExtrector data articles in ../../data/en/clean/ or ../../data/de/clean/
(produced by manual execution of WikiExtrector https://github.com/attardi/wikiextractor)
And Link information of Wikipedia in ../../data/en/original or ../../data/de/original

This function builds the data set, removes duplicates and returns a stemmed data set

Input:  ../../data/en/clean/wiki_xy
        ../../data/de/clean/wiki_xy
        ../../data/en/original/enwiki-latest-langlinks.sql
        ../../data/de/original/dewiki-latest-langlinks.sql

Output (Final): ../../data/final/wiki_dataset_stemmed.tsv
'''

def run_wiki_preprocessing():
    timer = Timer()

    # transform_wikiextr_output()
    print("Finished: Transforming WikiExtractor Output")
    timer.timestamp()

    # create_title_id_lu()
    print("Finished: Creating Title ID Lookup")
    timer.timestamp()

    # get_paired_docs()
    print("Finished: Getting paired documents")
    timer.timestamp()

    # pair_articles()
    print("Finished: Pairing Documents")
    timer.timestamp()

    # filter_pairs()
    print("Finished: Filtering pairs")
    timer.timestamp()

    # add_text_to_pairs()
    print("Finished: Adding text to pairs")
    timer.timestamp()

    stem_dataset(ds_path="../../data/final/wiki_dataset_cleaned.tsv", len_restrict_min=50, perc_diff_restrict=2)
    print("Finished: Stemming Dataset")
    timer.timestamp()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        raise IOError("Overspecified")
    print("STARTED - Wiki Preprocessing")
    run_wiki_preprocessing()
    print("FINISHED - Wiki Preprocessing")
