import sys
from code.helper import Timer

'''
Pair German and English articles
Can still contain bad link patterns

Input: ../../data/de/de-en-docs.txt
       ../../data/de/en-de-docs.txt
       ../../data/pairs/title-id-lookup.tsv
Output: ../../data/pairs/de_en_pairs_unfiltered.tsv
'''


def loadLookups():
    print("Loading Lookup")
    title_lookup = dict() # Title -> de_id, en_id
    de_id_lookup = dict() # de_id -> title
    en_id_lookup = dict() # en_id -> title
    with open("../../data/pairs/title-id-lookup.tsv", "r", encoding="utf8") as f_in:
        f_in.readline()
        for line in f_in:
            splits = line.strip().split("\t")
            if len(splits)<3:
                # Made a mistake while building, en_id 28644448 has no title
                continue

            title_lookup[splits[0]] = dict()
            if splits[1] == 'None':
                title_lookup[splits[0]]['en_id'] = None
            else:
                title_lookup[splits[0]]['en_id'] = int(splits[1])
                en_id_lookup[int(splits[1])] = splits[0]

            if splits[2] == 'None':
                title_lookup[splits[0]]['de_id'] = None
            else:
                title_lookup[splits[0]]['de_id'] = int(splits[2])
                de_id_lookup[int(splits[2])] = splits[0]
    print("Loaded Lookup")
    return title_lookup, de_id_lookup, en_id_lookup

def resolve_links(link_fp, title_lookup, id_lookup):
    global out_file
    global written_pairs
    with open(link_fp) as links:
        links.readline()
        for link in links:
            splits = link.strip().split("\t")
            start_id = int(splits[0])
            title_lang = splits[1].replace("'",'')
            goal_title = splits[2].replace("'",'')
            start_title = id_lookup.get(start_id)

            if goal_title=='' or start_title==None or title_lookup.get(goal_title)==None:
                # Remove if goal or start title empty or no ID found
                continue

            if title_lang=="en":
                if title_lookup[goal_title]["en_id"]==None:
                    continue
                goal_id = title_lookup[goal_title]["en_id"]
                out_string = str(goal_id) + "\t"  +goal_title + "\t" + str(start_id) + "\t" + start_title + "\n"
            elif title_lang=="de":
                if title_lookup[goal_title]["de_id"]==None:
                    continue
                goal_id = title_lookup[goal_title]["de_id"]
                out_string = str(start_id) + "\t" + start_title + "\t" + str(goal_id) + "\t" + goal_title + "\n"
            else:
                raise ValueError("Unexpected language specification")

            if out_string not in written_pairs:
                written_pairs.add(out_string)
                out_file.write(out_string)


def pair_articles():
    global out_file
    global written_pairs
    timer = Timer()
    written_pairs = set()
    title_lookup, de_id_lookup, en_id_lookup = loadLookups()
    out_file = open("../../data/pairs/de_en_pairs_unfiltered.tsv","w",encoding="utf8")
    out_file.write("en_id\ten_title\tde_id\tde_title\n")

    resolve_links("../../data/pairs/de-en-docs.txt", title_lookup,de_id_lookup)
    resolve_links("../../data/pairs/en-de-docs.txt", title_lookup, en_id_lookup)

    out_file.close()
    timer.timestamp()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        raise IOError("Overspecified")
    print("STARTED")
    pair_articles()
    print("FINISHED")