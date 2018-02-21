import sys
from code.helper import Timer

'''
Get all links between German and English articles

Input:  ../../data/de/original/dewiki-latest-langlinks.sql
        ../../data/en/original/enwiki-latest-langlinks.sql
Output: ../../data/pairs/de-en-docs.txt
        ../../data/pairs/en-de-docs.txt
'''

def get_paired_docs_dir(origin,to):
    if origin=="de":
        print("Open: "+ '../../data/'+origin+'/original/'+origin+'wiki-latest-langlinks.sql')
        f_in = open('../../data/'+origin+'/original/'+origin+'wiki-latest-langlinks.sql', 'r', encoding="utf8")
    else:
        print("Open: " + '../../data/' + origin + '/original/' + origin + 'wiki-latest-langlinks.sql')
        f_in = open('../../data/' + origin + '/original/' + origin + 'wiki-latest-langlinks.sql', 'r', encoding="latin-1")

    f_out = open('../../data/pairs/'+origin+'-'+to+'-docs.txt', 'w', encoding="utf8")

    f_out.write('% ID\tlanguage\ttitle\n')

    for line in f_in:
        if "'"+to+"'" in line:
            first_index = line.index("(")
            objects = line[first_index + 1:-2].split('),(')
            for obj in objects:
                content = obj.split(',')
                if content[1] != "'"+to+"'":
                    continue
                f_out.write(content[0] + "\t" + content[1] + "\t" + ",".join(content[2:]) + '\n')

    f_in.close()
    f_out.close()

def get_paired_docs():
    timer = Timer()
    get_paired_docs_dir('de', 'en')
    get_paired_docs_dir('en', 'de')
    timer.timestamp()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        raise IOError("Overspecified")
    get_paired_docs()