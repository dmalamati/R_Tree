import csv
from Entry import Entry, LeafEntry, Rectangle
from Node import Node
import pandas as pd

input_file = "datafile.csv"
# overflow_treatment_level = 1


# Function to read data from a specific block
def read_block_data(csv_reader, block_id):
    block_data = []

    slot = 0  # Initialize slot for each block
    for row in csv_reader:
        row_block_id = int(row[0])
        if row_block_id == block_id:
            lat = float(row[2])  # Convert lat to float
            lon = float(row[3])  # Convert lon to float
            block_data.append([block_id, slot, lat, lon])  # Include block_id, slot, lat, lon
            slot += 1  # Increment slot for each record in the block
        elif row_block_id > block_id:
            break  # Stop reading when the next block is reached

    return block_data


def choose_subtree(new_leaf_entry, tree):
    N = tree[0]  # Start at the root node

    if len(N.entries) == 0:
        return N
    while not isinstance(N.entries[0], LeafEntry):  # While N is not a leaf
        if isinstance(N.entries[0].child_node.entries[0], LeafEntry):  # if the children of N are leafs
            min_overlap_cost = float('inf')
            min_area_cost = float('inf')
            chosen_entry = None

            for i, entry in enumerate(N.entries):  # for every entry in N where N a node whose child is a leaf
                overlap_enlargement = entry.rectangle.calculate_overlap_enlargement(new_leaf_entry, i, N)
                area_enlargement = entry.rectangle.calculate_area_enlargement(new_leaf_entry)

                if overlap_enlargement < min_overlap_cost or (overlap_enlargement == min_overlap_cost and area_enlargement < min_area_cost):
                    min_overlap_cost = overlap_enlargement
                    min_area_cost = area_enlargement
                    chosen_entry = entry
        else:   # if the children of N are NOT leafs
            min_area_cost = float('inf')
            min_area = float('inf')
            chosen_entry = None

            for entry in N.entries:  # for every entry in N where N a node whose child is not a leaf
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
    if isinstance(entries[0], LeafEntry):
        # print(" in for leaf")
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
        # print(" in for not leaf")
        for axis in range(len(entries[0].rectangle.bottom_left_point)):
            entries.sort(key=lambda entry: entry.rectangle.bottom_left_point[axis])

            sum_margin = 0
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

            if sum_margin < min_sum_margin:
                min_sum_margin = sum_margin
                chosen_axis = axis

    return chosen_axis


def choose_split_index(entries, split_axis, min_entries):
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

            if overlap < min_overlap or (overlap == min_overlap and overall_area < min_area):
                min_overlap = overlap
                min_area = overall_area
                chosen_index = i
    else:
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

            if overlap < min_overlap or (overlap == min_overlap and overall_area < min_area):
                min_overlap = overlap
                min_area = overall_area
                chosen_index = i

    return entries[:chosen_index], entries[chosen_index:]


def overflow_treatment(node, level_of_node, tree):
    # global overflow_treatment_level
    if level_of_node == 0:
        # split root
        entry_group1, entry_group2 = split(node, Node.min_entries)
        if isinstance(entry_group1[0], LeafEntry):
            # print("split leaf root")
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
            tree.insert(0, new_root_node)
            tree.insert(1, new_leaf_node1)
            tree.insert(2, new_leaf_node2)
        else:
            # print("split internal root")
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

            for i, entry in enumerate(new_node1.entries):
                entry.child_node.set_parent(new_node1, i)
            for i, entry in enumerate(new_node2.entries):
                entry.child_node.set_parent(new_node2, i)

            tree.remove(node)
            tree.insert(0, new_root_node)  # root always stays at the head of the list
            tree.insert(1, new_node1)
            tree.insert(2, new_node2)

    elif level_of_node == Node.overflow_treatment_level:
        # reinsert
        # print("reinsert")
        Node.increase_overflow_treatment_level()
        # overflow_treatment_level += 1
        reinsert(tree, node)
    else:
        # split node
        entry_group1, entry_group2 = split(node, Node.min_entries)
        if isinstance(entry_group1[0], LeafEntry):
            # split leaf node
            # print("split leaf node")
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

            if len(node.parent.entries) > Node.max_entries:
                overflow_treatment(node.parent, level_of_node-1, tree)
            else:
                adjust_rectangles(node.parent)
        else:
            # split internal node
            # print("split internal node")
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

            if len(node.parent.entries) > Node.max_entries:
                overflow_treatment(new_node1.parent, level_of_node - 1, tree)
            else:
                adjust_rectangles(new_node1.parent)


