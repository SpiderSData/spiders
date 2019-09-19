# -*- coding: utf-8 -*-

import time
import os


brand_name = "Leprix"
# local_path = "/home/mac/"
local_path = "/home/gavin/"
# if os.path.exists("/home/hades"):
#     local_path = "/home/hades/Luxsens/luxsens/"
# elif os.path.exists("/media/gavin"):
#     local_path = "/media/gavin/cce17f31-6649-4241-a666-05be6f04de46/"
# elif os.path.exists("D:\\lux'sens\\"):
#     local_path = "D:\\lux'sens\\"
#全局的请求urls
#--------------------------------------------
brand_dict = {"hermes": 14, }


def search_key(value):
    for name, age in brand_dict.iteritems():    # for name, age in list.items():  (for Python 3.x)
        if age == value:
            print name


def mkdir(path):
    path = path.strip()
    path = path.rstrip("\\")

    isExists = os.path.exists(path)

    if not isExists:
        os.makedirs(path)
        print (path+" Directory or file created successfully!")
        return True
    else:
        print (path+" Directory or file already exists!")
        return False