'''
Sets the name structure, the data set paths, and necessary data for each data set

This needs to be changed manually by the user
'''

def load_namespace(mode):
    if mode == "wiki":
        # Wiki namespaces
        global_namespace = "wikipedia"
        main_dataset = {"path": "J:/master_thesis/data/final/wiki_dataset_stemmed.tsv",
                       "formatted": True,
                        "title_a": 1,
                        "index_a": 2,
                        "title_b": 4,
                        "index_b": 5}
        amount_pairs = 386365
        tag_coll_a = "en"
        tag_coll_b = "de"
        data_sets = [{"path": "J:/master_thesis/data/final/wiki_dataset_stemmed.tsv",
                       "formatted": True,
                       "index_a": 2,
                       "index_b": 5}]

    elif mode == "er-US":  # EventRegistry US
        global_namespace = "er-US"
        main_dataset = {"path": "J:/master_thesis/data/final/US_rand_pairs_processed.tsv",
                      "formatted": True,
                      "title_a": 4,
                      "index_a": 5,
                      "title_b": 9,
                      "index_b": 10}
        amount_pairs = 4721
        tag_coll_a = "left"
        tag_coll_b = "right"
        data_sets = [{"path":"J:/master_thesis/data/final/US_rand_pairs.tsv",
                       "formatted":False,
                       "index_a":5,
                       "index_b": 10},
                     {"path": "J:/master_thesis/data/final/US_rand_pairs_processed.tsv",
                      "formatted": True,
                      "index_a": 5,
                      "index_b": 10},
                     {"path": "J:/master_thesis/data/final/US_rand_pairs_len_restrict.tsv",
                      "formatted": False,
                      "index_a": 5,
                      "index_b": 10
                      }]

    elif mode == "er-UK":  # EventRegistry UK
        global_namespace = "er-UK"
        amount_pairs = 18170
        main_dataset = {"path": "J:/master_thesis/data/final/UK_rand_pairs_processed.tsv",
                      "formatted": True,
                      "title_a": 4,
                      "index_a": 5,
                      "title_b": 9,
                      "index_b": 10}
        tag_coll_a = "left"
        tag_coll_b = "right"
        data_sets = [{"path":"J:/master_thesis/data/final/UK_rand_pairs.tsv",
                       "formatted":False,
                       "index_a":5,
                       "index_b": 10},
                     {"path": "J:/master_thesis/data/final/UK_rand_pairs_processed.tsv",
                      "formatted": True,
                      "index_a": 5,
                      "index_b": 10},
                     {"path": "J:/master_thesis/data/final/UK_rand_pairs_len_restrict.tsv",
                      "formatted": False,
                      "index_a": 5,
                      "index_b": 10
                      }
                     ]
    else:
        raise ValueError("Unknown mode")

    return {"mode":mode,
            "db_name": db_name,
            "global_namespace": global_namespace,
            "tag_coll_a": tag_coll_a,
            "tag_coll_b": tag_coll_b,
            "data_sets": data_sets,
            "amount_pairs": amount_pairs,
            "main_dataset": main_dataset}

