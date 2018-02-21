from code.eventreg_preprocessing import *
from code.helper import load_sources
import os

'''
Requires ER event articles in ../../data/article_data
(produced by manual execution of get_event_list and acquire_data)

This function builds the data set, removes duplicates and returns a stemmed data set

Input:  ../../data/news_sources/*source lists*
        ../../data/article_data/*event_id*.art (multiple)

Output (Final): *dataset@outpath*_processed.tsv
'''

def run_er_preprocessing(outpath, left_outlets, right_outlets):

    # Build with random pairing behavior
    build_dataset(outpath,
                  left_outlets,
                  right_outlets,
                  pairing_behaviour="random")

    remove_duplicates(outpath)

    splits = outpath.split(".")

    no_dup_path = ".".join(splits[:-1]) + "_nodup." + splits[-1]
    final_out_path = ".".join(splits[:-1]) + "_processed." + splits[-1]

    process_article_text(final_out_path,no_dup_path,50,2)

if __name__ == '__main__':
    data_set_path = "../../data/final/"
    if not os.path.exists(data_set_path):
        os.makedirs(data_set_path)

    news_sources = load_sources()

    run_er_preprocessing(data_set_path + "UK_rand_pairs.tsv",
                  news_sources.left_uk,
                  news_sources.right_uk)
    run_er_preprocessing(data_set_path + "US_rand_pairs.tsv",
                  news_sources.left_us,
                  news_sources.right_us)
    run_er_preprocessing(data_set_path + "Mixed_rand_pairs.tsv",
                  news_sources.left,
                  news_sources.right)