import os
from random import shuffle
from code.helper import load_sources

'''
Pair the articles and build the first version of the data set.
Articles are still unprocessed and can occur multiple times.

An event can contain articles from multiple left and right sources.
The pairing behavior can be controlled with the "pairing_behaviour" parameter:
"default": By order of occurrence in the event data
"by_length": By length of article
"random": Pair randomly

Input:  ../../data/news_sources/*source lists*
        ../../data/article_data/*event_id*.art (multiple)
Output: *dataset@outpath*.tsv
'''

class pair_iterator(object):
    def __init__(self, path, sources_left, sources_right, pairing_behaviour="default"):
        self.path_attach = path if path.endswith("/") else path + "/"
        self.sources_left = sources_left
        self.sources_right = sources_right
        self.events = os.listdir(path)
        self.pairing_behaviour = pairing_behaviour

    def __iter__(self):
        for event in self.events:
            event_name = event.replace(".art", "")
            event_path = self.path_attach + event
            pairs = self.find_pairs(event_path)
            for pair in pairs:
                yield event_name, pair

    def _to_dict(self, line):
        fieldnames = ["article_id", "title", "url", "source_name", "article_text"]
        splits = line.strip().split("\t")
        assert (len(splits) == len(fieldnames))
        return dict(zip(fieldnames, splits))

    def __merge_duplicates(self,articles):
        a_seen = {}
        for i,article in enumerate(articles):
            article_id = article["article_id"]
            if a_seen.get(article_id)==None or a_seen[article_id]["length"]< len(article["article_text"]):
                a_seen[article_id] = {"length": len(article["article_text"]), "index": i}

        new_list = []
        for _, info in a_seen.items():
            new_list.append(articles[info["index"]])

        return new_list


    def build_pairs(self, articles_left, articles_right):
        # Check if an article occured twice in an event (e.g. got updated)
        # Clean inter-event duplicates
        articles_left = self.__merge_duplicates(articles_left)
        articles_right = self.__merge_duplicates(articles_right)

        if self.pairing_behaviour == "default":
            pairs = list(zip(articles_left, articles_right))
        elif self.pairing_behaviour == "by_length":
            s_left = sorted(articles_left,
                            key=lambda x: len(x["article_text"].split()),
                            reverse=True)
            s_right = sorted(articles_right,
                             key=lambda x: len(x["article_text"].split()),
                             reverse=True)
            pairs = list(zip(s_left, s_right))
        elif self.pairing_behaviour == "random":
            shuffle(articles_left)
            shuffle(articles_right)
            pairs = list(zip(articles_left, articles_right))
        else:
            raise ValueError("Pairing behaviour unknown")
        return pairs

    def find_pairs(self, event_path):
        articles_left = []
        articles_right = []
        with open(event_path, "r", encoding="utf8") as f_in:
            for line in f_in:
                article = self._to_dict(line)
                if article["source_name"] in self.sources_left:
                    articles_left.append(article)
                if article["source_name"] in self.sources_right:
                    articles_right.append(article)

        if len(articles_left) == 0 or len(articles_right) == 0:
            return []
        else:
            return self.build_pairs(articles_left, articles_right)


def build_dataset(outpath, left_outlets, right_outlets, pairing_behaviour="default"):
    pair_iter = pair_iterator("../../data/article_data/", left_outlets, right_outlets, pairing_behaviour)
    with open(outpath, "w", encoding="utf8") as f_in:
        f_in.write("event_id\t" +
                   "left_article_id\t" +
                   "left_source_name\t" +
                   "left_url\t" +
                   "left_title\t" +
                   "left_text\t" +
                   "right_article_id\t" +
                   "right_source_name\t" +
                   "right_url\t" +
                   "right_title\t" +
                   "right_text\n")

    with open(outpath, "a", encoding="utf8") as f_in:
        for event, pair in pair_iter:
            # Store as tsv
            f_in.write(event + "\t")
            f_in.write(pair[0]["article_id"] + "\t")
            f_in.write(pair[0]["source_name"] + "\t")
            f_in.write(pair[0]["url"] + "\t")
            f_in.write(pair[0]["title"] + "\t")
            f_in.write(pair[0]["article_text"] + "\t")
            f_in.write(pair[1]["article_id"] + "\t")
            f_in.write(pair[1]["source_name"] + "\t")
            f_in.write(pair[1]["url"] + "\t")
            f_in.write(pair[1]["title"] + "\t")
            f_in.write(pair[1]["article_text"] + "\t")
            f_in.write("\n")
    print("Finshed: " + outpath)

if __name__ == '__main__':
    data_set_path = "../../data/final/"
    if not os.path.exists(data_set_path):
        os.makedirs(data_set_path)

    news_sources = load_sources()

    # Random pairing behavior
    build_dataset(data_set_path+"UK_rand_pairs.tsv",
                  news_sources.left_uk,
                  news_sources.right_uk,
                  pairing_behaviour="random")
    build_dataset(data_set_path+"US_rand_pairs.tsv",
                  news_sources.left_us,
                  news_sources.right_us,
                  pairing_behaviour="random")
    build_dataset(data_set_path+"Mixed_rand_pairs.tsv",
                  news_sources.left,
                  news_sources.right,
                  pairing_behaviour="random")
