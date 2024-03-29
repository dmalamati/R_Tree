from Entry import Entry, LeafEntry, Rectangle
from Node import Node
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import time


def read_all_blocks_from_datafile(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    # read data from block0
    block0 = root.find(".//Block[@id='" + str(0) + "']")

    blocks = []
    # get the number of blocks in the datafile from block0
    num_of_blocks = int(block0.find(".//num_of_blocks").text)
    for block_id in range(1, num_of_blocks):
        block_data = read_block_from_datafile(block_id, filename)
        blocks.append(block_data)

    Node.set_max_entries(len(blocks[0]))

    return blocks


def read_block_from_datafile(block_id, filename):
    # parse the datafile.xml
    tree = ET.parse(filename)
    root = tree.getroot()

    # find the specified block with the given block_id
    block_to_read = root.find(".//Block[@id='" + str(block_id) + "']")

    if block_to_read is None:
        # if specified block_id doesn't exist return empty list
        return []

    # extract and return the records within the block
    records = []
    for record_elem in block_to_read.findall(".//Record"):
        block_id = int(block_to_read.get("id"))
        slot_in_block = int(record_elem.get("id"))
        coordinates = record_elem.find(".//coordinates").text.split()
        coordinates_float = list(map(float, coordinates))
        records.append([block_id, slot_in_block, *coordinates_float])

    return records


def choose_subtree(new_leaf_entry, tree):
    N = tree[0]  # start with the root node

    if len(N.entries) == 0:
        # if root is empty it returns the root
        return N
    # while N is not a leaf
    while not isinstance(N.entries[0], LeafEntry):
        # if the children of N are leafs
        if isinstance(N.entries[0].child_node.entries[0], LeafEntry):
            min_overlap_cost = float('inf')
            min_area_cost = float('inf')
            chosen_entry = None

            # for every entry in N where N a node whose child is a leaf
            for i, entry in enumerate(N.entries):
                overlap_enlargement = entry.rectangle.calculate_overlap_enlargement(new_leaf_entry, i, N)
                area_enlargement = entry.rectangle.calculate_area_enlargement(new_leaf_entry)

                if overlap_enlargement < min_overlap_cost or (overlap_enlargement == min_overlap_cost and area_enlargement < min_area_cost):
                    min_overlap_cost = overlap_enlargement
                    min_area_cost = area_enlargement
                    chosen_entry = entry
        else:
            # if the children of N are NOT leafs
            min_area_cost = float('inf')
            min_area = float('inf')
            chosen_entry = None

            # for every entry in N where N a node whose child is not a leaf
            for entry in N.entries:
                area_enlargement = entry.rectangle.calculate_area_enlargement(new_leaf_entry)
                new_area = entry.rectangle.calculate_area() + area_enlargement

                if area_enlargement < min_area_cost or (area_enlargement == min_area_cost and new_area < min_area):
                    min_area_cost = area_enlargement
                    min_area = new_area
                    chosen_entry = entry

        N = chosen_entry.child_node

    return N  # the most suitable leaf node for the new leaf_entry to be inserted


def split(node, min_entries):
    split_axis = choose_split_axis(node.entries, min_entries)
    group1, group2 = choose_split_index(node.entries, split_axis, min_entries)

    return group1, group2


def choose_split_axis(entries, min_entries):
    min_sum_margin = float('inf')
    chosen_axis = None
    # if the node we want to split is a leaf
    if isinstance(entries[0], LeafEntry):

        for axis in range(len(entries[0].point)):
            entries.sort(key=lambda entry: entry.point[axis])

            sum_margin = 0
            for i in range(min_entries, len(entries) - min_entries + 1):
                rect1 = Rectangle([entry.point for entry in entries[:i]])
                rect2 = Rectangle([entry.point for entry in entries[i:]])
                sum_margin += rect1.calculate_margin() + rect2.calculate_margin()

            if sum_margin < min_sum_margin:
                min_sum_margin = sum_margin
                chosen_axis = axis
    else:
        # if the node we want to split is internal
        for axis in range(len(entries[0].rectangle.bottom_left_point)):
            entries.sort(key=lambda entry: entry.rectangle.bottom_left_point[axis])

            sum_margin = 0
            # find every acceptable partition
            for i in range(min_entries, len(entries) - min_entries + 1):
                rect1_points = []
                for entry in entries[:i]:
                    rect1_points.append(entry.rectangle.bottom_left_point)
                    rect1_points.append(entry.rectangle.top_right_point)
                rect1 = Rectangle(rect1_points)

                rect2_points = []
                for entry in entries[i:]:
                    rect2_points.append(entry.rectangle.bottom_left_point)
                    rect2_points.append(entry.rectangle.top_right_point)
                rect2 = Rectangle(rect2_points)

                sum_margin += rect1.calculate_margin() + rect2.calculate_margin()
            # select the best partition based on the sum of the MBRs margins
            if sum_margin < min_sum_margin:
                min_sum_margin = sum_margin
                chosen_axis = axis

    return chosen_axis


def choose_split_index(entries, split_axis, min_entries):
    # if the node we want to split is a leaf
    if isinstance(entries[0], LeafEntry):
        entries.sort(key=lambda entry: entry.point[split_axis])
        min_overlap = float('inf')
        min_area = float('inf')
        chosen_index = None
        # finds every split that respects the minimum entries a node can have
        for i in range(min_entries, len(entries) - min_entries + 1):
            rect1 = Rectangle([entry.point for entry in entries[:i]])
            rect2 = Rectangle([entry.point for entry in entries[i:]])
            overlap = rect1.calculate_overlap_value(rect2)
            overall_area = rect1.calculate_area() + rect2.calculate_area()

            # selects the best partition based on the overlap of the MBRs
            if overlap < min_overlap or (overlap == min_overlap and overall_area < min_area):
                min_overlap = overlap
                min_area = overall_area
                chosen_index = i
    else:
        # if the node we want to split is internal
        entries.sort(key=lambda entry: entry.rectangle.bottom_left_point[split_axis])

        min_overlap = float('inf')
        min_area = float('inf')
        chosen_index = None

        for i in range(min_entries, len(entries) - min_entries + 1):
            rect1_points = []
            for entry in entries[:i]:
                rect1_points.append(entry.rectangle.bottom_left_point)
                rect1_points.append(entry.rectangle.top_right_point)
            rect1 = Rectangle(rect1_points)

            rect2_points = []
            for entry in entries[i:]:
                rect2_points.append(entry.rectangle.bottom_left_point)
                rect2_points.append(entry.rectangle.top_right_point)
            rect2 = Rectangle(rect2_points)

            overlap = rect1.calculate_overlap_value(rect2)
            overall_area = rect1.calculate_area() + rect2.calculate_area()

            # selects the best partition based on the overlap of the MBRs
            if overlap < min_overlap or (overlap == min_overlap and overall_area < min_area):
                min_overlap = overlap
                min_area = overall_area
                chosen_index = i

    return entries[:chosen_index], entries[chosen_index:]


def overflow_treatment(node, level_of_node, tree):
    if level_of_node == 0:
        # split root
        entry_group1, entry_group2 = split(node, Node.min_entries)
        # if  root is a leaf node
        if isinstance(entry_group1[0], LeafEntry):
            new_leaf_node1 = Node(entry_group1)
            new_leaf_node2 = Node(entry_group2)

            rect1 = Rectangle([entry.point for entry in entry_group1])
            root_entry1 = Entry(rect1, new_leaf_node1)
            rect2 = Rectangle([entry.point for entry in entry_group2])
            root_entry2 = Entry(rect2, new_leaf_node2)

            new_root_node = Node([root_entry1, root_entry2])
            new_leaf_node1.set_parent(new_root_node, 0)
            new_leaf_node2.set_parent(new_root_node, 1)

            tree.remove(node)
            # root always stays at the head of the list
            tree.insert(0, new_root_node)
            # the roots children follow right after
            tree.insert(1, new_leaf_node1)
            tree.insert(2, new_leaf_node2)
        else:
            # if root is internal node
            new_node1 = Node(entry_group1)
            new_node2 = Node(entry_group2)

            rect1_points = []
            for entry in entry_group1:
                rect1_points.append(entry.rectangle.bottom_left_point)
                rect1_points.append(entry.rectangle.top_right_point)
            rect1 = Rectangle(rect1_points)
            root_entry1 = Entry(rect1, new_node1)

            rect2_points = []
            for entry in entry_group2:
                rect2_points.append(entry.rectangle.bottom_left_point)
                rect2_points.append(entry.rectangle.top_right_point)
            rect2 = Rectangle(rect2_points)
            root_entry2 = Entry(rect2, new_node2)

            new_root_node = Node([root_entry1, root_entry2])
            new_node1.set_parent(new_root_node, 0)
            new_node2.set_parent(new_root_node, 1)

            # set the new nodes as parent of the children that were assigned to each of them
            for i, entry in enumerate(new_node1.entries):
                entry.child_node.set_parent(new_node1, i)
            for i, entry in enumerate(new_node2.entries):
                entry.child_node.set_parent(new_node2, i)

            tree.remove(node)
            # root always stays at the head of the list
            tree.insert(0, new_root_node)
            # the roots children follow right after
            tree.insert(1, new_node1)
            tree.insert(2, new_node2)

    elif level_of_node == Node.overflow_treatment_level:
        # reinsert
        Node.increase_overflow_treatment_level()
        reinsert(tree, node)
    else:
        # split node
        entry_group1, entry_group2 = split(node, Node.min_entries)
        if isinstance(entry_group1[0], LeafEntry):
            # split leaf node
            new_leaf_node1 = Node(entry_group1)
            new_leaf_node2 = Node(entry_group2)

            rect1 = Rectangle([entry.point for entry in entry_group1])
            internal_entry1 = Entry(rect1, new_leaf_node1)
            rect2 = Rectangle([entry.point for entry in entry_group2])
            internal_entry2 = Entry(rect2, new_leaf_node2)

            node.parent.entries.remove(node.parent.entries[node.slot_in_parent])
            node.parent.entries.insert(node.slot_in_parent, internal_entry1)
            node.parent.entries.insert(node.slot_in_parent + 1, internal_entry2)

            new_leaf_node1.set_parent(node.parent, node.parent.entries.index(internal_entry1))
            new_leaf_node2.set_parent(node.parent, node.parent.entries.index(internal_entry2))

            for i, entry in enumerate(node.parent.entries):
                entry.child_node.set_slot_in_parent(i)

            # replace the old node with the new ones
            index_to_replace = tree.index(node)
            tree.insert(index_to_replace, new_leaf_node1)
            tree.insert(index_to_replace + 1, new_leaf_node2)
            tree.remove(node)

            # check if the parent has overflown
            if len(node.parent.entries) > Node.max_entries:
                overflow_treatment(node.parent, level_of_node-1, tree)
            else:
                adjust_rectangles(node.parent)
        else:
            # split internal node
            new_node1 = Node(entry_group1)
            new_node2 = Node(entry_group2)

            rect1_points = []
            for entry in entry_group1:
                rect1_points.append(entry.rectangle.bottom_left_point)
                rect1_points.append(entry.rectangle.top_right_point)
            rect1 = Rectangle(rect1_points)
            internal_entry1 = Entry(rect1, new_node1)

            rect2_points = []
            for entry in entry_group2:
                rect2_points.append(entry.rectangle.bottom_left_point)
                rect2_points.append(entry.rectangle.top_right_point)
            rect2 = Rectangle(rect2_points)
            internal_entry2 = Entry(rect2, new_node2)

            node.parent.entries.remove(node.parent.entries[node.slot_in_parent])
            node.parent.entries.insert(node.slot_in_parent, internal_entry1)
            node.parent.entries.insert(node.slot_in_parent + 1, internal_entry2)

            new_node1.set_parent(node.parent, node.parent.entries.index(internal_entry1))
            new_node2.set_parent(node.parent, node.parent.entries.index(internal_entry2))

            # update slot_in_parent for all children of the parent node that was expanded
            for i, entry in enumerate(node.parent.entries):
                entry.child_node.set_slot_in_parent(i)
            # update slot_in_parent for all children of the new nodes
            for i, entry in enumerate(new_node1.entries):
                entry.child_node.set_parent(new_node1, i)
            for i, entry in enumerate(new_node2.entries):
                entry.child_node.set_parent(new_node2, i)

            # replace the old node with the new ones in the tree list
            index_to_replace = tree.index(node)
            tree.insert(index_to_replace, new_node1)
            tree.insert(index_to_replace + 1, new_node2)
            tree.remove(node)

            # check if the parent has overflown
            if len(node.parent.entries) > Node.max_entries:
                overflow_treatment(new_node1.parent, level_of_node - 1, tree)
            else:
                adjust_rectangles(new_node1.parent)


def reinsert(tree, leaf_node):
    new_rectangle = Rectangle([entry.point for entry in leaf_node.entries])
    sorted_entries = sorted(leaf_node.entries, key=lambda entry: new_rectangle.euclidean_distance(entry.point))
    p = int(round(0.3 * Node.max_entries))
    for i in range(p):
        # remove the first p entries from N
        leaf_node.entries.remove(sorted_entries[i])
    adjust_rectangles(leaf_node)  # adjust the bounding rectangle of N
    for i in range(p):
        # reinsert the p entries that were removed from N
        insert_entry_to_tree(tree, sorted_entries[i])


def adjust_rectangles(node):
    # if the given node is the root, the adjustment of the MBR is complete
    if node.parent is not None:
        # if the node is a leaf
        if isinstance(node.entries[0], LeafEntry):
            new_points = []
            for leaf_entry in node.entries:
                new_points.append(leaf_entry.point)
            # update the MBR of the parent Entry
            node.parent.entries[node.slot_in_parent].set_rectangle(new_points)
        else:
            # if the node is internal
            new_points = []
            for entry in node.entries:
                new_points.append(entry.rectangle.bottom_left_point)
                new_points.append(entry.rectangle.top_right_point)
            # update the MBR of the parent Entry
            node.parent.entries[node.slot_in_parent].set_rectangle(new_points)
        # recursive call for the parent node
        adjust_rectangles(node.parent)


def insert_entry_to_tree(tree, leaf_entry):
    N = choose_subtree(leaf_entry, tree)  # N is always a leaf_node

    leaf_level = N.find_node_level()  # level of N is leaf_level
    # if N has room for another entry
    if len(N.entries) < Node.max_entries:
        N.entries.append(leaf_entry)
        adjust_rectangles(N)
    # if N is full
    elif len(N.entries) == Node.max_entries:
        N.entries.append(leaf_entry)
        overflow_treatment(N, leaf_level, tree)


def insert_one_by_one(max_entries, blocks):
    Node.set_overflow_treatment_level(1)  # no reinsertion for the root, so we start from 1
    tree = []
    root = Node()
    Node.set_max_entries(max_entries)
    tree.append(root)
    for block in blocks:
        for record in block:
            new_leaf_entry = LeafEntry(record)
            insert_entry_to_tree(tree, new_leaf_entry)

    return tree  # return full tree


def save_tree_to_xml(tree, filename):
    def build_xml(node_elem, node, nodes):
        for entry in node.entries:
            if isinstance(entry, Entry):
                child_node_index = nodes.index(entry.child_node)
                entry.to_xml(node_elem, child_node_index)
            else:
                entry.to_xml(node_elem)
        if node.parent is not None:
            parent_node_index = nodes.index(node.parent)
            ET.SubElement(node_elem, "ParentNodeIndex").text = str(parent_node_index)
            ET.SubElement(node_elem, "SlotInParent").text = str(node.slot_in_parent)

    root_elem = ET.Element("Nodes", max_entries=str(Node.max_entries))

    for node in tree:
        node_elem = ET.SubElement(root_elem, "Node")
        build_xml(node_elem, node, tree)

    xml_tree = ET.ElementTree(root_elem)

    # save to the specified filename with 'utf-8' encoding and pretty formatting
    xml_tree.write(filename, encoding="utf-8", xml_declaration=True)

    # load the saved XML file and format it
    xml_content = minidom.parse(filename)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(xml_content.toprettyxml(indent="    "))


def load_tree_from_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    nodes = []  # to store the nodes of the tree in order

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


# MAIN -> build tree by inserting the records one by one
#  read the data from the datafile
blocks_from_file = read_all_blocks_from_datafile("datafile.xml")
start_time = time.time()
#  build the tree by inserting the records one by one
tree = insert_one_by_one(Node.max_entries, blocks_from_file)
end_time = time.time()

print("\nBuild tree by inserting the records one by one: ", end_time-start_time, " sec")
print("The tree has ", len(tree), " nodes: ")
for i, node in enumerate(tree):
    print("node", i, "level=", node.find_node_level(), "num of entries = ", len(node.entries))
    for j, entry in enumerate(node.entries):
        if isinstance(entry, LeafEntry):
            print("       leaf_entry", j, ":", entry.record_id, entry.point)
        else:
            print("       entry", j, ":", entry.rectangle.bottom_left_point, " ", entry.rectangle.top_right_point)

print("\n")

#  save the tree to the indexfile
save_tree_to_xml(tree, "indexfile.xml")


# small example for insertion
# tree = load_tree_from_xml("indexfile2.xml")
# print("max entries = ", Node.max_entries)
# print("min entries = ", Node.min_entries)
#
# for i, n in enumerate(tree):
#     print("node ", i, "level ", n.find_node_level())
#     if isinstance(n.entries[0], LeafEntry):
#         for j, entry in enumerate(n.entries):
#             print("     leaf_entry ", j, ": ", entry.point)
#     else:
#         for j, entry in enumerate(n.entries):
#             print("     entry ", j, ": ", entry.rectangle.bottom_left_point, " ", entry.rectangle.top_right_point)
#
# print("\n")
#
# insert_entry_to_tree(tree, LeafEntry([1, 20, -3.0, 1.0]))
# insert_entry_to_tree(tree, LeafEntry([1, 30, -5.0, 2.0]))
# insert_entry_to_tree(tree, LeafEntry([1, 40, -4.0, -6.0]))
# insert_entry_to_tree(tree, LeafEntry([1, 50, -7.0, -7.0]))
# insert_entry_to_tree(tree, LeafEntry([1, 60, -6.0, -2.0]))
# insert_entry_to_tree(tree, LeafEntry([1, 70, -8.0, -2.0]))
# insert_entry_to_tree(tree, LeafEntry([1, 80, -9.0, -3.0]))
#
# for i, n in enumerate(tree):
#     print("node ", i, "level ", n.find_node_level())
#     if isinstance(n.entries[0], LeafEntry):
#         for j, entry in enumerate(n.entries):
#             print("     leaf_entry ", j, ": ", entry.point)
#     else:
#         for j, entry in enumerate(n.entries):
#             print("     entry ", j, ": ", entry.rectangle.bottom_left_point, " ", entry.rectangle.top_right_point)
