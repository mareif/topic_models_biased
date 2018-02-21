import sys
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import json
from os.path import exists
from code.helper import build_basepath, load_namespace
import re
plt.style.use("seaborn-paper")

def fp_to_dump(file_path):
    file_name = file_path.strip().split("/")[-1]
    file_name = ".".join(file_name.split(".")[:-1])
    return file_name+".dump"

def quick_clean(text):
    # Remove everything that isn't alphanumeric
    article_text = re.sub(r"[^\w]", ' ', text)
    # Replace abbreviation of not
    article_text = re.sub(r"n't", ' not', article_text)
    # Reduce all whitespace to one
    article_text = re.sub(r"\s+", ' ', article_text)
    return article_text.lower().split()

def create_dump(file_path, dump_dir, formatted, index_a, index_b):
    if formatted==None or not index_a or not index_b:
        raise ValueError("Formatting or indeces need to be specified")
    # e.g. file_path: "../../data/final/wiki_dataset_cleaned.tsv"
    a_lens = []
    b_lens = []
    len_diffs = []
    len_diffs_perc = []

    global_dict = dict()

    uniq_words_a = []
    uniq_words_b = []

    with open(file_path, "r", encoding="utf8") as f_in:
        f_in.readline()
        for i,line in enumerate(f_in):
            if i%1000 == 0:
                print("Read line: "+str(i))
            splits = line.strip().split("\t")

            words_in_a = set()
            words_in_b = set()

            if formatted:
                a_doc = json.loads(splits[index_a])
                b_doc = json.loads(splits[index_b])
                len_a = a_doc["length"]
                len_b = b_doc["length"]

                for word,_ in a_doc["tokens"]:
                    if global_dict.get(word)==None:
                        global_dict[word]= {"freq_global":0, "freq_a":0, "freq_b":0,
                                            "in_a":0, "in_b":0, "in_both":0}
                    global_dict[word]["freq_global"] += 1
                    global_dict[word]["freq_a"] += 1
                    if word not in words_in_a:
                        words_in_a.add(word)
                        global_dict[word]["in_a"] += 1

                for word,_ in b_doc["tokens"]:
                    if global_dict.get(word)==None:
                        global_dict[word]= {"freq_global":0, "freq_a":0, "freq_b":0,
                                            "in_a":0, "in_b":0, "in_both":0}
                    global_dict[word]["freq_global"] += 1
                    global_dict[word]["freq_b"] += 1
                    if word not in words_in_b:
                        words_in_b.add(word)
                        global_dict[word]["in_b"] += 1

                    if word in words_in_a and word in words_in_b:
                        global_dict[word]["in_both"] += 1


            else:
                a_doc = quick_clean(splits[index_a])
                b_doc = quick_clean(splits[index_b])

                len_a = len(splits[index_a].split())
                len_b = len(splits[index_b].split())

                for word in a_doc:
                    if global_dict.get(word)==None:
                        global_dict[word]= {"freq_global":0, "freq_a":0, "freq_b":0,
                                            "in_a":0, "in_b":0, "in_both":0}
                    global_dict[word]["freq_global"] += 1
                    global_dict[word]["freq_a"] += 1
                    if word not in words_in_a:
                        words_in_a.add(word)
                        global_dict[word]["in_a"] += 1

                for word in b_doc:
                    if global_dict.get(word)==None:
                        global_dict[word]= {"freq_global":0, "freq_a":0, "freq_b":0,
                                            "in_a":0, "in_b":0, "in_both":0}
                    global_dict[word]["freq_global"] += 1
                    global_dict[word]["freq_b"] += 1
                    if word not in words_in_b:
                        words_in_b.add(word)
                        global_dict[word]["in_b"] += 1

                    if word in words_in_a and word in words_in_b:
                        global_dict[word]["in_both"] += 1

            diff_a_b = len_a - len_b
            a_lens.append(len_a)
            b_lens.append(len_b)
            len_diffs.append(diff_a_b)
            uniq_words_a.append(len(words_in_a))
            uniq_words_b.append(len(words_in_b))

            # Percentual difference: Neg = B overhead, Pos = A overhead
            if len_b > len_a:
                len_diffs_perc.append(-1 * ((len_b / len_a)-1))
            else:
                len_diffs_perc.append((len_a / len_b)-1)

    return_obj = {"a_lens": a_lens, "b_lens": b_lens, "len_diffs": len_diffs, "len_diffs_perc": len_diffs_perc,
                  "global_dict": global_dict, "uniq_words_a": uniq_words_a, "uniq_words_b": uniq_words_b}

    with open(dump_dir+fp_to_dump(file_path), "w") as f_dump:
        json.dump(return_obj, f_dump)

