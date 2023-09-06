from Entry import LeafEntry, Rectangle, Entry
import xml.etree.ElementTree as ET
from Node import Node
import heapq
import math


def k_nearest_neighbors(tree_root, query_point, k):
    """ Find the k nearest neighbors of query_point in the R-tree rooted at tree_root."""

    # A priority queue. Elements are (distance, node/point, is_leaf).
    # The distances are negative because Python's heapq doesn't have a max heap, only a min heap.
    # So we negate distances to get the max distance first when we pop from the queue.
    pq = []

    # Initialize the queue with the root of the tree
    heapq.heappush(pq, (-tree_root.entries[0].rectangle.euclidean_distance(query_point), tree_root, False))

    k_results = []

    while pq and len(k_results) < k:
        distance, current, is_leaf = heapq.heappop(pq)
        distance = -distance  # Convert back to positive

        if is_leaf:  # If it's a leaf entry
            k_results.append((distance, current))
            continue

        for entry in current.entries:
            if isinstance(entry, LeafEntry):  # Leaf Node
                point_distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(query_point, entry.point)]))
                heapq.heappush(pq, (-point_distance, entry, True))
            else:  # Internal Node
                rectangle_distance = entry.rectangle.euclidean_distance(query_point)
                heapq.heappush(pq, (-rectangle_distance, entry.child_node, False))

    return k_results


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
        lat, lon = map(float, coordinates)
        records.append([record_id, name, lat, lon])

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


tree = load_tree_from_xml("indexfile2.xml")

# for node in tree:
#     if node.is_leaf():
#         length = len(node.entries[0].point)
#         break

length = len(tree[-1].entries[0].point)
print(length)

query_point = [0] * length
k_nearest_neighbors = k_nearest_neighbors(tree[0], query_point, 3)
print(k_nearest_neighbors)
print("\n")

for distance, leaf_entry in k_nearest_neighbors:
    print(f"Distance: {distance}")
    print(f"RecordID: {leaf_entry.record_id}")
    print(f"Point: {leaf_entry.point}")
    print("---------------------")

# records = get_original_records_from_datafile(k_nearest_neighbors, datafile_name)
