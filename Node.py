import math
from Entry import Entry, LeafEntry


class Node:
    max_entries = 3  # M
    min_entries = math.floor(max_entries/2)  # m

    def __init__(self, entries=None, parent=None):
        if entries is None:
            self.entries = []  # List of entries (internal or leaf)
        else:
            self.entries = entries
        if parent is None:
            self.parent = None  # Reference to the parent node
        else:
            self.parent = parent

    def insert_entry(self, entry):
        self.entries.append(entry)

    def insert_entries(self, entries):
        for entry in entries:
            self.entries.append(entry)

    def delete_entry(self, entry):
        pass

    def set_parent(self, parent):
        self.parent = parent

    @classmethod
    def set_max_entries(cls, number):
        cls.max_entries = number
        cls.min_entries = math.floor(number/2)


# class InternalNode(Node):
#     def __init__(self, entries=None, parent=None):
#         super().__init__(entries=None, parent=None)
#
#
# class LeafNode(Node):
#     def __init__(self, entries=None, parent=None):
#         super().__init__(entries=None, parent=None)

#
# entr = [[1, 2, 3], [4, 5, 6]]
# entr2 = [[5, 2, 2], [2, 2, 5]]
# node1 = Node()
# node1.insert_entry(entr)
# print(node1.entries)
# node1.insert_entry(entr2)
# print(node1.entries)