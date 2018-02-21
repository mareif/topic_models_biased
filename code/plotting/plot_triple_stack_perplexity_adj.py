import pickle
import matplotlib.pyplot as plt
import numpy as np
from code.helper import build_basepath, rel_size_iteration_loop

def calculate_deviation_stats(samples):
    mean = np.mean(samples)
    std_error = np.std(samples,ddof=1)
    return mean, std_error

def calculate_percentiles(samples):
    median = np.median(samples)
    perc_25 = np.percentile(samples,25)
    perc_75 = np.percentile(samples, 75)
    return perc_25, median, perc_75

def output_latex_table_one(x_values, data_a, num_topics, namespace):
    print("\\begin{table}[H]")
    print("\centering")
    print("\\begin{tabular}{ |l||r|r|r| }")
    print("& \multicolumn{3}{c||}{PP 'total'} \\\\")
    print("\hline")
    print("& 25th Perc. & Median & 75th Perc. \\\\ \hline")
    for index, x in enumerate(x_values):
        print(str(x) + " & " + str(int(data_a[0][index] // 1))
                     + " & " + str(int(data_a[1][index] // 1))
                     + " & " + str(int(data_a[2][index] // 1))
                     + " \\\\")
    print("\\end{tabular}")
    print("\\caption{ Total Perplexity - "+namespace["global_namespace"]+" corpus - "+str(num_topics)+" Topics}")
    print("\\label{tab:perplexity_"+namespace["global_namespace"]+"_total_"+str(num_topics)+"}")
    print("\\end{table}")

def output_latex_table_two(x_values, data_a, data_b, num_topics, namespace):
    print("\\begin{table}[H]")
    print("\centering")
    print("\\begin{tabular}{ |l||r|r|r||r|r|r| }")
    print("& \multicolumn{3}{c||}{PP '"+namespace["tag_coll_a"]+"'} & \multicolumn{3}{c}{PP '"+namespace["tag_coll_b"]+"'} \\\\")
    print("\hline")
    print("& 25th Perc. & Median & 75th Perc. & 25th Perc. & Median & 75th Perc. \\\\ \hline")
    for index, x in enumerate(x_values):
        print(str(x) + " & " + str(int(data_a[0][index] // 1))
                     + " & " + str(int(data_a[1][index] // 1))
                     + " & " + str(int(data_a[2][index] // 1))
                     + " & " + str(int(data_b[0][index] // 1))
                     + " & " + str(int(data_b[1][index] // 1))
                     + " & " + str(int(data_b[2][index] // 1))
                     + " \\\\")
    print("\\end{tabular}")
    print("\\caption{ Group Perplexity - "+namespace["global_namespace"]+" corpus - "+str(num_topics)+" Topics}")
    print("\\label{tab:perplexity_"+namespace["global_namespace"]+"_groups_"+str(num_topics)+"}")
    print("\\end{table}")

def load_data_lda(relative_sizes, sample_size, iterations, namespace,num_topics):
    # Load data
    base_path = build_basepath("samples", namespace, sample_size)
    data_a = dict()  # x -> [ys]
    data_b = dict()  # x -> [ys]
    data_all = dict()  # x -> [ys]
    for rel_size, i, adj_path in rel_size_iteration_loop(relative_sizes, iterations, base_path):
        if rel_size not in data_a.keys():
            data_a[rel_size] = []
            data_b[rel_size] = []
            data_all[rel_size] = []

        # True LDA Eval (no adj)
        with open(adj_path + "eval/adj_lda_"+str(num_topics)+"_a.p", "rb") as f_a:
            perpl_exponent = pickle.load(f_a)
            data_a[rel_size].append(np.exp2(-perpl_exponent))

        with open(adj_path + "eval/adj_lda_"+str(num_topics)+"_b.p", "rb") as f_b:
            perpl_exponent = pickle.load(f_b)
            data_b[rel_size].append(np.exp2(-perpl_exponent))

        with open(adj_path + "eval/adj_lda_"+str(num_topics)+"_all.p", "rb") as f_all:
            perpl_exponent = pickle.load(f_all)
            data_all[rel_size].append(np.exp2(-perpl_exponent))

    return data_a, data_b, data_all

def plot_triple_stack(relative_sizes, sample_size, iterations, namespace, num_topics):
    # Init plot folders
    plot_path = build_basepath("plots", namespace, sample_size, appendix="-" + str(iterations) + "i")
    # Load data
    data_a_triple = []
    data_b_triple = []
    data_all_triple = []
    for topics in num_topics:
        data_a, data_b, data_all = load_data_lda(relative_sizes, sample_size, iterations, namespace, topics)
        data_a_triple.append(data_a)
        data_b_triple.append(data_b)
        data_all_triple.append(data_all)

    # Plot perplexity
    plot_triple_stack_perpl_adj(data_a_triple, data_b_triple, data_all_triple, namespace, plot_path, "lda_all")
    plot_triple_stack_perpl_all(data_all_triple, namespace,plot_path, "lda_all")

def plot_perpl(x_values , results, ax, label, color="black", no_std=False):
    perc_25_all, median_all, perc_75_all = results
    # Fill space in background
    if not no_std:
        ax.fill_between(x_values, perc_25_all, perc_75_all, alpha=0.3, facecolor=color)
        # plot std
        ax.plot(x_values, perc_25_all, '--', color=color, linewidth=0.5,
                label= label+ " 25/75th Perc.")
        ax.plot(x_values, perc_75_all, '--', color=color, linewidth=0.5)
    # plot mean
    ax.plot(x_values, median_all, color=color, linewidth=2.0, label=label + " Median")
    ax.set_ylabel("Perplexity")

def plot_triple_stack_perpl_all(data_all_triple, namespace,plot_path, outname, format="png"):
    plt.style.use('seaborn-paper')
    plt.rc('text', usetex=True)

    # Set x values
    x_values = sorted(list(data_all_triple[0].keys()))

    median_stats_triple = []
    for data_all in data_all_triple:
        results = zip(*[calculate_percentiles(data_all[x]) for x in x_values])
        median_stats_triple.append(results)

    f, axarr = plt.subplots(3,figsize=(5, 7), sharex=True)

    for index, topics in enumerate(num_topics):
        current_ax = axarr[index]
        plot_perpl(x_values, median_stats_triple[index], current_ax, label="All Test")
        current_ax.set_title(str(topics)+' Topics')
        current_ax.set_xlim(0.1, 0.9)

    # Set x limits
    lgd = axarr[0].legend( bbox_to_anchor=(0., 1.15, 1., .13), loc=3, ncol=2, mode="expand",
                     borderaxespad=0.)

    # Set axis labels
    axarr[-1].set_xlabel("Percentage of '" + namespace["tag_coll_a"] + "' documents in the training corpus")
    f.savefig(plot_path + outname + "_perplexity_all_triple.png", bbox_extra_artists=(lgd,), bbox_inches='tight')
    f.savefig(plot_path + outname + "_perplexity_all_triple.pdf", bbox_extra_artists=(lgd,), bbox_inches='tight', format="pdf")

def plot_triple_stack_perpl_adj(data_a_triple, data_b_triple, data_all_triple, namespace, plot_path, outname, format="png"):
    plt.style.use('seaborn-paper')
    plt.rc('text', usetex=True)

    # Set x values
    x_values = sorted(list(data_a_triple[0].keys()))

    median_a_stats_triple = []
    for data_a in data_a_triple:
        results = list(zip(*[calculate_percentiles(data_a[x]) for x in x_values]))
        median_a_stats_triple.append(results)

    median_b_stats_triple = []
    for data_b in data_b_triple:
        results = list(zip(*[calculate_percentiles(data_b[x]) for x in x_values]))
        median_b_stats_triple.append(results)

    median_all_stats_triple = []
    for data_all in data_all_triple:
        results = list(zip(*[calculate_percentiles(data_all[x]) for x in x_values]))
        median_all_stats_triple.append(results)

    f, axarr = plt.subplots(3, figsize=(5, 7), sharex=True)

    for index, topics in enumerate(num_topics):
        output_latex_table_one(x_values, median_all_stats_triple[index], topics, namespace)
        # output_latex_table_two(x_values, median_a_stats_triple[index], median_b_stats_triple[index], topics, namespace)

        current_ax = axarr[index]
        plot_perpl(x_values, median_a_stats_triple[index], current_ax, label="'"+namespace["tag_coll_a"]+"' Test", color="red")
        plot_perpl(x_values, median_all_stats_triple[index], current_ax, label="Complete Corpus", no_std=True)
        plot_perpl(x_values, median_b_stats_triple[index], current_ax, label="'"+namespace["tag_coll_b"]+"' Test", color="blue")

        current_ax.set_title(str(topics) + ' Topics')
        current_ax.set_xlim(0.1, 0.9)

    # Set x limits
    lgd = axarr[0].legend(bbox_to_anchor=(0., 1.15, 1., .13), loc=3, ncol=2, mode="expand",
                          borderaxespad=0.)

    # Set axis labels
    axarr[-1].set_xlabel("Percentage of '" + namespace["tag_coll_a"] + "' documents in the training corpus")
    f.savefig(plot_path + outname + "_perplexity_triple.png", bbox_extra_artists=(lgd,), bbox_inches='tight')
    f.savefig(plot_path + outname + "_perplexity_triple.pdf", bbox_extra_artists=(lgd,), bbox_inches='tight',
              format="pdf")


if __name__ == "__main__":
    from code.helper.load_namespace import load_namespace

    relative_sizes = [x / 100 for x in range(10, 100, 10)]
    iterations = 50
    num_topics = [64, 128, 256]

    namespace = load_namespace("wiki")
    sample_size = 20000
    plot_triple_stack(relative_sizes, sample_size, iterations, namespace, num_topics)

    namespace = load_namespace("er-UK")
    sample_size = 10000
    plot_triple_stack(relative_sizes, sample_size, iterations, namespace, num_topics)

    namespace = load_namespace("er-US")
    sample_size = 4000
    plot_triple_stack(relative_sizes, sample_size, iterations, namespace, num_topics)

