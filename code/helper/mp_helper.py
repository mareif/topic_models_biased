import multiprocessing as mp
import time

'''
Allows easier multicore processing (for large files, and to track custom processes)
'''

class Chunker(object):

    def __init__(self, object_to_chunk, el_function=None, chunksize=10000):
        self.obj = object_to_chunk
        self.chunksize = chunksize
        self.el_function = el_function

    def __iter__(self):
        chunk = []
        for element in self.obj:
            if self.el_function!=None:
                proc_element = self.el_function(element)
                chunk.append(proc_element)
            else:
                chunk.append(element)
            if len(chunk) >= self.chunksize:
                yield chunk
                chunk=[]

        if len(chunk) > 0:
            yield chunk

def ensure_process_count(process_count):
    while len(mp.active_children()) >= process_count:
        time.sleep(5)

def wait_for_processes(mp_instance_offset=0):
    while len(mp.active_children()) > mp_instance_offset:
        # print(str(len(mp.active_children())) + " left - " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())))
        time.sleep(10)

def chunk(obj_to_chunk, function_name, args, chunksize=10000, process_count=mp.cpu_count()-1, read_Offset=0, pass_Offset = False, timer=None, mp_instance_offset=0):
    # Note: f_in needs to be at the actual data (not at a header)
    #
    # Always assume:
    #   - first argument: text_array
    #   - locks and stuff is in args
    #   - last argument: potential chunk offset

    offset = 0
    chunk_id = 1
    chunk = []

    while offset<read_Offset:
        next(obj_to_chunk)
        offset+=1

    for element in obj_to_chunk:
        chunk.append(element)
        if len(chunk) >= chunksize:
            ensure_process_count(process_count)

            print("Starting Process on Chunk: "+str(offset + ((chunk_id-1) * chunksize)+1) +
                  " - " + str(offset + (chunk_id * chunksize)))
            if timer:
                timer.timestamp()

            if pass_Offset:
                p = mp.Process(target=function_name, args=tuple( [chunk]+list(args)+ [offset + ((chunk_id-1) * chunksize)]))
            else:
                p = mp.Process(target=function_name, args=tuple([chunk] + list(args)))
            p.start()
            chunk_id+=1
            chunk=[]

    if len(chunk)>0:
        if pass_Offset:
            p = mp.Process(target=function_name,
                           args=tuple([chunk] + list(args) + [offset + ((chunk_id - 1) * chunksize)]))
        else:
            p = mp.Process(target=function_name, args=tuple([chunk] + list(args)))
        p.start()

    wait_for_processes(mp_instance_offset=mp_instance_offset)