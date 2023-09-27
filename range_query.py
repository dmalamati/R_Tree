from Entry import Entry, LeafEntry, Rectangle
import xml.etree.ElementTree as ET
from Node import Node
import time


def read_whole_block_from_datafile(block_id, filename):
    # parse the datafile.xml
    tree = ET.parse(filename)
    root = tree.getroot()

    # find the specified block with the given block_id
    block_to_read = root.find(".//Block[@id='" + str(block_id) + "']")

    # if block with the specified block_id doesn't exist
    if block_to_read is None:
        return []

    # extract and return the records within the block
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


def linear_search_in_datafile_range_query(search_rectangle, datafile_name):
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
            # if the point of the record overlaps with the search area append it to the result
            if search_rectangle.overlaps_with_point(point):
                record_id = int(record_elem.find(".//record_id").text)
                name = record_elem.find(".//name").text
                result_records.append([record_id, name, *point])
    return result_records


def linear_search_in_tree_leafs_range_query(search_rectangle, leaf_entries):
    result_records = []
    # for each block in the datafile (except block0)
    for leaf_entrie in leaf_entries:
        # if the point of the record overlaps with the search area append it to the result
        if search_rectangle.overlaps_with_point(leaf_entrie.point):
            result_records.append(leaf_entrie)
    return result_records


def load_tree_from_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    nodes = []  # to store the tree's nodes in order

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


# MAIN
tree = load_tree_from_xml("indexfile.xml")

search_rectangle = Rectangle([[41.5163899, 26.5291294], [41.4913027, 26.5308288]])
print("search rect is: ", search_rectangle.bottom_left_point, " ", search_rectangle.top_right_point)


# range query using index
start_time = time.time()
records = search_rectangle.find_points_in_rectangle(tree[0])
end_time = time.time()
print("Range query using index: ", end_time-start_time, " sec")

original_records = get_original_records_from_datafile(records, "datafile.xml")
if len(original_records) > 0:
    print("found points in search rect:")
    for i, original_record in enumerate(original_records):
        print("record ", i, ": ", original_record)
else:
    print("nothing found")


# range query using linear search in datafile
start_time = time.time()
other_records = linear_search_in_datafile_range_query(search_rectangle, "datafile.xml")
end_time = time.time()
print("\nRange query using linear search in datafile: ", end_time-start_time, " sec")

if len(other_records) > 0:
    print("found points in search rect:")
    for i, record in enumerate(other_records):
        print("record ", i, ": ", record)
else:
    print("nothing found")


# range query using linear search on tree leafs
leaf_entries = []
for node in tree[::-1]:
    if isinstance(node.entries[0], LeafEntry):
        for leaf_entry in node.entries:
            leaf_entries.append(leaf_entry)
    else:
        break

start_time = time.time()
other_records = linear_search_in_tree_leafs_range_query(search_rectangle, leaf_entries)
end_time = time.time()
print("\nRange query using linear search on tree leafs: ", end_time-start_time, " sec")

original_records = get_original_records_from_datafile(other_records, "datafile.xml")
if len(original_records) > 0:
    print("found points in search rect:")
    for i, original_record in enumerate(original_records):
        print("record ", i, ": ", original_record)
else:
    print("nothing found")

# small example
# tree = load_tree_from_xml("indexfile2.xml")
# search_rectangle = Rectangle([[-4.0, -6.0], [4.0, 0.0]])
# records = search_rectangle.find_points_in_rectangle(tree[0])
# if len(records) > 0:
#     print("found points in search rect:")
#     for i, record in enumerate(records):
#         print("record ", i, ": ", record.point)
# else:
#     print("nothing found")
