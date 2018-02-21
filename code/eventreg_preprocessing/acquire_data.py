from os import listdir
from code.helper import load_sources
from eventregistry import *

'''
Acquires articles based on the previously created event-list. 

The event list specifies which events contain left and right articles.
This function requests 200 article chunks of these events.
One event is processed when acquired at least one article pair.

You need to add your own API key to access Event Registry

Input:  ../../data/news_sources/*source lists*
        ../../data/event_uris/*start_date*-eventuris.json
Output: ../../data/article_data/*event_id*.art (multiple)
'''

def requestArticles(er,event, pageNr):
    q = QueryEvent(event)
    articleInfo = ReturnInfo(
            ArticleInfoFlags(
                    bodyLen = -1,
                    basicInfo = False,
                    title = True,
                    eventUri = True,
                    originalArticle = True,
                )
        )
    q.setRequestedResult(
        RequestEventArticles(
            page = pageNr,
            count = 200, # Max 200
            lang = "eng",
            sortBy = "socialScore", sortByAsc = False,
            returnInfo = articleInfo
        )
    )
    return er.execQuery(q)


# eventID generator with continue and log
class eventGen:
    def __init__(self, article_page_threshold=1):
        self.article_page_threshold = article_page_threshold
        if not os.path.exists("progress_logs"):
            os.makedirs("progress_logs")

        open("progress_logs/file_progress.log", 'a').close()
        with open("progress_logs/file_progress.log", "r", encoding="utf8") as f_prog:
            # Format of progress log: "filename \t event_index \t article_page \t hit \n"
            final_line = None
            for line in f_prog:
                final_line = line

            self.event_file_list = self.__load_event_files_list()
            if final_line == None:
                # Init Fresh
                start_date = self.event_file_list[0]
                self.filename = self.__tuple_to_filename(start_date)
                with open( "../../data/event_uris/" + self.filename, "r", encoding="utf8") as f_data:
                    self.current_data = json.load(f_data)["uriList"]["results"]
                self.event_index = 0
                self.article_page = 1
                self.hit = False
            else:
                # Continue
                continue_point = final_line.strip().split("\t")
                self.filename = continue_point[0]
                with open( "../../data/event_uris/" + self.filename, "r", encoding="utf8") as f_data:
                    self.current_data = json.load(f_data)["uriList"]["results"]
                self.event_index = int(continue_point[1])
                self.article_page = int(continue_point[2])
                if continue_point[3] == "Dead":
                    self.hit = True
                else:
                    self.hit = bool(continue_point[3])
                self.step(write=False)

    def step(self, write=True):
        if write:
            self.__write_log()

        # Assume you want to get the next page
        self.article_page += 1

        # If we found something before or the article_page_threshold has been exceeded
        # we're done with the event
        if self.hit or self.article_page > self.article_page_threshold:
            self.event_index += 1
            self.hit = False
            # If the week data is processed, continue with the next week
            if self.event_index >= len(self.current_data):
                self.event_index = 0
                self.filename = self.__next_file()
                if not self.filename:
                    return False
                with open("../../data/event_uris/" + self.filename, "r", encoding="utf8") as f_data:
                    self.current_data = json.load(f_data)["uriList"]["results"]
            self.article_page = 1
        return True

    def __iter__(self):
        yield self.current_data[self.event_index], self.article_page
        while self.step():
            yield self.current_data[self.event_index], self.article_page

    def __write_log(self):
        with open("progress_logs/file_progress.log", "a") as f_log:
            f_log.write(self.filename + "\t" +
                        str(self.event_index) + "\t" +
                        str(self.article_page) + "\t" +
                        str(self.hit) + "\n")

    def __next_file(self):
        date = self.__filename_to_tuple(self.filename)
        next_index = self.event_file_list.index(date) + 1
        if next_index >= len(self.event_file_list):
            return None
        return self.__tuple_to_filename(self.event_file_list[next_index])

    def __filename_to_tuple(self, filename):
        return [int(x) for x in filename.split("-")[0].split("_")]

    def __tuple_to_filename(self, date_tuple):
        return (str(date_tuple[0]) + "_" +
                str(date_tuple[1]) + "_" +
                str(date_tuple[2]) + "-eventuris.json")

    def __load_event_files_list(self):
        assert (len(listdir("../../data/event_uris/")) > 0)
        event_files = []
        for filename in listdir("../../data/event_uris/"):
            date = self.__filename_to_tuple(filename)
            event_files.append(date)
        return sorted(event_files)

def reset_log():
    open("progress_logs/file_progress.log", 'w').close()

# Start up Event Registry and set amount of iterations
API_KEY = "INSERT YOUR API KEY HERE"
er = EventRegistry(apiKey = API_KEY)

possible_requests = 1000
event_generator = eventGen(article_page_threshold=4)

news_sources = load_sources()

left_set = set(news_sources.left)
right_set = set(news_sources.right)

# Make sure that the outpaths exist
article_path =  "../../data/article_data/"
if not os.path.exists(article_path):
    os.makedirs(article_path)

previous_event = None
hit_left, hit_right = False, False
for event_id, pagenr in event_generator:
    print(event_id, pagenr)
    if previous_event != event_id:
        hit_left, hit_right = False, False
    previous_event = event_id

    res = requestArticles(er, event_id, pagenr)

    if res[event_id].get("articles") == None:
        # Some events have been merged with other events -> skip
        print(res[event_id])
        event_generator.hit = "Dead"
    else:
        # write out file: article_uri \t title \t url \t source_uri \t body \n
        with open(article_path + event_id + ".art", "a", ) as event_out:
            for article in res[event_id]["articles"]["results"]:
                event_out.write(article["uri"] + "\t" +
                                article["title"].replace("\n", " ").replace("\t", " ") + "\t" +
                                article["url"] + "\t" +
                                article["source"]["uri"] + "\t" +
                                article["body"].replace("\n", " ").replace("\t", " ") + "\n"
                                )
                if article["source"]["uri"] in left_set:
                    hit_left = True
                elif article["source"]["uri"] in right_set:
                    hit_right = True

    if hit_left and hit_right:
        print("Left and Right article found in: " + event_id)
        event_generator.hit = True

    possible_requests -= 1
    if possible_requests < 0:
        break

print("Finished")

