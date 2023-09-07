from Entry import Entry, LeafEntry, Rectangle
import xml.etree.ElementTree as ET
from Node import Node
import heapq
import math


def read_whole_block_from_datafile(block_id, filename):
    # Parse the datafile.xml
    tree = ET.parse(filename)
    root = tree.getroot()

    # Find the specified block with the given block_id
    block_to_read = None
    for block_elem in root.findall(".//Block[@id='" + str(block_id) + "']"):
        block_to_read = block_elem
        break

    if block_to_read is None:
        return []  # Block with the specified block_id not found

    # Extract and return the records within the block
    records = []
    for record_elem in block_to_read.findall(".//Record"):
        record_id = int(record_elem.find(".//record_id").text)
        name = record_elem.find(".//name").text
        coordinates = record_elem.find(".//coordinates").text.split()
        coordinates_float = list(map(float, coordinates))
        records.append([record_id, name, *coordinates_float])

    return records


def get_original_records_from_datafile(points, filename):
    # sort the points based on the block_id
    points.sort(key=lambda leaf_entry: leaf_entry.record_id[0])
    # separate them by block using a dictionary
    groups = {}
    for leaf_entry in points:
        key = leaf_entry.record_id[0]
        if key not in groups:
            groups[key] = []
        groups[key].append(leaf_entry)
    list_of_block_items = list(groups.values())  # convert the dictionary into a list of lists

    records_of_points = []
    for sublist in list_of_block_items:
        block_id = sublist[0].record_id[0]
        block_records = read_whole_block_from_datafile(block_id, filename)  # read the whole block
        for leaf_entry in sublist:
            slot_in_block = leaf_entry.record_id[1]
            records_of_points.append(block_records[slot_in_block])  # keep only the records we are looking for
    return records_of_points


def load_tree_from_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    nodes = []  # To store nodes in order

    max_entries = int(root.attrib.get("max_entries"))
    Node.set_max_entries(max_entries)

    for node_elem in root.findall("Node"):
        entries = []
        child_node_indices = []

        if node_elem.find("Entry") is not None:
            for entry_elem in node_elem.findall("Entry"):
                rectangle_elem = entry_elem.find("Rectangle")
                bottom_left_point = [float(coord) for coord in rectangle_elem.find("BottomLeftPoint").text.split()]
                top_right_point = [float(coord) for coord in rectangle_elem.find("TopRightPoint").text.split()]
                rectangle = Rectangle([bottom_left_point, top_right_point])

                child_node_index_elem = entry_elem.find("ChildNodeIndex")
                if child_node_index_elem is not None:
                    child_node_index = int(child_node_index_elem.text)
                    child_node_indices.append(child_node_index)
                entries.append(Entry(rectangle, None))

        elif node_elem.find("LeafEntry") is not None:
            for entry_elem in node_elem.findall("LeafEntry"):
                record_id_elem = entry_elem.find("RecordID")
                point_elem = entry_elem.find("Point")
                record_id = tuple(map(int, record_id_elem.text.split(",")))
                point = [float(coord) for coord in point_elem.text.split()]
                # leaf_entry = LeafEntry([record_id[0], record_id[1]] + point)
                record = [record_id[0], record_id[1]] + [float(coord) for coord in point]
                leaf_entry = LeafEntry(record)
                entries.append(leaf_entry)

        parent_node_index_elem = node_elem.find("ParentNodeIndex")
        if parent_node_index_elem is not None:
            parent_node = nodes[int(parent_node_index_elem.text)]
            slot_in_parent = int(node_elem.find("SlotInParent").text)
            node = Node(entries, parent_node, slot_in_parent)  # creates node and sets parent
            parent_node.entries[slot_in_parent].set_child_node(node)  # sets the parent's corresponding entry's child
        else:
            node = Node(entries)  # only for root node
        nodes.append(node)

        Node.set_overflow_treatment_level(nodes[-1].find_node_level())

    return nodes


def is_dominated(point, skyline_points):
    for skyline_point in skyline_points:
        if all(a <= b for a, b in zip(skyline_point, point)):
            return True
    return False


# This is a placeholder for your mindist function.
def mindist(query_point, rectangle):
    sum_of_squares = 0
    for q, bl, tr in zip(query_point, rectangle.bottom_left_point, rectangle.top_right_point):
        if q < bl:
            sum_of_squares += (bl - q) ** 2
        elif q > tr:
            sum_of_squares += (q - tr) ** 2
    return math.sqrt(sum_of_squares)


def dominates(a, b):
    """
    Returns True if point 'a' dominates point 'b' based on Skyline Query criteria.
    Both 'a' and 'b' should be tuples or lists representing points in n-dimensional space.
    """
    is_strictly_less_in_at_least_one_dimension = False  # To keep track if any dimension of 'a' is strictly less than 'b'
    is_less_or_equal_in_all_dimensions = True  # To keep track if 'a' is less or equal to 'b' in all dimensions

    for ai, bi in zip(a, b):
        if ai > bi:
            is_less_or_equal_in_all_dimensions = False
            break
        if ai < bi:
            is_strictly_less_in_at_least_one_dimension = True

    return is_strictly_less_in_at_least_one_dimension and is_less_or_equal_in_all_dimensions


class QueueEntry:
    def __init__(self, mindist, node_or_entry):
        self.mindist = mindist
        self.node_or_entry = node_or_entry

    def __lt__(self, other):
        return self.mindist < other.mindist


def skyline_algorithm(tree, query_point):
    pq = [QueueEntry(0, 0)]  # Initialize the priority queue with the index of the root node
    S = []  # The skyline set

    while pq:
        queue_entry = heapq.heappop(pq)
        node_index = queue_entry.node_or_entry
        node = tree[node_index]

        # print(f"Priority Queue: {[(entry.mindist, entry.node_or_entry) for entry in pq]}")

        if node.is_leaf():
            for entry in node.entries:
                if not is_dominated(entry.point, S):
                    # Remove points from S that are dominated by the new point
                    S = [s for s in S if not dominates(entry.point, s)]
                    S.append(entry.point)
                # print(f"Updated Skyline: {S}")

        else:
            for entry in node.entries:
                entry_mindist = mindist(query_point, entry.rectangle)
                child_index = tree.index(entry.child_node)  # Assuming child_node is an object, find its index in the tree list
                heapq.heappush(pq, QueueEntry(entry_mindist, child_index))

    return S


tree = load_tree_from_xml("indexfile1.xml")

# for node in tree:
#     if node.is_leaf():
#         length = len(node.entries[0].point)
#         print(node.entries[0].point)

length = len(tree[-1].entries[0].point)
print(length)

# for node in tree:
#     if node.is_leaf():
#         for entry in node.entries:
#             print(entry.point)

query_point = [0] * length
result = skyline_algorithm(tree, query_point)
print("Result of skyline algorithm:", result)

