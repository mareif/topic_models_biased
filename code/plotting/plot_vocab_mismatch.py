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

def to_float_string(number):
    return str((int(number*100))/100)

def output_latex_table_two(x_values, data_a, data_b, num_topics, namespace):
    print("\\begin{table}[H]")
    print("\centering")
    print("\\begin{tabular}{ |l||r|r||r|r| }")
    print("& \multicolumn{2}{c||}{Voc. Mismatch '"+namespace["tag_coll_a"]+"'} & \multicolumn{2}{c}{Voc. Mismatch '"+namespace["tag_coll_b"]+"'} \\\\")
    print("\hline")
    print(namespace["tag_coll_a"] + " in Training & 25th Perc. & Median & 75th Perc. & 25th Perc. & Median & 75th Perc. \\\\ \hline")
    for index, x in enumerate(x_values):
        print(str(x) + " & " + str(int(data_a[0][index]))
                     + " & " + str(int(data_a[1][index]))
                     + " & " + str(int(data_b[0][index]))
                     + " & " + str(int(data_b[1][index]))
                     + " \\\\")
    print("\\end{tabular}")
    print("\\caption{ Group Perplexity - "+namespace["global_namespace"]+" corpus - "+str(num_topics)+" Topics}")
    print("\\label{tab:perplexity_"+namespace["global_namespace"]+"_groups_"+str(num_topics)+"}")
    print("\\end{table}")

def plot_vocab_mismatch(relative_sizes, sample_size, iterations, namespace, format="png"):
    plt.style.use('seaborn-paper')

    # Init plot folders
    plot_path = build_basepath("plots", namespace, sample_size, appendix="-" + str(iterations) + "i")

    # Load data
    base_path = build_basepath("samples", namespace, sample_size)
    data_a = dict()  # x -> [ys]
    data_b = dict()  # x -> [ys]
    for rel_size, i, adj_path in rel_size_iteration_loop(relative_sizes, iterations, base_path):
        if rel_size not in data_a.keys():
            data_a[rel_size] = []
            data_b[rel_size] = []

        with open(adj_path + "eval/mismatch_a.p", "rb") as f_a:
            prob_mismatch_per_doc = pickle.load(f_a)
            data_a[rel_size] += prob_mismatch_per_doc

        with open(adj_path + "eval/mismatch_b.p", "rb") as f_b:
            prob_mismatch_per_doc = pickle.load(f_b)
            data_b[rel_size] += prob_mismatch_per_doc

    # Set x values
    x_values = sorted(list(data_a.keys()))

    # ----------------
    # Plot Means + Std
    # ----------------

    # Calc stats for x values
    means_a, std_a = list(zip(*[calculate_deviation_stats(data_a[x]) for x in x_values]))
    means_b, std_b = list(zip(*[calculate_deviation_stats(data_b[x]) for x in x_values]))

    # Command Line output
    print(namespace["tag_coll_a"] + " Vocab Mismatch")
    for i in range(len(x_values)):
        print(str(x_values[i]) + " - " + str(means_a[i]) + " - " + str(std_a[i]))

    print("\n" + namespace["tag_coll_b"] + " Vocab Mismatch")
    for i in range(len(x_values)):
        print(str(x_values[i]) + " - " + str(means_b[i]) + " - " + str(std_b[i]))

    plt.rc('text', usetex=True)

    # Plot overlapping
    fig, ax = plt.subplots(figsize=(5.7,3))
    # Plot group A
    # Fill space in background
    ax.fill_between(x_values, np.array(means_a) + std_a, np.array(means_a) - std_a, alpha=0.3, facecolor="red")
    # plot mean
    ax.plot(x_values, means_a, color="red", linewidth=2.0, label=namespace["tag_coll_a"] + " mean")
    # plot std
    ax.plot(x_values, np.array(means_a) + std_a, '--', color="red", linewidth=0.5, label = namespace["tag_coll_a"] + " std")
    ax.plot(x_values, np.array(means_a) - std_a, '--', color="red", linewidth=0.5)

    # Plot group B
    # Fill space in background
    ax.fill_between(x_values, np.array(means_b) + std_b, np.array(means_b) - std_b, alpha=0.3, facecolor="blue")
    # plot mean
    ax.plot(x_values, means_b, color="blue", linewidth=2.0, label=namespace["tag_coll_b"] + " mean")
    # plot std
    ax.plot(x_values, np.array(means_b) + std_b, '--', color="blue", linewidth=0.5, label = namespace["tag_coll_b"] + " std")
    ax.plot(x_values, np.array(means_b) - std_b, '--', color="blue", linewidth=0.5)

    # Set x limits

    lgd = ax.legend( bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand",
                       borderaxespad=0.)
    ax.set_xlim(0.1,0.9)
    ax.set_ylim(0, 1)

    # Set axis labels
    ax.set_xlabel("Percentage of '"+namespace["tag_coll_a"]+"' documents in the training corpus")
    ax.set_ylabel("Proportion of Vocabulary Missmatch in a Test Document")

    fig.savefig(plot_path + "vocab_miss_mean.png", bbox_extra_artists=(lgd,), bbox_inches='tight')
    fig.savefig(plot_path + "vocab_miss_mean.pdf", bbox_extra_artists=(lgd,), bbox_inches='tight', format="pdf")
    # plt.show()

if __name__ == "__main__":
    from code.helper.load_namespace import load_namespace

    relative_sizes = [x / 100 for x in range(10, 100, 10)]
    iterations = 50
    num_topics = [64, 128, 256]

    namespace = load_namespace("wiki")
    sample_size = 20000
    plot_vocab_mismatch(relative_sizes, sample_size, iterations, namespace)

    namespace = load_namespace("er-UK")
    sample_size = 10000
    plot_vocab_mismatch(relative_sizes, sample_size, iterations, namespace)

    namespace = load_namespace("er-US")
    sample_size = 4000
    plot_vocab_mismatch(relative_sizes, sample_size, iterations, namespace)