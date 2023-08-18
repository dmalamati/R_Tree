import math
from Entry import Entry, LeafEntry


class Node:
    max_entries = 4  # M
    min_entries = math.floor(max_entries/2.0)  # m

    def __init__(self, entries=None, parent=None, slot_in_parent=None):
        if entries is None:
            self.entries = []  # List of entries (internal or leaf)
        else:
            self.entries = entries
        if parent is None:
            self.parent = None  # Reference to the parent node
            self.slot_in_parent = None
        else:
            self.parent = parent
            self.slot_in_parent = slot_in_parent

   # def __str__(self):
        #if hasattr(self, 'mbr'):
            #return f"Node with MBR: {self.mbr}"
        #else:
            #return f"Node with {len(self.entries)} entries"

    def insert_entry(self, entry):
        self.entries.append(entry)

    def is_leaf(self):
        if not self.entries:
            return False
        return isinstance(self.entries[0], LeafEntry)

    def set_entries(self, entries):
        self.entries = entries

    def delete_entry(self, entry):
        pass

    def set_parent(self, parent, slot_in_parent):
        self.parent = parent
        self.slot_in_parent = slot_in_parent

    def find_node_level(self):
        if self.parent is not None:
            return self.parent.find_node_level() + 1
        else:
            return 0


    @classmethod
    def set_max_entries(cls, number):
        cls.max_entries = number
        cls.min_entries = math.floor(number/2.0)
        # if cls.min_entries < 2:
        #     cls.min_entries = 2  # 2 <= m <= M/2


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