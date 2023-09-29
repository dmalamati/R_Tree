import math
from Entry import Entry, LeafEntry


class Node:
    max_entries = 4  # M
    min_entries = math.floor(max_entries * 0.3)  # m = 30% of M

    overflow_treatment_level = 1

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

    def __str__(self):
        if hasattr(self, 'mbr'):
            return f"Node with MBR: {self.mbr}"
        else:
            return f"Node with {len(self.entries)} entries"

    def is_leaf(self):
        if not self.entries:
            return False
        return isinstance(self.entries[0], LeafEntry)

    def set_parent(self, parent, slot_in_parent):
        self.parent = parent
        self.slot_in_parent = slot_in_parent

    def set_slot_in_parent(self, slot_in_parent):
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

    @classmethod
    def set_overflow_treatment_level(cls, leaf_level):
        cls.overflow_treatment_level = leaf_level

    @classmethod
    def increase_overflow_treatment_level(cls):
        cls.overflow_treatment_level += 1
