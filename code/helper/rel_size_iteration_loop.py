import os.path

'''
Helps iterating through the samples
'''

class rel_size_iteration_loop:
    def __init__(self, rel_sizes, iterations, base_path=None):
        self.rel_sizes = rel_sizes
        self.iterations = iterations
        self.base_path = base_path

    def __iter__(self):
        for i in range(1, self.iterations + 1):
            for relative_size in self.rel_sizes:
                if self.base_path!=None and isinstance(self.base_path, str):
                    path = self.base_path + str(i) + "/" + str(round(relative_size * 100)) + "/"
                    if not os.path.exists(path):
                        os.makedirs(path)
                    yield relative_size, i, path
                else:
                    yield relative_size, i