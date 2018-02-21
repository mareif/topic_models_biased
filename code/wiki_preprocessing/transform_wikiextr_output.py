import sys
import re
import multiprocessing as mp
from code.helper import Timer

'''
Process the WikiExtractor output and format it to fit a tsv

Input:  ../../data/en/clean/wiki_xy
        ../../data/de/clean/wiki_xy

Output: ../../data/en/en_articles.tsv
        ../../data/de/de_articles.tsv
        ../../data/pairs/title-id-lookup.tsv
'''

# Generator
def iterate_xml(file_path):
    with open(file_path,"r",encoding="utf8") as f_in:
        reading = False
        doc_text = ""
        for line in f_in:
            if line.startswith("<doc "):
                reading=True
            elif line.startswith("</doc>"):
                yield doc_text
                reading=False
                doc_text=""

            if reading:
                doc_text+=line


def process_page(page):
    try:
        first_line = page[0:page.index("\n")]
    except ValueError:
        print(page)
        return

    article_id = first_line[first_line.index("id=")+4:first_line.index("url=")-2]
    article_title = first_line[first_line.index("title=")+7:-2]

    if not article_id or not article_title:
        raise ValueError("Could not find article title or id")

    article_text = page[page.index("\n"):]
    # Replace all non-word chars (except num and letters)
    # article_text = re.sub(r"[^\w\s]", '', article_text)
    # Replace all whitespace
    article_text = re.sub(r"\s+", ' ', article_text)

    # Sometimes there are still new lines (for whatever reason)
    article_text.replace("\n"," ").strip()
    return article_id + "\t" + article_title + "\t" + article_text + "\n"

def parse(lang, iteration, lock, write_buffer = 500):
    number_str = str(iteration)
    if len(number_str) == 1:
        number_str = "0" + number_str

    if lang=="en":
        file_path = '../../data/en/clean/wiki_'+number_str
        print("Working on: "+file_path)
    elif lang=="de":
        file_path = '../../data/de/clean/wiki_'+number_str
        print("Working on: " + file_path)
    else:
        print("Need language specification")
        return

    buffer_counter = 0
    gen = iterate_xml(file_path)
    output_string = ""
    output_string_lu = ""
    for elem in gen:
        page_string = process_page(elem)
        if page_string != None:
            output_string+=page_string
            output_string_lu+="\t".join(reversed(page_string.strip().split("\t")[:2]))+"\n" # Write title -> id lookup
            buffer_counter+=1
            if buffer_counter>=write_buffer:
                with lock:
                    if lang=="en":
                        with open("../../data/en/en_articles.tsv",'a', encoding="utf8") as f_out:
                            f_out.write(output_string)
                        with open("../../data/pairs/title-id-lookup_en.tsv",'a', encoding="utf8") as f_out_lu:
                            f_out_lu.write(output_string_lu)
                    else:
                        with open("../../data/de/de_articles.tsv",'a', encoding="utf8") as f_out:
                            f_out.write(output_string)
                        with open("../../data/pairs/title-id-lookup_de.tsv",'a', encoding="utf8") as f_out_lu:
                            f_out_lu.write(output_string_lu)
                buffer_counter=0
                output_string=""
                output_string_lu = ""

    if buffer_counter>0:
        with lock:
            if lang == "en":
                with open("../../data/en/en_articles.tsv", 'a', encoding="utf8") as f_out:
                    f_out.write(output_string)
                with open("../../data/pairs/title-id-lookup_en.tsv", 'a', encoding="utf8") as f_out_lu:
                    f_out_lu.write(output_string_lu)
            else:
                with open("../../data/de/de_articles.tsv", 'a', encoding="utf8") as f_out:
                    f_out.write(output_string)
                with open("../../data/pairs/title-id-lookup_de.tsv", 'a', encoding="utf8") as f_out_lu:
                    f_out_lu.write(output_string_lu)

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

def transform_wikiextr_output():

    timer = Timer()
    # Init out documents
    with open("../../data/en/en_articles.tsv", 'w', encoding="utf8") as f_out:
        f_out.write("% id\ttitle\ttext\n")
    with open("../../data/de/de_articles.tsv", 'w', encoding="utf8") as f_out:
        f_out.write("% id\ttitle\ttext\n")
    with open("../../data/pairs/title-id-lookup_en.tsv", 'w', encoding="utf8") as f_out_lu:
        f_out_lu.write("% title\tid\n")
    with open("../../data/pairs/title-id-lookup_de.tsv", 'w', encoding="utf8") as f_out_lu:
        f_out_lu.write("% title\tid\n")

    processes = []
    de_lock = mp.Lock()
    en_lock = mp.Lock()

    # Start parsing DE
    for i in range(0, 5):
        p = mp.Process(target=parse, args=('de', i, de_lock))
        p.start()
        processes.append(p)

    # Start parsing EN
    for i in range(0, 12):
        p = mp.Process(target=parse, args=('en', i, en_lock))
        p.start()
        processes.append(p)

    for proc in processes:
        proc.join()

    mergeLookups()

    timer.timestamp()

if __name__ == "__main__":
    if len(sys.argv)>1:
        raise IOError("Overspecified")
    print("STARTED")

    transform_wikiextr_output()

    print("FINISHED")