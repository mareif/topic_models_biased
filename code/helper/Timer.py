import time

'''
Helps to track the time of each process
'''

class Timer(object):

    def __init__(self):
        self.start = time.time()


    def timestamp(self):
        end = time.time()
        m, s = divmod(end - self.start, 60)
        h, m = divmod(m, 60)
        print("%d:%02d:%02d" % (h, m, s))

    def reset(self):
        self.start = time.time()

