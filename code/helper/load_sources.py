'''
Loads the left and right news sources
'''

class Sources():
    left_us = []
    left_uk = []
    right_us = []
    right_uk = []
    left = []
    right = []
    complete = []

    def __init__(self,
                 source_path="../../data/news_sources/",
                 left_us_path = "us_sources_left.txt",
                 right_us_path = "us_sources_right.txt",
                 left_uk_path="uk_sources_left.txt",
                 right_uk_path = "uk_sources_right.txt"):
        self.left_us = load_list(source_path + left_us_path)
        self.right_us = load_list(source_path + right_us_path)
        self.left_uk = load_list(source_path + left_uk_path)
        self.right_uk = load_list(source_path + right_uk_path)

        self.left = self.left_us + self.left_uk
        self.right = self.right_us + self.right_uk
        self.complete = self.left + self.right


def load_list(path):
    data = []
    with open(path,"r",encoding="utf8") as f_in:
        for line in f_in:
            data.append(line.strip())
    return data

def load_sources():
    return Sources()
