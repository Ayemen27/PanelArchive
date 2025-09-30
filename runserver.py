#coding: utf-8
# +-------------------------------------------------------------------
# | aaPanel
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2099 aaPanel(www.aapanel.com) All rights reserved.
# +-------------------------------------------------------------------
# | Author: hwliang <hwl@aapanel.com>
# +-------------------------------------------------------------------
import sys
import os
from os import environ

# Add required paths to sys.path before importing BTPanel
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if os.path.join(current_dir, 'class') not in sys.path:
    sys.path.insert(0, os.path.join(current_dir, 'class'))
if os.path.join(current_dir, 'class_v2') not in sys.path:
    sys.path.insert(0, os.path.join(current_dir, 'class_v2'))

from BTPanel import app

if __name__ == '__main__':
    f = open('data/port.pl')
    PORT = int(f.read())
    HOST = '0.0.0.0'
    f.close()
    app.run(host=HOST,port=PORT)
