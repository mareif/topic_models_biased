import  sys
from code.helper import Timer
import multiprocessing as mp

'''
Add the article content to the the Title/ID pairs

Input:  ../../data/pairs/de_en_pairs.tsv
        ../../data/en/en_articles.tsv
        ../../data/de/de_articles.tsv
Output: ../../data/final/wiki_dataset_cleaned.tsv
'''

def load_pairs():
    en_ids = set()
    de_ids = set()
    pairs = []
    with open("../../data/pairs/de_en_pairs.tsv", "r", encoding="utf8") as f_in:
        f_in.readline()
        for line in f_in:
            splits = line.strip().split("\t")
            en_ids.add(int(splits[0]))
            de_ids.add(int(splits[2]))
            pairs.append(tuple(splits))
    print("Loaded pairs")
    return en_ids, de_ids, pairs

def get_textlines(articles_path, id_list):
    init_length=len(id_list)
    with open(articles_path, "r", encoding="utf8") as f_in:
        offset = len(bytes(f_in.readline(),"utf8"))+1
        line_offset = dict()
        for line in f_in:
            article_id = int(line[0:line.index("\t")].strip())
            if article_id in id_list:
                id_list.remove(article_id)
                line_offset[article_id]=offset
                if len(id_list)==0:
                    break
            offset += len(bytes(line,"utf8"))+1
        print("Unmatched: " + str(len(id_list)/init_length))
        # All unmatched documents are one of those: Categories, Help pages, Forwarding pages
        # -> They get dropped by the wiki extraction because they got no text content
    return line_offset

def attach_text(en_offsets, de_offsets, pairs, no_go_list, lock, write_buffer = 200):

    pair_counter = 0
    out_text = ""

    for pair in pairs:
        en_id = int(pair[0])
        en_title = pair[1]
        de_id = int(pair[2])
        de_title = pair[3]

        if en_id in no_go_list["en"] or de_id in no_go_list["de"]:
            continue

        with open("../../data/de/de_articles.tsv", "r", encoding="utf8") as f_de:
            f_de.seek(de_offsets[de_id])
            de_line = f_de.readline()
            de_splits = de_line.strip().split("\t")
            assert(int(de_splits[0])==de_id)
            de_text=de_splits[-1]

        with open("../../data/en/en_articles.tsv", "r", encoding="utf8") as f_en:
            f_en.seek(en_offsets[en_id])
            en_line = f_en.readline()
            en_splits = en_line.strip().split("\t")
            assert (int(en_splits[0]) == en_id)
            en_text = en_splits[-1]

        out_text += str(en_id) + "\t" + en_title + "\t" + en_text + "\t" + str(de_id) + "\t" + de_title + "\t" + de_text + "\n"
        pair_counter+=1

        if pair_counter>=write_buffer:
            with lock:
                with open("../../data/final/wiki_dataset_cleaned.tsv", "a", encoding="utf8") as f_out:
                    f_out.write(out_text)
            out_text=""
            pair_counter=0

    if pair_counter > 0:
        with lock:
            with open("../../data/final/wiki_dataset_cleaned.tsv", "a", encoding="utf8") as f_out:
                f_out.write(out_text)


def add_text_to_pairs(process_count = 15):
    en_ids, de_ids, pairs = load_pairs()
    timer = Timer()
    line_offset_de = get_textlines("../../data/de/de_articles.tsv", de_ids)
    with open("../../data/de/Missing_DE.tsv","w",encoding="utf8") as out:
        out.write(str(de_ids))
    print("Loaded all DE text")

    line_offset_en = get_textlines("../../data/en/en_articles.tsv", en_ids)
    with open("../../data/en/Missing_EN.tsv","w",encoding="utf8") as out:
        out.write(str(en_ids))
    print("Loaded all EN text")

    # All unmatchable documents (one of those: Categories, Help pages, Forwarding pages)
    # So they can be skipped
    no_go_list = {"de":de_ids ,"en":en_ids}

    with open("../../data/final/wiki_dataset_cleaned.tsv", "w", encoding="utf8") as f_out:
        f_out.write("%en_id\ten_title\ten_text\tde_id\tde_title\tde_text\n")

    processes = []
    lock = mp.Lock()

    # Select subset of pairs
    amount_of_pairs = len(pairs)
    amount_per_process = amount_of_pairs//(process_count-1)
    amount_assinged = 0
    for i in range(1,process_count):
        # Init n-1 processes
        process_load = pairs[(i-1)*amount_per_process:(i*amount_per_process)]
        p = mp.Process(target=attach_text,args=(line_offset_en, line_offset_de,process_load, no_go_list, lock))
        p.start()
        processes.append(p)
        print("Started: "+str((i-1)*amount_per_process)+" to "+str(i*amount_per_process))
        amount_assinged += len(process_load)

    # Init last process
    process_load = pairs[ ((process_count-1) * amount_per_process):]
    p = mp.Process(target=attach_text, args=(line_offset_en, line_offset_de,process_load, no_go_list, lock))
    p.start()
    processes.append(p)
    amount_assinged += len(process_load)
    print("Started: " + str((process_count-1) * amount_per_process) + " to END")

    print("Assigned: "+str(amount_assinged)+ " - Started: "+str(len(pairs)))

    assert(amount_assinged==len(pairs))
    print("All processes started")

    for proc in processes:
        proc.join()
    timer.timestamp()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        raise IOError("Overspecified")
    print("STARTED")

    add_text_to_pairs()

    print("FINISHED")