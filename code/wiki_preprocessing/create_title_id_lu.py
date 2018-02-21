import sys
from code.helper import Timer

'''
Creates a Title -> ID Lookup necessary to pair the Wikipedia articles
Wikipedia ID system only tracks one language version

Input:  ../../data/de/original/dewiki-latest-pages-articles-multistream.xml.bz2
        ../../data/en/original/enwiki-latest-pages-articles-multistream.xml.bz2
Output: ../../data/pairs/title-id-lookup_de.tsv
        ../../data/pairs/title-id-lookup_en.tsv
        ../../data/pairs/title-id-lookup.tsv
'''

out_file = None
def parse_articles(file_path):
    with open(file_path,"r",encoding="utf8") as f_in:
        f_in.readline()

        for line in f_in:
            (article_id, title) = line.strip().split("\t")[0:2]
            out_file.write(title + "\t" + article_id +"\n")

def initOutFile(out_path):
    global out_file
    out_file = open(out_path, 'w', encoding="utf8")
    out_file.write("title\tid\n")


def create_title_id_lu_lang(lang):
    global out_file
    if lang == 'de':
        file_path = '../../data/de/de_articles.tsv'
        initOutFile("../../data/pairs/title-id-lookup_de.tsv")
    elif lang == 'en':
        file_path = '../../data/en/en_articles.tsv'
        initOutFile("../../data/pairs/title-id-lookup_en.tsv")
    else:
        raise ValueError("Language unknown")

    parse_articles(file_path)
    out_file.close()

def mergeLookups():
    with open("../../data/pairs/title-id-lookup_de.tsv",'r',encoding="utf8") as f_in_de:
        f_in_de.readline()
        title_id_de = dict()
        for line in f_in_de:
            splits = line.strip().split("\t")
            # Store Title -> ID
            title_id_de[splits[0]]=int(splits[1])

    with open("../../data/pairs/title-id-lookup.tsv", 'w', encoding="utf8") as f_out:
        with open("../../data/pairs/title-id-lookup_en.tsv", 'r', encoding="utf8") as f_in_en:
            f_in_en.readline()
            f_out.write("%title\ten_id\tde_id\n")
            for line in f_in_en:
                splits = line.strip().split("\t")
                if title_id_de.get(splits[0])!=None:
                    # German title present, write: Title -> EN_id, DE_id
                    f_out.write(line.strip()+"\t"+str(title_id_de.pop(splits[0]))+"\n")
                else:
                    # No German title present, write: Title -> EN_id, __
                    f_out.write(line.strip() + "\tNone\n")
            for key,value in title_id_de.items():
                # Write remaining German only titles
                f_out.write(key+"\tNone\t"+str(value)+"\n")

def create_title_id_lu():
    timer = Timer()
    create_title_id_lu_lang("en")
    print("Finished English Lookup")
    create_title_id_lu_lang("de")
    print("Finished German Lookup")
    mergeLookups()
    timer.timestamp()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        raise IOError("Overspecified")
    print("STARTED")
    create_title_id_lu()
    print("FINISHED")
