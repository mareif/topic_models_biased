'''
Only keeps resolvable link patterns in the data set

Input:  ../../data/de/de-en-docs.txt
        ../../data/de/en-de-docs.txt
        ../../data/pairs/title-id-lookup.tsv
        ../../data/pairs/de_en_pairs_unfiltered.tsv

Output: ../../data/pairs/de_en_pairs.tsv
'''

def loadLookups():
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
    return title_lookup, de_id_lookup, en_id_lookup

def build_nodes(title_lookup, de_id_lookup, en_id_lookup):
    nodes_en = {}       # en_id -> {indegree, outdegree}
    nodes_de = {}       # de_id -> {indegree, outdegree}
    wiki_links = {}          # (en_id, de_id) -> [*directions*]

    for link_fp in ["../../data/pairs/de-en-docs.txt", "../../data/pairs/en-de-docs.txt"]:
        with open(link_fp) as links:
            links.readline()
            for link in links:
                splits = link.strip().split("\t")
                start_id = int(splits[0])
                title_lang = splits[1].replace("'", '')
                goal_title = splits[2].replace("'", '')

                if title_lang == "en":
                    start_title = de_id_lookup.get(start_id)
                elif title_lang == "de":
                    start_title = en_id_lookup.get(start_id)
                else:
                    raise ValueError("Unknown language tag")

                if goal_title == '' or start_title == None or title_lookup.get(goal_title) == None:
                    # Remove if goal or start title empty or no ID found
                    continue

                if title_lang == "en":
                    # DE -> EN
                    # de_id -> en_title
                    if title_lookup[goal_title]["en_id"] == None:
                        continue
                    goal_id = title_lookup[goal_title]["en_id"]
                    out_string = str(goal_id) + "\t" + goal_title + "\t" + str(start_id) + "\t" + start_title + "\n"
                    info = {"en_id":goal_id,"en_title":goal_title,"de_id":start_id,"de_title":start_title}

                    link = (info["en_id"],info["de_id"])
                    if wiki_links.get(link) == None:
                        wiki_links[link]=set()
                    wiki_links[link].add("de to en")

                    if nodes_en.get(info["en_id"]) == None:
                        nodes_en[info["en_id"]] = {"indegree":0, "outdegree":0, "to":[], "from":[]}
                    nodes_en[info["en_id"]]["indegree"] += 1
                    nodes_en[info["en_id"]]["from"].append(info["de_id"])

                    if nodes_de.get(info["de_id"]) == None:
                        nodes_de[info["de_id"]] = {"indegree":0, "outdegree":0, "to":[], "from":[]}
                    nodes_de[info["de_id"]]["outdegree"] += 1
                    nodes_de[info["de_id"]]["to"].append(info["en_id"])

                elif title_lang == "de":
                    # EN -> DE
                    # en_id -> de_title
                    if title_lookup[goal_title]["de_id"] == None:
                        continue
                    goal_id = title_lookup[goal_title]["de_id"]
                    out_string = str(start_id) + "\t" + start_title + "\t" + str(goal_id) + "\t" + goal_title + "\n"
                    info = {"en_id": start_id, "en_title": start_title, "de_id": goal_id, "de_title": goal_title}

                    link = (info["en_id"], info["de_id"])
                    if wiki_links.get(link) == None:
                        wiki_links[link] = set()
                    wiki_links[link].add("en to de")

                    if nodes_de.get(info["de_id"]) == None:
                        nodes_de[info["de_id"]] = {"indegree":0, "outdegree":0, "to":[], "from":[]}
                    nodes_de[info["de_id"]]["indegree"] += 1
                    nodes_de[info["de_id"]]["from"].append(info["en_id"])

                    if nodes_en.get(info["en_id"]) == None:
                        nodes_en[info["en_id"]] = {"indegree":0, "outdegree":0, "to":[], "from":[]}
                    nodes_en[info["en_id"]]["outdegree"] += 1
                    nodes_en[info["en_id"]]["to"].append(info["de_id"])
                else:
                    raise ValueError("Unexpected language specification")

    return nodes_de, nodes_en, wiki_links

def mark_for_removal(nodes_de, nodes_en, wiki_links, de_id_lookup, en_id_lookup):
    referencing_eachother = 0
    singlelink = 0
    removed = 0
    to_be_removed = set()
    for (en_id, de_id), directions in wiki_links.items():
        if "de to en" in directions and "en to de" in directions:
            # Keep pages that point at each other (EN <-> DE)
            referencing_eachother += 1
            continue
        elif ((nodes_en[en_id]["indegree"] == 0 and nodes_de[de_id]["outdegree"] == 0 and nodes_de[de_id][
            "indegree"] == 1) or
                  (nodes_de[de_id]["indegree"] == 0 and nodes_en[en_id]["outdegree"] == 0 and nodes_en[en_id][
                      "indegree"] == 1)):
            # Keep pages that are only single links (EN -> DE, DE -> EN)
            # Note: Chains, star patterns, etc lead to removal
            singlelink += 1
            continue
        else:
            removed += 1
            print("Unwanted: " + str((en_id, de_id)))
            print(directions)
            if "de to en" in directions:
                print(de_id_lookup[de_id] + " -> " + en_id_lookup[en_id])
            elif "en to de" in directions:
                print(en_id_lookup[en_id] + " -> " + de_id_lookup[de_id])
            print(nodes_en[en_id])
            print(nodes_de[de_id])
            print("------------")
            # Add to blacklist
            to_be_removed.add((en_id, de_id))

    print("Referencing each other: " + str(referencing_eachother))
    print("Single Link: " + str(singlelink))
    print("Removed: " + str(removed))
    return to_be_removed

def remove_questionable_links(to_be_removed):
    with open("../../data/pairs/de_en_pairs_unfiltered.tsv","r",encoding="utf8") as f_in:
        with open("../../data/pairs/de_en_pairs.tsv", "w", encoding="utf8") as f_out:
            f_out.write(f_in.readline())
            for line in f_in:
                splits = line.strip().split("\t")
                en_id = int(splits[0])
                de_id = int(splits[2])
                if not (en_id,de_id) in to_be_removed:
                    f_out.write(line)

# Goal: create an en + de ID blacklist and filter
def filter_pairs():
    title_lookup, de_id_lookup, en_id_lookup = loadLookups()
    nodes_de, nodes_en, wiki_links = build_nodes(title_lookup, de_id_lookup, en_id_lookup)
    to_be_removed = mark_for_removal(nodes_de, nodes_en, wiki_links, de_id_lookup, en_id_lookup)
    remove_questionable_links(to_be_removed)

if __name__ == "__main__":
    filter_pairs()