def reinsert(tree, leaf_node):
    new_rectangle = Rectangle([entry.point for entry in leaf_node.entries])
    sorted_entries = sorted(leaf_node.entries, key=lambda entry: new_rectangle.euclidean_distance(entry.point))
    p = int(round(0.3 * Node.max_entries))
    for i in range(p):  # Remove the first p entries from N
        leaf_node.entries.remove(sorted_entries[i])
    adjust_rectangles(leaf_node)  # Adjust the bounding rectangle of N
    for i in range(p):
        insert_entry_to_tree(tree, sorted_entries[i])


def adjust_rectangles(node):
    if node.parent is not None:
        if isinstance(node.entries[0], LeafEntry):
            new_points = []
            for leaf_entry in node.entries:
                new_points.append(leaf_entry.point)
            node.parent.entries[node.slot_in_parent].set_rectangle(new_points)
        else:
            new_points = []
            for entry in node.entries:
                new_points.append(entry.rectangle.bottom_left_point)
                new_points.append(entry.rectangle.top_right_point)
            node.parent.entries[node.slot_in_parent].set_rectangle(new_points)
        adjust_rectangles(node.parent)


def insert_entry_to_tree(tree, leaf_entry):
    N = choose_subtree(leaf_entry, tree)  # N is a leaf_node

    leaf_level = N.find_node_level()  # level of N is leaf_level
    if len(N.entries) < Node.max_entries:
        N.entries.append(leaf_entry)
        adjust_rectangles(N)
    elif len(N.entries) == Node.max_entries:
        N.entries.append(leaf_entry)
        overflow_treatment(N, leaf_level, tree)


def insert_one_by_one(max_entries, blocks):
    # global overflow_treatment_level
    # overflow_treatment_level = 1
    Node.set_overflow_treatment_level(1)
    tree = []
    root = Node()
    Node.set_max_entries(max_entries)
    tree.append(root)
    for i, block in enumerate(blocks):
        # print("block", i)
        for j, record in enumerate(block):
            new_leaf_entry = LeafEntry(record)
            insert_entry_to_tree(tree, new_leaf_entry)

    return tree  # return full tree


with open(input_file, "r", newline="", encoding="utf-8") as csv_file:
    csv_reader = csv.reader(csv_file)
    # Skip the header row
    next(csv_reader)
    # Read and store the metadata from the second row
    metadata = next(csv_reader)
    # Parse metadata
    total_entries = int(metadata[1])
    total_blocks = int(metadata[2])
    block_size = int(metadata[3])
    # Store all block data in a list called "blocks"
    blocks = []
    # Read and process each data block
    for block_id in range(1, total_blocks + 1):
        csv_file.seek(0)  # Reset the reader position to the beginning
        next(csv_reader)  # Skip the header row
        next(csv_reader)  # Skip the metadata row

        block_data = read_block_data(csv_reader, block_id)
        blocks.append(block_data)

    max_entries = int(total_entries / total_blocks)

    print("max entries = ", max_entries)
    tree = insert_one_by_one(max_entries, blocks)
    print("tree len = ", len(tree))
    for i, node in enumerate(tree):
        print("node", i, "level=", node.find_node_level(), "num of entries = ", len(node.entries))
        for j, entry in enumerate(node.entries):
            if isinstance(entry, LeafEntry):
                print("       leaf_entry", j, ":", entry.record_id, entry.point)
            else:
                print("       entry", j, ":", entry.rectangle.bottom_left_point, " ", entry.rectangle.top_right_point)






