from eventregistry import *
from code.helper import load_sources

'''
Requests all events that contain articles from left and right sources
(currently does not differentiate between US and UK sources)

You need to add your own API key to access Event Registry

Input: ../../data/news_sources/*source lists*
Output: ../../data/event_uris/*start_date*-eventuris.json (multiple)
'''

# Complex Request
# "Return if event is covered by at least one left and one right wing news outlet"
def requestEventUrisComplex(er,startDate,endDate):
    global NEWS_OUTLETS_LEFT, NEWS_OUTLETS_RIGHT
    print(NEWS_OUTLETS_LEFT)
    cq = ComplexEventQuery(
            CombinedQuery.AND(
                [
                BaseQuery(
                    sourceUri = QueryItems.OR(NEWS_OUTLETS_LEFT),
                    lang = "eng",
                    dateStart = startDate,
                    dateEnd = endDate
                ),
                BaseQuery(
                    sourceUri = QueryItems.OR(NEWS_OUTLETS_RIGHT),
                    lang = "eng",
                    dateStart = startDate,
                    dateEnd = endDate
                )
            ]
        )
        )
    q = QueryEvents.initWithComplexQuery(cq)
    # Only return Event identifiers
    q.setRequestedResult(RequestEventsUriList())
    res = er.execQuery(q)
    return res



# Decide if outfiles should be overwritten
overwrite = False

# Load News outlets
news_outlets = load_sources()

NEWS_OUTLETS_LEFT = news_outlets.left
NEWS_OUTLETS_RIGHT = news_outlets.right

API_KEY = "INSERT YOUR API KEY HERE"
er = EventRegistry(apiKey = API_KEY)

# Init outpath
event_path = "../../data/event_uris/"
if not os.path.exists(event_path):
    os.makedirs(event_path)

# Init dates in a given timeframe
delta = datetime.timedelta(days=7)
today = datetime.datetime.today()

end_date = datetime.datetime(today.year, today.month, today.day)

# Set the end date to last monday (so you always get full weeks
while end_date.strftime("%A")!="Monday":
    end_date = end_date - datetime.timedelta(days=1)
start_date = end_date - delta

# set to raw text cell,such that it is not executed unintentionally
# Get event uris for the last month
for i in range(4):
    # If you dont overwrite and the file exist -> go to next week
    print("Checking: "+ event_path + str(start_date.year) + "_" + str(start_date.month) + "_"
                                                + str(start_date.day) + "-eventuris.json")
    if not overwrite and os.path.exists(event_path + str(start_date.year) + "_" + str(start_date.month) + "_"
                                                + str(start_date.day) + "-eventuris.json"):
        print(event_path + str(start_date.year) + "_" + str(start_date.month) + "_"
              + str(start_date.day) + "-eventuris.json already exists")
        end_date, start_date = start_date, start_date - delta
        continue
    print("Current: " + str(start_date) + " - " + str(end_date))

    # Get Event Uris
    res = requestEventUrisComplex(er, start_date, end_date)

    if res.get("info"):
        # Found an info tag = there is no actual data
        print("Could not retrieve more information")
        break
    else:
        # Print how many results you have found
        print(str(res["uriList"]["totalResults"]) + " - Results")

    # Store even uris
    with open(event_path + str(start_date.year) + "_" + str(start_date.month) + "_"
                      + str(start_date.day) + "-eventuris.json", "w", encoding="utf8") as f_out:
        json.dump(res, f_out, indent=2)

    end_date, start_date = start_date, start_date - delta

    # Keep some space between the requests
    time.sleep(1)