def load_dump(file_path, dump_dir, cut_min=None, cut_max=None, cut_diff=None):
    with open(dump_dir+fp_to_dump(file_path), "r") as f_dump:
        print("Loading Dump: "+dump_dir+fp_to_dump(file_path))
        data = json.load(f_dump)
        a_lens = data["a_lens"]
        b_lens = data["b_lens"]
        len_diffs = data["len_diffs"]
        len_diffs_perc = data["len_diffs_perc"]
        global_dict = data["global_dict"]
        uniq_words_a = data["uniq_words_a"]
        uniq_words_b = data["uniq_words_b"]

        amount_lines = len(a_lens)
        fallout = 0
        for i in range(0, len(a_lens)):
            len_a = a_lens[i]
            len_b = b_lens[i]
            if ((cut_min != None and (len_a <= cut_min or len_b <= cut_min)) or
                (cut_max != None and (len_a >= cut_max or len_b >= cut_max)) or
                (cut_diff != None and (abs(len_a - len_b) >= cut_diff))):
                fallout += 1
    if cut_min != None or cut_max != None or cut_diff != None:
        print("Cutting with: (min: " + str(cut_min) +
              ",max: " + str(cut_max) +
              ",diff: " + str(cut_diff) + ") results in total fallout of " +
              str(((fallout / amount_lines) // 0.0001) / 100) + "%")

    return a_lens, b_lens, len_diffs, len_diffs_perc, global_dict, uniq_words_a, uniq_words_b

def load_dump_data(file_path, formatted=None, index_a=None, index_b=None, cut_min=None, cut_max=None, cut_diff=None, dump_dir = "../../dumps/"):
    if not exists(dump_dir+fp_to_dump(file_path)):
        print("Dump not found - loading original file")
        create_dump(file_path=file_path, dump_dir = dump_dir, formatted=formatted, index_a=index_a, index_b=index_b)
    params = load_dump(file_path=file_path, dump_dir = dump_dir, cut_min=cut_min, cut_max=cut_max, cut_diff=cut_diff)
    return params

def plot_diff_histogram(values, display_mode, namespace, bin_from=None, bin_to=None, bin_gran=100):
    if bin_from == None:
        bin_from = min(values)
    if bin_to == None:
        bin_to = max(values)

    if display_mode == "sbs":
        # Side by side
        bins = np.linspace(bin_from, bin_to, bin_gran)
    elif display_mode == "overlap":
        # Overlap
        if bin_to != max(values):
            bins = np.linspace(0, bin_to, bin_gran)
        else:
            bins = np.linspace(0, max(-bin_from, bin_to), bin_gran)
    else:
        raise ValueError("Unknown display mode: "+str(display_mode))

    overhead_a = []
    overhead_b = []
    for value in values:
        if value > 0:
            overhead_a.append(value)
        elif value < 0:
            overhead_b.append(value)
    plt.hist(overhead_a, bins, alpha=0.5, color="r", label=namespace["tag_coll_a"] + " overhead")
    plt.hist(overhead_b, bins, alpha=0.5, color="b", label=namespace["tag_coll_b"] + " overhead")
    plt.legend()

def plot_histogram(values, mode, bin_from=None, bin_to=None, bin_gran=100):
    plt.ylabel("Frequency")

    if bin_from == None:
        bin_from = min(values)
    if bin_to == None:
        bin_to = max(values)

    if mode == "a":
        color = "r"
    elif mode == "b":
        color = "b"
    else:
        raise ValueError("Unknwon mode: "+str(mode))

    bins = np.linspace(bin_from, bin_to, bin_gran)
    plt.hist(values, bins, color=color)

def plot_diff_cdf(values, namespace, at_x=list()):
    amount_values = len(values)
    count_dict = Counter(values)

    plt.ylabel("Cumulative Amount")

    at_x.sort()
    perc_at_x = dict()
    for x in at_x:
        perc_at_x[x]=[0,0]

    x_a = []
    y_a = []
    x_b = []
    y_b = []
    current_a = 0
    current_b = 0
    crossed_zero = False

    for key in sorted(count_dict.keys()):

        for x in at_x:
            if abs(key) > x and key >= 0:
                perc_at_x[x][0] += count_dict[key]
            if abs(key) > x and key <=0:
                perc_at_x[x][1] += count_dict[key]

        if key >= 0:
            if not crossed_zero:
                crossed_zero=True
                y_b = [current_b - y_val for y_val in y_b]

            current_a += count_dict[key]
            x_a.append(key)
            y_a.append(current_a)

        if key <= 0:
            current_b += count_dict[key]
            x_b.append(-key)
            y_b.append(current_b)

    plt.step(x_a, y_a, color="r", label = str(namespace["tag_coll_a"]), linewidth=2)
    plt.step(x_b, y_b, color="b", label = str(namespace["tag_coll_b"]), linewidth=2)
    plt.legend(loc="lower right")

    for x_cut in at_x:
        plt.axvline(x_cut, color="g")

    if len(at_x) > 0:
        print("Differences:")
        for key in sorted(perc_at_x.keys()):
            print("Lost values in "+namespace["tag_coll_a"]+" @x=" + str(key) + " : " +
                  str(perc_at_x[key][0]) + " = " +
                  str((((perc_at_x[key][0] / amount_values)) // 0.0001) / 100) + "%")
            print("Lost values in " + namespace["tag_coll_b"] + " @x=" + str(key) + " : " +
                  str(perc_at_x[key][1]) + " = " +
                  str((((perc_at_x[key][1] / amount_values)) // 0.0001) / 100) + "%")
        print("\n")

def plot_cdf(values, mode, percentiles=list(), cutoff=list(), at_x=list(), label=False):
    if len(percentiles) > 0 and len(cutoff) > 0:
        raise ValueError("Only enter percentile or cutoff")

    amount_values = len(values)
    count_dict = Counter(values)

    plt.ylabel("Cumulative Amount")

    percentiles.sort()
    percentiles_x = []
    percentiles_index = 0

    at_x.sort()
    perc_at_x = dict()
    at_x_index = 0

    x = []
    y = []

    current = 0
    for key in sorted(count_dict.keys()):

        while at_x_index < len(at_x) and key > at_x[at_x_index]:
            perc_at_x[at_x[at_x_index]] = current / amount_values
            at_x_index += 1

        current += count_dict[key]

        while percentiles_index < len(percentiles) and current / amount_values >= percentiles[percentiles_index] / 100:
            percentiles_x.append(key)
            percentiles_index += 1
        while at_x_index < len(at_x) and key == at_x[at_x_index]:
            perc_at_x[at_x[at_x_index]] = current
            at_x_index += 1

        x.append(key)
        y.append(current)

    if mode == "a":
        color = "r"
    elif mode == "b":
        color = "b"
    else:
        raise ValueError("Unknwon mode: " + str(mode))

    if label:
        plt.step(x, y, color=color, label=namespace["tag_coll_"+mode], linewidth = 2)
    else:
        plt.step(x, y, color=color, linewidth = 2)
    for percentile in percentiles_x:
        plt.axvline(percentile, color="g", linewidth = 2)

    cutoff.sort()
    for threshold in cutoff:
        plt.axvline(threshold, color="g", linewidth = 2)

    if len(at_x) > 0:
        # Init output
        for key in sorted(perc_at_x.keys()):
            print(str(key) + " : " + str(perc_at_x[key]) + " = " + str(
                (((perc_at_x[key] / amount_values)) // 0.0001) / 100) + "%")
        print("\n")

def plot_counts(values, namespace, cutoff=None):
    pre_a_overhead = 0
    pre_b_overhead = 0
    post_a_overhead = 0
    post_b_overhead = 0

    for value in values:
        if value > 0:
            pre_a_overhead += 1
            if cutoff != None and value >= cutoff[0] and value <= cutoff[1]:
                post_a_overhead += 1

        if value < 0:
            pre_b_overhead += 1
            if cutoff != None and value >= cutoff[0] and value <= cutoff[1]:
                post_b_overhead += 1

    plt.title("Counts @cutoff:" + str(cutoff) + " @post: " + str(post_a_overhead + post_b_overhead))
    plt.ylabel("Amount")

    bar1 = plt.bar([0, 1], [pre_a_overhead, pre_b_overhead], width=0.75, color=["r", "b"], alpha=0.3, align="center")
    bar2 = plt.bar([0, 1], [post_a_overhead, post_b_overhead], width=0.75, color=["r", "b"], align="center")
    plt.xticks([0, 1], (namespace["tag_coll_a"]+' overhead', namespace["tag_coll_b"]+' overhead'))
    plt.legend((bar1, bar2), ("Pre", "Post"))

def plot_sources_dist(sources, namespace, width=0.5, *args, **kwargs):
    plt.ylabel("Frequency")
    dict_items = sorted(list(sources.items()), key=lambda x: x[1], reverse=True)
    labels, values = zip(*dict_items)
    index = np.arange(0,len(dict_items))
    colors = 'rgbymc'
    plt.bar(index, height=values, width = width, color=colors ,*args, **kwargs)
    plt.xticks(index +width/2, labels,rotation="vertical")
    plt.tight_layout()

def plot_pair_matrix(sources_a, sources_b, sources_pair, namespace):
    # A on x-axis, B on y-axis
    dict_items_a = sorted(list(sources_a.items()), key=lambda x: x[1], reverse=True)
    labels_a, values_a = zip(*dict_items_a)
    index_a = np.arange(0, len(dict_items_a))

    dict_items_b = sorted(list(sources_b.items()), key=lambda x: x[1], reverse=True)
    labels_b, values_b = zip(*dict_items_b)
    index_b = np.arange(0, len(dict_items_b))

    matrix = np.zeros((len(dict_items_b),len(dict_items_a)))
    for pair, amount in sources_pair.items():
        lookup_a = labels_a.index(pair[0])
        lookup_b = labels_b.index(pair[1])
        matrix[lookup_b,lookup_a] = amount

    im = plt.imshow(matrix, interpolation="none")

    plt.xticks(index_a, labels_a, rotation="vertical")
    plt.yticks(index_b, labels_b)

    plt.colorbar(im, use_gridspec=True)
    plt.tight_layout()

def load_sources(file_path, namespace):
    with open(file_path,"r",encoding="utf8") as f_in:
        first_line = f_in.readline().strip().split("\t")
        a_index = None
        b_index = None
        for index, field_name in enumerate(first_line):
            if field_name==namespace["tag_coll_a"]+"_source_name":
                a_index = index
            if field_name==namespace["tag_coll_b"]+"_source_name":
                b_index = index
        if a_index==None or b_index==None:
            raise ValueError("Could not find the necessary field names")

        sources_a = {}
        sources_b = {}
        sources_pair = {}
        for line in f_in:
            splits = line.strip().split("\t")
            source_a = splits[a_index]
            source_b = splits[b_index]
            if sources_a.get(source_a) == None:
                sources_a[source_a]=0
            sources_a[source_a] += 1

            if sources_b.get(source_b) == None:
                sources_b[source_b]=0
            sources_b[source_b] += 1

            source_pair = (source_a,source_b)
            if sources_pair.get(source_pair)==None:
                sources_pair[source_pair] = 0
            sources_pair[source_pair]+=1

        return sources_a, sources_b, sources_pair

def plot_word_frequency(ax,dictionary, key="freq_global", *args, **kwargs):

    ax.set_xlabel("Rank")
    ax.set_ylabel("Frequency")

    y = sorted([item[1][key] for item in dictionary.items() if item[1][key]>0], reverse=True)
    x = range(1, len(y) + 1)

    ax.step(x, y, *args, **kwargs)

def write_stat_overview(file_path, namespace, a_lens, b_lens, len_diffs, len_diffs_perc, global_dict, uniq_words_a, uniq_words_b):
    amount_pairs = len(a_lens)

    # General Length stats
    min_len_a = min(a_lens)
    max_len_a = max(a_lens)
    mean_len_a = sum(a_lens)/len(a_lens)
    min_len_b = min(b_lens)
    max_len_b = max(b_lens)
    mean_len_b = sum(b_lens) / len(b_lens)

    # Length Difference Stats
    min_len_diff = min(len_diffs)
    max_len_diff = max(len_diffs)
    mean_len_diff = 0
    absolute_mean_len_diff = 0
    for len_diff in len_diffs:
        absolute = abs(len_diff)
        mean_len_diff += len_diff
        absolute_mean_len_diff += absolute
    mean_len_diff /= len(len_diffs)
    absolute_mean_len_diff /= len(len_diffs)


    min_len_perc_diff = min(len_diffs_perc)
    max_len_perc_diff = max(len_diffs_perc)
    mean_len_diff_perc = 0
    absolute_mean_len_diff_perc = 0
    for len_diff_perc in len_diffs_perc:
        absolute_perc = abs(len_diff_perc)
        mean_len_diff_perc += len_diff_perc
        absolute_mean_len_diff_perc += absolute_perc
    mean_len_diff_perc /= len(len_diffs_perc)
    absolute_mean_len_diff_perc /= len(len_diffs_perc)

    a_longer_than_b = 0
    a_equal_b = 0
    b_longer_than_a = 0

    for x in len_diffs:
        if x>0:
            a_longer_than_b+=1
        elif x==0:
            a_equal_b+=1
        else:
            b_longer_than_a+=1

    # Threshold Tests (length <50, length difference >= x2)
    smaller_50 = len([x for x in a_lens if x < 50] + [x for x in b_lens if x < 50])
    pair_smaller_50 = len([i for i in range(0,len(a_lens)) if (a_lens[i] < 50 or b_lens[i] < 50)])
    twice_as_long = len([x for x in len_diffs_perc if (x>1 or x<-1)])

    # Dictionary Stats
    amount_words_a = len([x for x in global_dict.items() if x[1]["freq_a"]>0])
    amount_words_b = len([x for x in global_dict.items() if x[1]["freq_b"]>0])
    amount_words_corp = len(global_dict)
    shared_words_unique = amount_words_a + amount_words_b - amount_words_corp
    common_words_per_pair = sum([x[1]["in_both"] for x in global_dict.items()])/amount_pairs

    # Word uniqueness
    min_uniq_a = min(uniq_words_a)
    min_uniq_b = min(uniq_words_b)
    max_uniq_a = max(uniq_words_a)
    max_uniq_b = max(uniq_words_b)
    mean_uniq_a = sum(uniq_words_a)/len(uniq_words_a)
    mean_uniq_b = sum(uniq_words_b)/len(uniq_words_b)

    top20_a = sorted(global_dict.items(),key=lambda x: x[1]["freq_a"], reverse=True)[0:20]
    top20_b = sorted(global_dict.items(), key=lambda x: x[1]["freq_b"], reverse=True)[0:20]
    top20_corp = sorted(global_dict.items(), key=lambda x: x[1]["freq_global"], reverse=True)[0:20]

    with open(file_path,"w",encoding="utf8") as f_out:
        a_tag = namespace["tag_coll_a"]
        b_tag = namespace["tag_coll_b"]

        # General Stats
        f_out.write("General Stats\n\n")
        f_out.write("Amount of pairs: "+str(amount_pairs)+"\n")
        f_out.write("\n-----------------------------\n\n")

        # Lengths Stats
        f_out.write("Length Statistics\n\n")

        f_out.write("Min. Document Length "+a_tag+": "+str(min_len_a)+"\n")
        f_out.write("Max. Document Length " + a_tag + ": " + str(max_len_a) + "\n")
        f_out.write("Mean Document Length " + a_tag + ": " + str(mean_len_a) + "\n\n")

        f_out.write("Min. Document Length " + b_tag + ": " + str(min_len_b) + "\n")
        f_out.write("Max. Document Length " + b_tag + ": " + str(max_len_b) + "\n")
        f_out.write("Mean Document Length " + b_tag + ": " + str(mean_len_b) + "\n\n-----------------------------\n\n")

        # Pair Stats
        f_out.write("Pair Statistics\n\n")

        f_out.write(a_tag + " longer than "+ b_tag +": " + str(a_longer_than_b) + " - " + str(a_longer_than_b/amount_pairs) + "%\n")
        f_out.write("Length of " + a_tag + " and " + b_tag + " equal: " + str(a_equal_b) + " - " + str(a_equal_b / amount_pairs) + "%\n")
        f_out.write(b_tag + " longer than " + a_tag + ": " + str(b_longer_than_a) + " - " + str(b_longer_than_a / amount_pairs) + "%\n\n-----------------------------\n\n")

        # Difference Stats
        f_out.write("Length Difference Statistics\n\n")

        f_out.write("Min. Document Difference: " + str(min_len_diff) + "\n")
        f_out.write("Max. Document Difference: " + str(max_len_diff) + "\n")
        f_out.write("Mean Document Difference: " + str(mean_len_diff) + "\n")
        f_out.write("Absolute Doc. Difference: " + str(absolute_mean_len_diff) +"\n\n")

        f_out.write("Min. Document Difference (Perc): " + str(min_len_perc_diff) + "\n")
        f_out.write("Max. Document Difference (Perc): " + str(max_len_perc_diff) + "\n")
        f_out.write("Mean Document Difference (Perc): " + str(mean_len_diff_perc) + "\n")
        f_out.write("Absolute Doc. Difference (Perc): " + str(absolute_mean_len_diff_perc) + "\n\n-----------------------------\n\n")

        # Reduction Stats
        f_out.write("Reduction Statistics\n\n")

        f_out.write("Articles of Length <50: " + str(smaller_50) + "\n")
        f_out.write("Pairs with at least one article Length <50: " + str(pair_smaller_50) + "\n" )
        f_out.write("Pairs with Perc Length Difference > 2x: " + str(twice_as_long) + "\n\n-----------------------------\n\n")

        # Amount of words (A,B,Corpus)
        f_out.write("Dictionary Statistics\n\n")

        f_out.write("Amount of words in " + a_tag+": " + str(amount_words_a) + "\n")
        f_out.write("Amount of words in " + b_tag + ": " + str(amount_words_b) + "\n")
        f_out.write("Amount of words in Corpus: " + str(amount_words_corp) + "\n")
        f_out.write("Amount of words in " + a_tag + " and " + b_tag + ": " + str(shared_words_unique) + " - " + str(shared_words_unique/amount_words_corp)+"% of all words\n")
        f_out.write("Avg. Amount of words shared per pair: " + str(common_words_per_pair) + " words\n\n-----------------------------\n\n")

        # Amount of unique words in a doc min,max,avg (A,B,Corpus)
        f_out.write("Unique Words Statistics\n\n")

        f_out.write("Min. Amount of unique words " + a_tag + ": " + str(min_uniq_a) + "\n")
        f_out.write("Max. Amount of unique words " + a_tag + ": " + str(max_uniq_a) + "\n")
        f_out.write("Mean Amount of unique words " + a_tag + ": " + str(mean_uniq_a) + "\n\n")

        f_out.write("Min. Amount of unique words " + b_tag + ": " + str(min_uniq_b) + "\n")
        f_out.write("Max. Amount of unique words " + b_tag + ": " + str(max_uniq_b) + "\n")
        f_out.write("Mean Amount of unique words " + b_tag + ": " + str(mean_uniq_b) + "\n\n-----------------------------\n\n")

        # Top 20 words of A,B, Corpus
        f_out.write("Top 20 words of "+a_tag+"\n\n")
        for i,item in enumerate(top20_a):
            f_out.write(str(i+1)+". " + str(item[0]) + " - "+ str(item[1]["freq_a"]) + " appearences in " +str(item[1]["in_a"])+ " documents - " +str(item[1]["in_a"]/amount_pairs)+ "%\n")

        f_out.write("\nTop 20 words of " + b_tag + "\n\n")
        for i,item in enumerate(top20_b):
            f_out.write(str(i+1)+". " + str(item[0]) + " - "+ str(item[1]["freq_b"]) + " appearences in " +str(item[1]["in_b"])+ " documents - " +str(item[1]["in_b"]/amount_pairs)+ "%\n")

        f_out.write("\nTop 20 words of corpus\n\n")
        for i, item in enumerate(top20_corp):
            f_out.write(str(i+1) + ". " + str(item[0]) + " - " + str(item[1]["freq_global"]) + " appearences in " + str(
                item[1]["in_a"]+item[1]["in_b"]) + " documents - " + str((item[1]["in_a"]+item[1]["in_b"]) / (2 * amount_pairs)) + "%\n")

def plot_corpus_stats(namespace, format="png", *args, **kwargs):
    plt.style.use('seaborn-paper')
    plt.rc('text', usetex=True)

    data_sets = namespace["data_sets"]
    for data_set in data_sets:
        # if data_set["path"].endswith("cleaned.tsv"):
        #    print("Skipped: "+data_set["path"])
        #    continue

        file_path = data_set["path"]

        base_plotpath = build_basepath("plots", namespace, subfolder = ".".join(file_path.strip().split("/")[-1].split(".")[:-1]))

        a_lens, b_lens, len_diffs, len_diffs_perc,\
        global_dict, uniq_words_a, uniq_words_b = load_dump_data(file_path=file_path,
                                                   formatted=data_set["formatted"],
                                                   index_a=data_set["index_a"],
                                                   index_b=data_set["index_b"],
                                                   *args, **kwargs)

        write_stat_overview(base_plotpath + "stats.txt", namespace, a_lens, b_lens, len_diffs, len_diffs_perc, global_dict, uniq_words_a, uniq_words_b)

        # Word Frequency Plots
        fig, ax = plt.subplots(figsize=(5.7,3))
        ax = plt.gca()
        ax.set_xlabel("Word Rank")
        file_name = "word_frequency_global"
        ax.set_xscale("log")
        ax.set_yscale("log")
        plot_word_frequency(ax, global_dict, key="freq_global", linewidth=2)
        fig.tight_layout()
        fig.savefig(base_plotpath + file_name + "." + format, format=format)

        fig, ax = plt.subplots(figsize=(5.7,3))
        ax = plt.gca()
        ax.set_xlabel("Word Rank")
        ax.set_xscale("log")
        ax.set_yscale("log")
        file_name = "word_frequency_" + namespace["tag_coll_a"] + "_" + namespace["tag_coll_b"]
        plot_word_frequency(ax, global_dict, key="freq_a", color="r", linewidth=2, label= namespace["tag_coll_a"] + " Words")
        plot_word_frequency(ax, global_dict, key="freq_b", color="b", linewidth=2, label= namespace["tag_coll_b"] + " Words")
        ax.legend()
        fig.tight_layout()
        fig.savefig(base_plotpath + file_name + "." + format, format=format)
        fig.savefig(base_plotpath + file_name + ".pdf", format="pdf")

        plt.clf()

        ''' Disabled
        # Document Length Distribution
        plt.figure()
        file_name = namespace["tag_coll_a"] + "_distribution_max1000"
        title = namespace["tag_coll_a"].upper() + " length distribution"
        plot_histogram(a_lens, mode="a", bin_to=1000)
        plt.xlabel("Document Length")
        # plt.title(title)
        plt.savefig(base_plotpath+file_name+"."+format,format=format)

        plt.figure()
        file_name = namespace["tag_coll_b"] + "_distribution_max1000"
        title = namespace["tag_coll_b"].upper() + " length distribution"
        plot_histogram(b_lens, mode="b", bin_to=1000)
        plt.xlabel("Document Length")
        # plt.title(title)
        plt.savefig(base_plotpath + file_name + "." + format, format=format)


        # Length Difference Distribution
        plt.figure()
        file_name = "diff_distribution_sbs1000"
        title = namespace["tag_coll_a"].upper()+"/"+namespace["tag_coll_b"].upper()+" length difference distribution"
        plot_diff_histogram(len_diffs, display_mode="sbs", namespace=namespace, bin_from=-1000, bin_to=1000, bin_gran=100)
        plt.xlabel("Pairwise length difference")
        # plt.title(title)
        plt.savefig(base_plotpath + file_name + "." + format, format=format)

        # Document Length CDF
        plt.figure()
        file_name = namespace["tag_coll_a"] + "_cdf_log"
        title = namespace["tag_coll_a"].upper() + " length CDF"
        plot_cdf(a_lens, mode="a")
        # plt.title(title)
        plt.xlabel("Document Length")
        plt.xscale("log")
        plt.yscale("log")
        plt.savefig(base_plotpath+file_name+"."+format,format=format)

        plt.figure()
        file_name = namespace["tag_coll_b"] + "_cdf_log"
        title = namespace["tag_coll_b"].upper() + " length CDF"
        plot_cdf(b_lens, mode="b")
        plt.xlabel("Document Length")
        # plt.title(title)
        plt.xscale("log")
        plt.yscale("log")
        plt.savefig(base_plotpath+file_name+"."+format,format=format)

        # Length Difference CDF
        plt.figure()
        file_name = "diffs_cdf"
        title = namespace["tag_coll_a"].upper()+"/"+namespace["tag_coll_b"].upper()+" length difference CDF"
        plot_diff_cdf(len_diffs, namespace=namespace)
        # plt.title(title)
        plt.xlabel("Pairwise length difference")
        plt.xscale("log")
        plt.yscale("log")
        plt.savefig(base_plotpath+file_name+"."+format,format=format)

        plt.figure()
        file_name = namespace["tag_coll_a"] + "_cdf_log_cut"
        title = namespace["tag_coll_a"].upper() + " length CDF"
        plot_cdf(a_lens, mode="a", cutoff=[50])
        # plt.title(title)
        plt.xlabel("Document Length")
        plt.xscale("log")
        plt.yscale("log")
        plt.savefig(base_plotpath+file_name+"."+format,format=format)

        plt.figure()
        file_name = namespace["tag_coll_b"] + "_cdf_log_cut"
        title = namespace["tag_coll_b"].upper() + " length CDF"
        plot_cdf(b_lens, mode="b", cutoff=[50])
        # plt.title(title)
        plt.xlabel("Document Length")
        plt.xscale("log")
        plt.yscale("log")
        plt.savefig(base_plotpath+file_name+"."+format,format=format)
        '''

        plt.figure(figsize=(5.7,3))
        file_name = namespace["tag_coll_a"] + "_" + namespace["tag_coll_b"] + "_cdf_log_cut"
        plot_cdf(b_lens, mode="b", cutoff=[50],label=True)
        plot_cdf(a_lens, mode="a", label=True)
        plt.xscale("log")
        plt.yscale("log")
        plt.legend(loc="lower right")
        ax = plt.gca()
        ax.set_xlabel("Document Length")
        plt.tight_layout()
        plt.savefig(base_plotpath + file_name + "." + format, format=format)
        plt.savefig(base_plotpath + file_name + ".pdf", format="pdf")
        plt.clf()


        # Percentual Length Difference CDF
        plt.figure(figsize=(5.7,3))
        file_name = "diffs_cdf_perc_total"
        title = namespace["tag_coll_a"].upper()+"/"+namespace["tag_coll_b"].upper()+" Percentual length difference CDF"
        plot_diff_cdf(len_diffs_perc, namespace=namespace, at_x=[1])
        # plt.title(title)
        plt.xlim([0, 3])
        plt.xlabel("Pairwise percentual length difference")
        plt.tight_layout()
        plt.savefig(base_plotpath+file_name+"."+format,format=format)
        plt.savefig(base_plotpath + file_name + ".pdf", format="pdf")
        plt.clf()

        '''
        plt.figure()
        file_name = "diffs_cdf_perc_total_threshold"
        title = namespace["tag_coll_a"].upper() + "/" + namespace[
            "tag_coll_b"].upper() + " Percentual length difference CDF"
        plot_diff_cdf(len_diffs_perc, namespace=namespace)
        # plt.title(title)
        plt.xlim([0, 1])
        plt.xlabel("Pairwise percentual length difference")
        plt.savefig(base_plotpath + file_name + "." + format, format=format)
        '''

        # Difference Frequency Distribution
        plt.figure(figsize=(5.7,3))
        file_name = "diff_counts_cut-2"
        title = namespace["tag_coll_a"].upper()+"/"+namespace["tag_coll_b"].upper()+" overhead cases"
        plot_counts(len_diffs_perc, namespace, cutoff=[-2, 2])
        plt.xlim([-0.5, 2])
        # plt.title(title)
        plt.tight_layout()
        plt.savefig(base_plotpath+file_name+"."+format,format=format)
        plt.savefig(base_plotpath + file_name + ".pdf", format="pdf")
        plt.close("all")

        if namespace["mode"] != "wiki":
            sources_a, sources_b, sources_pair = load_sources(file_path,namespace)

            # Source Frequency Distribution
            plt.figure(figsize=(5.7,3))
            file_name = "source_dist_"+namespace["tag_coll_a"]
            plot_sources_dist(sources_a,namespace)
            plt.savefig(base_plotpath + file_name + "." + format, format=format)
            plt.savefig(base_plotpath + file_name + ".pdf", format="pdf")
            plt.clf()

            plt.figure(figsize=(5.7,3))
            file_name = "source_dist_" + namespace["tag_coll_b"]
            plot_sources_dist(sources_b, namespace)
            plt.savefig(base_plotpath + file_name + "." + format, format=format)
            plt.savefig(base_plotpath + file_name + ".pdf", format="pdf")
            plt.clf()

            plt.figure(figsize=(5.7,5))
            plt.axes().set_aspect('equal')
            file_name = "source_dist_pairs"
            plot_pair_matrix(sources_a, sources_b, sources_pair, namespace)
            plt.savefig(base_plotpath + file_name + "." + format, format=format, dpi=600)
            plt.savefig(base_plotpath + file_name + ".pdf", format="pdf")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        raise IOError("Overspecified")
    print("STARTED")

    namespace = load_namespace("wiki")
    plot_corpus_stats(namespace)

    namespace = load_namespace("er-US")
    plot_corpus_stats(namespace)

    namespace = load_namespace("er-UK")
    plot_corpus_stats(namespace)

    print("FINISHED")