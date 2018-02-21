import matplotlib.pyplot as plt
import numpy as np
from code.helper import build_basepath, rel_size_iteration_loop
import pickle
import seaborn as sns

def to_float_string(number):
    return str((int(number*100))/100)

def output_latex_table(x_values, data, num_topics, namespace):
    a_prop, shared_prop, b_prop = data
    print("\\begin{table}[H]")
    print("\centering")
    print("\\begin{tabular}{ l || r | r | r}")
    print("Prop. Training & Prop. '"+namespace["tag_coll_a"]+"' & Prop. shared & Prop. '"+namespace["tag_coll_b"]+"' \\\\ \hline")
    for x in x_values:
        print(str(x) + " & " +to_float_string(a_prop[x][0])
                     + " & " +to_float_string(shared_prop[x][0])
                     + " & " +to_float_string(b_prop[x][0]) + " \\\\")
    print("\\end{tabular}")
    print("\\caption{"+namespace["global_namespace"]+" corpus - "+str(num_topics)+" Topics}")
    print("\\label{tab:"+namespace["global_namespace"]+"_topic_dist_data_"+str(num_topics)+"}")
    print("\\end{table}")

def norm_inference_sum(inference):
    # Normalize document wise
    inference = np.array(inference)
    row_sums = inference.sum(axis=1)
    inference_data = inference / row_sums[:, np.newaxis]

    # Sum all documents
    accu_inference = inference_data.sum(axis=0)
    return accu_inference

def calculate_deviation_stats(samples):
    mean = np.mean(samples)
    std_error = np.std(samples,ddof=1)
    return mean, std_error

def deviation_stats_inference(inference_data):
    perc_a, perc_b, perc_undef = list(zip(*inference_data))
    dev_stats_a = calculate_deviation_stats(perc_a)
    dev_stats_b = calculate_deviation_stats(perc_b)
    dev_stats_undef = calculate_deviation_stats(perc_undef)
    return [dev_stats_a,dev_stats_b, dev_stats_undef]

def load_topic_group_data(base_path, relative_sizes, iterations, num_topics):
    data = dict()
    # Iterate over directories
    for rel_size, i, adj_path in rel_size_iteration_loop(relative_sizes, iterations, base_path):
        if rel_size not in data.keys():
            data[rel_size] = []

        with open(adj_path + "eval/lda_" + str(num_topics) + "_inf_a.p","rb") as f_a:
            inference_a = pickle.load(f_a)

        with open(adj_path + "eval/lda_" + str(num_topics) + "_inf_b.p","rb") as f_b:
            inference_b = pickle.load(f_b)

        inference_sum_a = norm_inference_sum(inference_a[0])
        inference_sum_b = norm_inference_sum(inference_b[0])
        inference_sum_both = inference_sum_a + inference_sum_b

        assinged_a = (inference_sum_a / inference_sum_both) >= 0.9
        assinged_b = (inference_sum_b / inference_sum_both) >= 0.9
        not_assigned = np.logical_not(np.logical_or(assinged_a, assinged_b))

        amount_a = sum(assinged_a)
        amount_b = sum(assinged_b)
        amount_undef = sum(not_assigned)
        assert (amount_a + amount_b + amount_undef == num_topics)

        data[rel_size].append((amount_a/num_topics, amount_b/num_topics, amount_undef/num_topics))
    return data

def load_inference_data(namespace, sample_size, num_topics):
    base_path = build_basepath("samples", namespace, sample_size)
    inference_data = load_topic_group_data(base_path, relative_sizes, iterations, num_topics)

    # Init X-values (relative_size)
    x_values = sorted(list(inference_data.keys()))

    # Init plot 1 data
    red_y = []
    purple_y = []
    blue_y = []

    # Init plot 2 data
    a_prop = dict()
    b_prop = dict()
    shared_prop = dict()

    for x in x_values:
        deviation_stats = deviation_stats_inference(inference_data[x])
        print(deviation_stats)
        # Plot 1 - Data
        blue_y.append(deviation_stats[0][0] + deviation_stats[1][0] + deviation_stats[2][0])
        purple_y.append(deviation_stats[0][0] + deviation_stats[2][0])
        red_y.append(deviation_stats[0][0])

        # Plot 2 - Data
        a_prop[x], b_prop[x], shared_prop[x] = deviation_stats

    data_1 = (red_y, purple_y, blue_y)
    data_2 = (a_prop, shared_prop, b_prop)
    return x_values, data_1, data_2

def plot_topic_dist(x_values, data, ax):
    (red_y, purple_y, blue_y) = data

    sns.barplot(x=x_values, y=blue_y, color="blue", label=namespace["tag_coll_b"], ax=ax)
    # Overlap Shared amount
    sns.barplot(x=x_values, y=purple_y, color="purple", label="unassigned", ax=ax)
    #  Overlap A-only
    sns.barplot(x=x_values, y=red_y, color="red", label=namespace["tag_coll_a"], ax=ax)
    # ax.set_ylabel("Proportion")

