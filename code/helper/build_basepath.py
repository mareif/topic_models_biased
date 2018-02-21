import os

'''
Create the foundation path of data/samples/etc
'''

def build_basepath(rootfolder, namespace, sample_size=None, subfolder=None, appendix=None):
    if sample_size==None:
        path =  "../../" + str(rootfolder) + "/" + str(namespace["global_namespace"]) + "/general/"
    else:
        path =  "../../"+str(rootfolder)+"/"+str(namespace["global_namespace"])+"/" + str(sample_size) + "/"

    if appendix != None:
        path = path[:-1] + appendix + "/"

    if subfolder!=None:
        path += str(subfolder) + "/"


    if not os.path.exists(path):
        os.makedirs(path)

    return path