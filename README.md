# Topic Models on Biased Corpora

This git contains the code used during my master thesis "Topic Models on Biased Corpora". Text corpora tend to contain hidden meta groups. The size relation of these groups is frequently imbalanced. Their presence is often ignored when applying a topic model. Therefore, my thesis explores the influence of such imbalanced corpora on topic models.

The code is able to generate artificial imbalanced training samples from various data sets. Each sample contains two different groups whose size relation differ. These samples were used to train LDA. In the thesis the following data sets and respective group differences were used:

* Wikipedia (German vs English)
* UK articles (Left vs Right political orientation)
* US articles (Left vs Right political orientation)

The Wikipedia samples should show the effect of a large group difference, The Article samples should show the effect of a small group difference on a topic model. The predictive performance on those imbalanced corpora is judged using perplexity.

The following instructions will explain how to repeat the experiment. All required python modules are listed in the [requirements.txt](requirements.txt). The execution is build around an 8-core machine. In case you use less cores, you might want to adjust the amount of processes in the "run" functions.

## Data Acquisition

The git does not contain any data to repeat the experiment but it provides all necessary tools to reproduce the data sets.

### Wikipedia Data

Wikipedia creates regular data dumps. For the respective language versions, these dumps can be found at:

* [English Wikipedia Data](https://dumps.wikimedia.org/enwiki/latest/)
* [German Wikipedia Data](https://dumps.wikimedia.org/dewiki/latest/)

The article data (e.g. "enwiki-latest-pages-articles-multistream.xml.bz2") is the foundation of the Wikipedia data set. To remove the Wikipedia's formatting I used the [WikiExtractor](https://github.com/attardi/wikiextractor) with the following parameters:

```
python *path*/WikiExtractor.py *path-to-en-dataset* --processes 8 --output data\en\clean --bytes 1G --sections
python *path*/WikiExtractor.py *path-to-de-dataset* --processes 8 --output data\de\clean --bytes 1G --sections
```

During the experiment the articles need to be paired (to be able to control the concepts across both groups while varying the groups' relative size relation later in the experiment). The pairs are built using Wikipedia's language links (e.g. "enwiki-latest-langlinks.sql.gz"). The link data is expected to be decompressed as .sql at "data/en/original" or "data/de/original".

Using the WikiExtractor articles and language links, running [run_wiki_preprocessing](code/run/run_wiki_preprocessing.py) will create a data set of paired, stemmed and formated article pairs. Additionally, the unfiltered and non-formated version of that data set will be created.

### US/UK Article Data

The US and UK article data set were created using the service [Event Registry](http://eventregistry.org/). I was provided with a 5000 request license and collected articles over a timeframe of 3 months.

The functions follwing function need to be executed manually to obtain article data from Event Registry:

* [get_event_list](code/eventreg_preprocessing/get_event_list.py) (Get all events that contain at least one left AND right source)
* [acquire_data](code/eventreg_preprocessing/acquire_data.py) (Get articles from these events until you can build at least one pair)

Both programs require you to specify a valid Event Registry API key.

When the articles have been stored, running [run_wiki_preprocessing](code/run/run_er_preprocessing.py) will build the paired, stemmed and formated article pairs. Additionally, two non-formatted data sets will be created in between steps. One data set containing the raw pairs, another ensuring that each article only appears exactly once.


## Build Topic Models

To use a dataset in the experimental setup, various parameters of the dataset need to be specified manually in [load_namespace.py](code/helper/load_namespace.py).

* **global_namespace**: tag for the whole dataset (used in plots and file names) e.g. wikipedia
* **main_dataset**: dictionary; specifying data of the main data set
	* **path**: absolute path to the data set e.g. C:/biased_topic_models/wiki_ds_stemmed.tsv
	* **formatted**: bool; specifies if the articles are still raw (string) or already formatted (list of stemmed words + position identifier)
	* **title_a**: position of group A article title in .tsv
	* **title_b**: position of group B article title in .tsv
	* **index_a**: position of group A article content in .tsv
	* **index_b**: position of group A article content in .tsv
* **amount_pairs**: Amount of pairs in the dataset e.g. 386365 pairs in the Wikipedia dataset
* **tag_coll_a**: tag for group a (used in plots and file names) e.g. en for English
* **tag_coll_b**: tag for group b (used in plots and file names) e.g. de for German
* **data_sets**: list of additional datasets you want to compute stats for (needs: path, title_a, title_b, index_a, index_b; like "main_dataset")


Each namespace has its own identifier which needs to be used when topic modelling and plotting.

After setting up the namespace, you can execute [run_topic_modeling.py](code/run/run_topic_modeling.py). This program will perform the experiment. It will build a set of imbalanced samples (will controlling the high level concepts for one iteration), train a topic model and compute the perplexity of the test documents. The samples will be created in the following folder scheme:
`samples/dataset_name/sample_size/iteration/fraction_of_group_A`

It needs the following parameters:
* **relative_sizes**: list of fractions group A documents should provide for a sample e.g. `[0.1,0.5,0.9]`
* **sample_size**: size of a sample e.g. 20.000 documents
* **iterations**: amount of samples that should be created e.g. 50 iterations
* **namespace**: namespace of the dataset (see above)
* **num_topics**: list of amount of topics LDA should learn e.g. `[64,128,256]`
* **overwrite**: bool; specifies if already created samples should be overwritten
* **process_count**: amount of processes should be used at max (currently set to 8)


## Plotting

All plotting functions have to be executed manually. Corpus related plots will be created in `plots/dataset_name/general`; while experiment related plots will be created in `plots/dataset_name/samplesize-iterations/`.

Computing Corpus Stats + Plots:
* [plot_corpus_stats.py](code/plotting/plot_corpus_stats.py) - creates a dump tracking word occurences in a data set; computes general corpus statistics
* [plot_corpus_dictionary.py](code/plotting/plot_corpus_dictionary.py) - computes general dictionary statistcs (dump has to be created)

Computing Topic Model Stats + Plots (parameters need to match the ones used to build the topic models)
* [plot_vocab_mismatch.py](code/plotting/plot_vocab_mismatch.py) - plots vocabulary mismatch
* [plot_triple_stack_perplexity_adj.py](code/plotting/plot_triple_stack_perplexity_adj.py) - plots perplexity for the complete test corpus and for each group's test corpus
* [plot_triple_stack_topic_dist.py](code/plotting/plot_triple_stack_topic_dist.py) - plots the proportion of topics that could be assigned to a group


## Built With

* [WikiExtractor](https://github.com/attardi/wikiextractor) - Removing Wikipedia Formatting
* [Gensim](https://radimrehurek.com/gensim/) - LDA implementation and Perplexity calculations
* [NLTK](https://www.nltk.org/) - Snowball stemmer implementation and stopword removal
* [Matplotlib](https://matplotlib.org/) - Plotting
* [Seaborn](https://seaborn.pydata.org/) - Plotting

NLTK's default stopword lists were extended with:

* [German stopwords](https://github.com/solariz/german_stopwords/blob/master/german_stopwords_full.txt)
* [English stopwords](http://xpo6.com/list-of-english-stop-words/)


## License

This project is licensed under the GNU General Public License (GPLv3) - see the [LICENSE.md](LICENSE.md) file for details
