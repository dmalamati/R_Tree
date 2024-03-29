import time

from Entry import LeafEntry, Rectangle, Entry
import xml.etree.ElementTree as ET
from Node import Node
import heapq
import math


def k_nearest_neighbors(tree_root, query_point, k):
    pq = []  # Priority queue: Elements are (distance, count, node/point, is_leaf).

    count = 0  # Counter for unique ordering for same distances.

    visited_entries = set()  # To keep track of visited nodes and leaf entries

    # Initialize the queue with the root of the tree
    for entry in tree_root.entries:
        if id(entry) not in visited_entries:
            visited_entries.add(id(entry))
            if isinstance(entry, LeafEntry):
                point_distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(query_point, entry.point)]))
                heapq.heappush(pq, (point_distance, count, entry, True))
            else:
                heapq.heappush(pq, (entry.rectangle.euclidean_distance(query_point), count, entry.child_node, False))
            count += 1

    results = []

    while pq and len(results) < k:
        distance, _, current, is_leaf = heapq.heappop(pq)
        if is_leaf:  # If it's a leaf entry (i.e., a point)
            results.append((distance, current.point, current.record_id))
        else:  # If it's a node (either internal or leaf node)
            for entry in current.entries:
                entry_id = id(entry)
                if entry_id not in visited_entries:
                    visited_entries.add(entry_id)
                    if isinstance(entry, LeafEntry):  # Leaf Node
                        point_distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(query_point, entry.point)]))
                        heapq.heappush(pq, (point_distance, count, entry, True))
                    else:  # Internal Node
                        rectangle_distance = entry.rectangle.euclidean_distance(query_point)
                        heapq.heappush(pq, (rectangle_distance, count, entry.child_node, False))
                count += 1

    return results



def linear_search_in_datafile_KNN(query_point, datafile_name, k):
    tree = ET.parse(datafile_name)
    root = tree.getroot()
    result_records = []
    # for each block in the datafile (except block0)
    for block_elem in root.findall("Block"):
        if int(block_elem.get("id")) == 0:
            continue
        # for every record in each block
        for record_elem in block_elem.findall("Record"):
            coordinates = record_elem.find(".//coordinates").text.split()
            point = list(map(float, coordinates))
            point_distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(query_point, point)]))
            result = [point, point_distance]
            result_records.append(result)
    sorted_data = sorted(result_records, key=lambda x: x[1])
    linear_knn_results = []
    count = 0
    for list_1 in sorted_data:
        if count == k:
            break
        linear_knn_results.append(list_1)
        count += 1
    return linear_knn_results

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


tree = load_tree_from_xml("indexfile.xml")

length = len(tree[-1].entries[0].point)
print(length)

query_point = [0] * length
#query_point = [6, 6]
k = 5

start_time = time.time()
k_nearest_neighbors = k_nearest_neighbors(tree[0], query_point, k)
end_time = time.time()
print("\nKNN using knn algorithm in tree: ", end_time-start_time, " sec")

for distance, point, record_id in k_nearest_neighbors:
    print(f"Distance: {distance}")
    print(f"RecordID: {record_id}")
    print(f"Point: {point}")
    print("---------------------")

datafile_name = "datafile.xml"
start_time = time.time()
result_records = linear_search_in_datafile_KNN(query_point, datafile_name, k)
end_time = time.time()
print("\nKNN using linear search in datafile: ", end_time-start_time, " sec")

for list in result_records:
    print(f"Distance: {list[1]}")
    print(f"Point: {list[0]}")
    print("---------------------")



#records = get_original_records_from_datafile(k_nearest_neighbors, "indexfile2.xml")
