from random import choice

'''
Ensures that all articles only appear exactly ones.
Which pair will be kept is decided randomly.

Input: *dataset@outpath*.tsv
Output: *dataset@outpath*_nodup.tsv
'''

def assign_to_keep_remove(seen,keep,remove):
    for _, pairs in list(seen.items()):
        if len(pairs) <= 1:
            continue

        keep_element = None
        for pair in pairs:
            if pair in keep:
                keep_element = pair

        if not keep_element:
            keep_element = choice(pairs)

        keep.add(keep_element)
        for pair in pairs:
            if pair != keep_element:
                remove.add(pair)

def debug_print(a_seen, b_seen,keep,remove):
    print("A - Duplicates\n-------\n")
    for _, value in list(a_seen.items()):
        if len(value) > 1:
            for pair in value:
                assert (pair in keep or pair in remove)
                formatted_pair = (pair[0], pair[1], pair[3])
                print(str(formatted_pair) + " - Keep: " + str(pair in keep) + " - Delete: " + str(pair in remove))
            print("-------")

    print("B - Duplicates\n-------\n")
    for _, value in list(b_seen.items()):
        if len(value) > 1:
            for pair in value:
                assert (pair in keep or pair in remove)
                formatted_pair = (pair[0], pair[1], pair[3])
                print(str(formatted_pair) + " - Keep: " + str(pair in keep) + " - Delete: " + str(pair in remove))
            print("-------")

    keep_and_remove = keep.intersection(remove)
    print(len(keep_and_remove))
    print(keep_and_remove)

def remove_duplicates(file_path, debug=False):
    a_index = 1
    b_index = 6
    event_index = 0

    # Clean intra-event duplicates
    with open(file_path,"r",encoding="utf8") as f_in:
        first_line = f_in.readline()
        a_seen = {}
        b_seen = {}
        for line in f_in:
            splits = line.strip().split("\t")
            a_id = splits[a_index]
            b_id = splits[b_index]
            event_nr = splits[event_index]
            if event_nr.endswith("copy"):
                continue

            if a_seen.get(a_id) == None:
                a_seen[a_id] = []
            a_seen[a_id].append((event_nr,a_id,b_id))

            if b_seen.get(b_id) == None:
                b_seen[b_id] = []
            b_seen[b_id].append((event_nr,a_id,b_id))

        keep = set()
        remove = set()

        assign_to_keep_remove(a_seen, keep, remove)
        assign_to_keep_remove(b_seen, keep, remove)

        if debug:
            debug_print(a_seen, b_seen, keep, remove)

    file_path_splits = file_path.split(".")
    file_path_splits[-2]+="_nodup"
    new_file_path = ".".join(file_path_splits)

    with open(new_file_path,"w",encoding="utf8") as f_out:
        with open(file_path, "r", encoding="utf8") as f_in:
            f_out.write(f_in.readline())
            for line in f_in:
                splits = line.strip().split("\t")
                a_id = splits[a_index]
                b_id = splits[b_index]
                event_nr = splits[event_index]
                if (event_nr,a_id,b_id) in remove:
                    continue
                else:
                    f_out.write(line)

    print("Finished: "+ new_file_path)

if __name__ == '__main__':
    remove_duplicates("../../data/final/US_rand_pairs.tsv")
    remove_duplicates("../../data/final/UK_rand_pairs.tsv")
    remove_duplicates("../../data/final/Mixed_rand_pairs.tsv")