"""This holds pointers to data, that will be read in by pandas"""

import os

# Assume there is a "data" directory at the same level as this directory.
DATADIR = os.path.join(os.path.dirname(__file__), "data")

xys = {
    "Pancan12-mRNA": os.path.join(DATADIR, "Pancan12.mRNA.openOrd.xys")
}

attrs = {
    "Pancan12-mRNA": os.path.join(DATADIR, "Pancan12.mini.attrs")
}


