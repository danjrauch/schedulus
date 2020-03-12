from src.types.node import *

__metaclass__ = type

class Cluster:
    def __init__(self):
        self.nodes = []
        self.total = -1
        self.idle  = -1
        self.avail = -1