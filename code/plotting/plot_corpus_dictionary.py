# NOTE: NEEDS DUMPS FOR THE DATA SET TO BE PRESENT

import json
import sys
from code.helper import load_namespace, build_basepath
import matplotlib.pyplot as plt

def extract_unique_words(global_dict, out_path):

    only_a = []  # (word, doc_frequency)
    only_b = []
    shared = 0
    for word, data in global_dict.items():
        if data["in_a"]>0 and data["in_b"]==0:
            only_a.append((word,data["in_a"]))
        elif data["in_b"] > 0 and data["in_a"] == 0:
            only_b.append((word, data["in_b"]))
        else:
            shared+=1

    only_a.sort(key=lambda x: x[1],reverse=True)
    only_b.sort(key=lambda x: x[1],reverse=True)

    with open(out_path+"unique_words_stats.txt","w",encoding="utf8") as f_out:
        f_out.write("Overall\n\n")
        f_out.write("Overall unique tokens A: " + str(len(only_a)) + "\n")
        f_out.write("Overall unique tokens B: " + str(len(only_b)) + "\n\n-----------------------------\n\n")

        f_out.write("Most Frequenty Unique A\n\n")
        for index, (word,frequency) in enumerate(only_a[:50]):
            f_out.write(str(index+1) + ".\t"+str(word)+"\t-\t"+str(frequency)+"\n")
        f_out.write("\n\n-----------------------------\n\n")

        f_out.write("Most Frequenty Unique B\n\n")
        for index, (word, frequency) in enumerate(only_b[:50]):
            f_out.write(str(index + 1) + ".\t" + str(word) + "\t-\t" + str(frequency) + "\n")
        f_out.write("\n\n-----------------------------\n\n")

    return len(only_a), len(only_b), shared

def plot_corpus_dictionary(ds_name, namespace):
    plt.rc('text', usetex=True)
    plt.style.use('seaborn-paper')

    with open("../../dumps/"+ds_name+".dump", "r") as f_dump:
        print("Loading Dump: ../../dumps/"+ds_name+".dump")
        data = json.load(f_dump)
        global_dict = data["global_dict"]

    out_path = build_basepath("plots", namespace, subfolder=ds_name)

    # Dump unique words for each group
    a_uniq, b_uniq, shared = extract_unique_words(global_dict, out_path)
    total = a_uniq + b_uniq + shared

    #Normalize
    a_uniq /= total
    b_uniq /= total
    shared /= total

    # Plot distribution
    fig, ax = plt.subplots(figsize=(5.7,0.7))
    ax.get_yaxis().set_visible(False)
    ax.set_xticks([x/10 for x in range(11)])

    ax.barh([0], [1], align='edge', color='blue', height=1, label=namespace["tag_coll_b"] + " exclusive")
    ax.barh([0], [a_uniq+shared], align='edge', color='purple', height=1, label="shared")
    ax.barh([0], [a_uniq], align='edge', color='red', height=1, label=namespace["tag_coll_a"] + " exclusive")

    ax.set_xlabel('Proportion')

    handles, labels = ax.get_legend_handles_labels()
    handles = [handles[2], handles[1], handles[0]]
    labels = [labels[2], labels[1], labels[0]]

    lgd = ax.legend(handles=handles, labels=labels, bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                    ncol=3, mode="expand", borderaxespad=0.)

    fig.savefig(out_path+"ditionary_dist.png",bbox_extra_artists=(lgd,), bbox_inches='tight')
    fig.savefig(out_path + "ditionary_dist.pdf", bbox_extra_artists=(lgd,), bbox_inches='tight', format="pdf")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        raise IOError("Overspecified")
    print("STARTED")

    namespace = load_namespace("wiki")
    plot_corpus_dictionary("wiki_dataset_reduced", namespace)
    plot_corpus_dictionary("wiki_dataset_stemmed", namespace)

    namespace = load_namespace("er-US")
    plot_corpus_dictionary("US_rand_pairs_len_restrict", namespace)
    plot_corpus_dictionary("US_rand_pairs_processed", namespace)

    namespace = load_namespace("er-UK")
    plot_corpus_dictionary("UK_rand_pairs_len_restrict", namespace)
    plot_corpus_dictionary("UK_rand_pairs_processed", namespace)

    print("FINISHED")