def plot_topic_ratio(x_values, data, ax):
    a_prop, shared_prop, b_prop = data

    a_ratio = [a_prop[x][0] / x for x in x_values]
    b_ratio = [b_prop[x][0] / (1 - x) for x in x_values]
    b_ratio.reverse()

    # Plot Plot 2
    ax.plot(x_values, a_ratio, linewidth=2, color="red", label=namespace["tag_coll_a"])
    ax.plot(x_values, b_ratio, linewidth=2, color="blue", label=namespace["tag_coll_b"])

def plot_topic_group_distribution_triple(relative_sizes, sample_size, iterations, namespace, num_topics):
    plt.style.use('seaborn-paper')
    plt.rc('text', usetex=True)

    plot_path = build_basepath("plots", namespace, sample_size, appendix="-" + str(iterations) + "i")

    # Load data
    data_1_all = []
    data_2_all = []
    x_values = []
    # Load data
    for topics in num_topics:
        x_values, data_1, data_2 = load_inference_data(namespace, sample_size, topics)
        data_1_all.append(data_1)
        data_2_all.append(data_2)
        output_latex_table(x_values, data_2, topics, namespace)

    # Plot 1
    # f, axarr = plt.subplots(3, figsize=(2.2, 7), sharex=True, sharey=True)
    f, axarr = plt.subplots(1,3, figsize=(9,2), sharey=True)

    for index, topics in enumerate(num_topics):
        current_ax = axarr[index]
        plot_topic_dist(x_values, data_1_all[index], current_ax)
        current_ax.set_title(str(topics) + ' Topics')
        #current_ax.set_xlim(0.1, 0.9)
        current_ax.set_ylim(0, 1)

    legend_ax = axarr[1]
    handles, labels = legend_ax.get_legend_handles_labels()
    handles = [handles[2], handles[1], handles[0]]
    labels = [labels[2], labels[1], labels[0]]
    # Set x limits
    lgd = legend_ax.legend(handles=handles, labels=labels, bbox_to_anchor=(0., 1.13, 1., .102), loc=3, ncol=3, mode="expand",
                          borderaxespad=0.)

    # Set axis labels
    # axarr[-1].set_xlabel("Perc. of '" + namespace["tag_coll_a"] + "' docs in training corpus")

    axarr[1].set_xlabel("Percentage of group's documents in the trainings corpus")
    axarr[0].set_ylabel("Proportion")

    f.savefig(plot_path + "lda_all_topic_dist_triple.png", bbox_extra_artists=(lgd,), bbox_inches='tight')
    f.savefig(plot_path + "lda_all_topic_dist_triple_triple.pdf", bbox_extra_artists=(lgd,), bbox_inches='tight',
              format="pdf")

    # Plot 2
    # f2, axarr2 = plt.subplots(1,3, figsize=(5, 7), sharex=True, sharey=True)
    f2, axarr2 = plt.subplots(1,3, figsize=(9, 2) ,sharey=True)

    for index, topics in enumerate(num_topics):
        current_ax = axarr2[index]
        plot_topic_ratio(x_values, data_2_all[index], current_ax)
        current_ax.set_title(str(topics) + ' Topics')
        current_ax.set_xlim(0.1, 0.9)
        current_ax.set_ylim(0, 1)

    # Set x limits
    lgd2 = axarr2[1].legend(bbox_to_anchor=(0., 1.13, 1., .102), loc=3, ncol=2,
                           mode="expand",
                           borderaxespad=0.)
    # Set axis labels
    #axarr2[-1].set_xlabel("Percentage of group's documents in the trainings corpus")
    axarr2[0].set_ylabel("Topic/Corpus Ratio")
    axarr2[1].set_xlabel("Percentage of group's documents in the trainings corpus")

    f2.savefig(plot_path + "lda_all_topic_ratio_triple.png", bbox_extra_artists=(lgd2,), bbox_inches='tight')
    f2.savefig(plot_path + "lda_all_topic_ratio_triple_triple.pdf", bbox_extra_artists=(lgd2,), bbox_inches='tight',
              format="pdf")


if __name__ == "__main__":
    from code.helper.load_namespace import load_namespace

    relative_sizes = [x / 100 for x in range(10, 100, 10)]
    iterations = 50
    num_topics = [64, 128, 256]

    namespace = load_namespace("wiki")
    sample_size = 20000
    plot_topic_group_distribution_triple(relative_sizes, sample_size, iterations, namespace, num_topics)

    namespace = load_namespace("er-UK")
    sample_size = 10000
    plot_topic_group_distribution_triple(relative_sizes, sample_size, iterations, namespace, num_topics)

    namespace = load_namespace("er-US")
    sample_size = 4000
    plot_topic_group_distribution_triple(relative_sizes, sample_size, iterations, namespace, num_topics)
