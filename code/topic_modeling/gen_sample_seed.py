from os.path import exists
from os import makedirs
import pickle
from random import sample, shuffle

'''
Creates the sample seed. Chooses which pairs to use for one sample

Input:  --- namespace needs to be defined

Output: ../../samples/*data-set*/*sample size*/sample_seed.p
'''

def create_sample_seed(sample_size, namespace):
    # Get Sample Lines
    amount_pairs = namespace["amount_pairs"]
    sample_ids = sample(range(1, amount_pairs + 1), sample_size)
    return sample_ids

def gen_sample_seed(sample_size, namespace, out_path, overwrite=False):
    # Get Seed and Shuffle
    sample_seed = create_sample_seed(sample_size, namespace)
    shuffle(sample_seed)

    if not overwrite and exists(out_path + "sample_seed.p"):
        print("Sample seed exists - Continue")
        return
    else:
        if not exists(out_path):
            makedirs(out_path)
        with open(out_path + "sample_seed.p", "wb") as f_seed:
            pickle.dump(sample_seed,f_seed)

    print("Created Seed: "+out_path)