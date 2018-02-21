import os

'''
Allows consistend creation of a log
The log tracks which data has already been processed and can be used across multiple processes
'''

class progress_logger(object):

    def __init__(self,logfile_path, overwrite=False, lock = None):
        self.file_path = logfile_path
        folder_path = "/".join(logfile_path.split("/")[:-1])
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        self.already_written = None
        if overwrite and os.path.exists(logfile_path):
            os.remove(logfile_path)
        self.lock = lock

    def write_log(self,line_elements):
        if self.lock!= None:
            self.lock.acquire()

        with open(self.file_path, "a", encoding="utf8") as f_out:
            if self.already_written != None:
                if len(line_elements) == 1:
                    self.already_written.add(str(line_elements[0]))
                else:
                    self.already_written.add(tuple(map(str, line_elements)))
            out_string = ("\t".join(map(str, line_elements)) + "\n")
            f_out.write(out_string)

        if self.lock!= None:
            self.lock.release()

    def write_log_multiple(self,multiple_lines):
        if self.lock!= None:
            self.lock.acquire()

        with open(self.file_path,"a",encoding="utf8") as f_out:
            for line_elements in multiple_lines:
                if self.already_written!=None:
                    if len(line_elements)==1:
                        self.already_written.add(str(line_elements[0]))
                    else:
                        self.already_written.add(tuple(map(str,line_elements)))
                out_string=("\t".join(map(str,line_elements)) + "\n")
                f_out.write(out_string)

        if self.lock!= None:
            self.lock.release()

    def get_already_written(self):
        # Lazy fetch - Only add elements when initialized -> breaks when writing in multiprocessing
        if self.already_written == None:
            if not os.path.exists(self.file_path):
                self.already_written = set()
            else:
                self.update_already_written()
        return self.already_written

    def update_already_written(self):
        # update for multiprocessing
        if self.lock!= None:
            self.lock.acquire()

        self.already_written = set()
        with open(self.file_path, "r", encoding="utf8") as f_out:
            for line in f_out:
                splits = line.strip().split("\t")
                if len(splits) == 1:
                    self.already_written.add(splits[0])
                else:
                    self.already_written.add(tuple(splits))

        if self.lock!= None:
            self.lock.release()

if __name__ == "__main__":
    # Test
    proglog = progress_logger("../../progress/testlog.log", overwrite=True)
    aw = proglog.get_already_written()
    print(aw)
    if ("1","2","3") not in proglog.get_already_written():
        proglog.write_log([1,2,3])
    proglog.write_log_multiple([[4, 5, 6],[6, 5, 4],[3, 2, 1]])
    aw = proglog.get_already_written()
    print(aw)

    proglog_read = progress_logger("../../progress/testlog.log", overwrite=False)
    aw = proglog_read.get_already_written()
    print(aw)
    print()