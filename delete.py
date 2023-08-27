import csv
from Entry import Entry, LeafEntry, Rectangle
from Node import Node

input_file = "datafile.csv"
overflow_treatment_level = 1


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
    global overflow_treatment_level
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

    elif level_of_node == overflow_treatment_level:
        # reinsert
        # print("reinsert")
        overflow_treatment_level += 1
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


def delete_entry_from_tree(tree, leaf_entry):
    N = find_leaf_node(leaf_entry, tree[0])
    if N is not None:
        # leaf_entry has been removed
        if len(N.entries) < Node.min_entries:
            condense_tree(tree, N)
        else:
            adjust_rectangles(N)
    else:
        print("no such entry in tree")


def find_leaf_node(leaf_entry, root_node):
    nodes_to_be_examined = [root_node]
    while not isinstance(nodes_to_be_examined[0].entries[0], LeafEntry):
        old_nodes_index = len(nodes_to_be_examined)
        for i in range(old_nodes_index):
            for entry in nodes_to_be_examined[i].entries:
                if entry.rectangle.overlaps_with_point(leaf_entry.point):
                    nodes_to_be_examined.append(entry.child_node)
        if len(nodes_to_be_examined) == old_nodes_index:
            return None
        else:
            nodes_to_be_examined = nodes_to_be_examined[old_nodes_index:]
    for leaf_node in nodes_to_be_examined:
        for entry in leaf_node.entries:
            if leaf_entry.record_id == entry.record_id and leaf_entry.point == entry.point:
                # if the leaf_entry is found in a leaf_node it removes it
                leaf_node.entries.remove(entry)
                return leaf_node
    return None


def get_leaf_entries_from_node(node):
    leaf_entries = []
    nodes_to_extract_leaf_entries = [node]
    while len(nodes_to_extract_leaf_entries) > 0:
        if isinstance(nodes_to_extract_leaf_entries[0].entries[0], LeafEntry):
            for entry in nodes_to_extract_leaf_entries[0].entries:
                leaf_entries.append(entry)
            nodes_to_extract_leaf_entries.pop(0)
        else:
            for entry in nodes_to_extract_leaf_entries[0].entries:
                nodes_to_extract_leaf_entries.append(entry.child_node)
            nodes_to_extract_leaf_entries.pop(0)
    return leaf_entries


def remove_children_from_tree(tree, node):
    children_of_nodes_to_be_removed = [node]
    while len(children_of_nodes_to_be_removed) > 0:
        if isinstance(children_of_nodes_to_be_removed[0].entries[0], Entry):
            for entry in children_of_nodes_to_be_removed[0].entries:
                children_of_nodes_to_be_removed.append(entry.child_node)
                tree.remove(entry.child_node)
        children_of_nodes_to_be_removed.pop(0)


def condense_tree(tree, leaf_node):
    node = leaf_node
    eliminated_nodes = []
    while node.parent is not None:
        if len(node.entries) < Node.min_entries:
            eliminated_nodes.append(node)
            node.parent.entries.remove(node.parent.entries[node.slot_in_parent])
            # update slot_in_parent for all the children nodes of the entries
            for i, entry in enumerate(node.parent.entries):
                entry.child_node.set_slot_in_parent(i)
            tree.remove(node)
            # if node is internal node then remove its children from the tree
            if isinstance(node.entries[0], Entry):
                remove_children_from_tree(tree, node)
            node = node.parent
        else:
            adjust_rectangles(node)
            break

    root = tree[0]
    # if root has only one Entry then the child must become the root
    if len(root.entries) == 1 and isinstance(root.entries[0], Entry) and len(tree) > 1:
        for entry in root.entries:
            entry.child_node.set_parent(None, None)
        tree.remove(root)

    # insert leaf entries of eliminated_nodes in tree
    global overflow_treatment_level
    overflow_treatment_level = tree[-1].find_node_level()
    for node in eliminated_nodes:
        leaf_entries_to_insert = get_leaf_entries_from_node(node)
        for leaf_entry in leaf_entries_to_insert:
            insert_entry_to_tree(tree, leaf_entry)


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

    # START TEST: split
    leaf_entry1 = LeafEntry([1, 0, 0.0, 4.0])
    leaf_entry2 = LeafEntry([1, 1, 1.0, 2.0])
    leaf_entry3 = LeafEntry([1, 2, 1.0, 3.0])

    leaf_entry4 = LeafEntry([1, 3, 2.0, 2.0])
    leaf_entry5 = LeafEntry([1, 4, 2.0, 3.0])
    leaf_entry6 = LeafEntry([1, 5, 4.0, 1.0])

    leaf_entry7 = LeafEntry([1, 6, 1.0, 7.0])
    leaf_entry8 = LeafEntry([1, 7, 2.0, 6.0])
    leaf_entry9 = LeafEntry([1, 8, 3.0, 8.0])

    leaf_entry10 = LeafEntry([1, 9, 7.0, 5.0])
    leaf_entry11 = LeafEntry([1, 10, 8.0, 7.0])
    leaf_entry12 = LeafEntry([1, 11, 9.0, 6.0])

    leaf_entry13 = LeafEntry([1, 12, 8.0, 2.0])
    leaf_entry14 = LeafEntry([1, 13, 9.0, 4.0])
    leaf_entry15 = LeafEntry([1, 14, 12.0, 1.0])

    leaf_entry16 = LeafEntry([1, 15, 10.0, 5.0])
    leaf_entry17 = LeafEntry([1, 16, 10.0, 7.0])
    leaf_entry18 = LeafEntry([1, 17, 11.0, 5.0])

    leaf_entry19 = LeafEntry([1, 18, 6.0, 9.0])
    leaf_entry20 = LeafEntry([1, 19, 6.0, 10.0])
    leaf_entry21 = LeafEntry([1, 20, 7.0, 10.0])

    leaf_entry22 = LeafEntry([1, 21, 10.0, 11.0])
    leaf_entry23 = LeafEntry([1, 22, 12.0, 12.0])
    leaf_entry24 = LeafEntry([1, 23, 13.0, 9.0])

    leaf_entry25 = LeafEntry([1, 24, 8.0, 13.0])
    leaf_entry26 = LeafEntry([1, 25, 9.0, 14.0])
    leaf_entry27 = LeafEntry([1, 26, 10.0, 13.0])

    leaf_node1 = Node([leaf_entry1, leaf_entry2, leaf_entry3])
    leaf_node2 = Node([leaf_entry4, leaf_entry5, leaf_entry6])
    leaf_node3 = Node([leaf_entry7, leaf_entry8, leaf_entry9])
    leaf_node4 = Node([leaf_entry10, leaf_entry11, leaf_entry12])
    leaf_node5 = Node([leaf_entry13, leaf_entry14, leaf_entry15])
    leaf_node6 = Node([leaf_entry16, leaf_entry17, leaf_entry18])
    leaf_node7 = Node([leaf_entry19, leaf_entry20, leaf_entry21])
    leaf_node8 = Node([leaf_entry22, leaf_entry23, leaf_entry24])
    leaf_node9 = Node([leaf_entry25, leaf_entry26, leaf_entry27])

    rectangle1 = Rectangle([leaf_entry1.point, leaf_entry2.point, leaf_entry3.point])
    rectangle2 = Rectangle([leaf_entry4.point, leaf_entry5.point, leaf_entry6.point])
    rectangle3 = Rectangle([leaf_entry7.point, leaf_entry8.point, leaf_entry9.point])
    rectangle4 = Rectangle([leaf_entry10.point, leaf_entry11.point, leaf_entry12.point])
    rectangle5 = Rectangle([leaf_entry13.point, leaf_entry14.point, leaf_entry15.point])
    rectangle6 = Rectangle([leaf_entry16.point, leaf_entry17.point, leaf_entry18.point])
    rectangle7 = Rectangle([leaf_entry19.point, leaf_entry20.point, leaf_entry21.point])
    rectangle8 = Rectangle([leaf_entry22.point, leaf_entry23.point, leaf_entry24.point])
    rectangle9 = Rectangle([leaf_entry25.point, leaf_entry26.point, leaf_entry27.point])

    entry1 = Entry(rectangle1, leaf_node1)
    entry2 = Entry(rectangle2, leaf_node2)
    entry3 = Entry(rectangle3, leaf_node3)
    entry4 = Entry(rectangle4, leaf_node4)
    entry5 = Entry(rectangle5, leaf_node5)
    entry6 = Entry(rectangle6, leaf_node6)
    entry7 = Entry(rectangle7, leaf_node7)
    entry8 = Entry(rectangle8, leaf_node8)
    entry9 = Entry(rectangle9, leaf_node9)

    internal_node1 = Node([entry1, entry2, entry3])
    # internal_node1 = Node([entry1, entry2])
    internal_node2 = Node([entry4, entry5, entry6])
    internal_node3 = Node([entry7, entry8, entry9])

    root_rectangle1 = Rectangle([entry1.rectangle.bottom_left_point, entry1.rectangle.top_right_point, entry2.rectangle.bottom_left_point, entry2.rectangle.top_right_point, entry3.rectangle.bottom_left_point, entry3.rectangle.top_right_point])
    # root_rectangle1 = Rectangle([entry1.rectangle.bottom_left_point, entry1.rectangle.top_right_point, entry2.rectangle.bottom_left_point, entry2.rectangle.top_right_point])
    root_rectangle2 = Rectangle([entry4.rectangle.bottom_left_point, entry4.rectangle.top_right_point, entry5.rectangle.bottom_left_point, entry5.rectangle.top_right_point, entry6.rectangle.bottom_left_point, entry6.rectangle.top_right_point])
    root_rectangle3 = Rectangle([entry7.rectangle.bottom_left_point, entry7.rectangle.top_right_point, entry8.rectangle.bottom_left_point, entry8.rectangle.top_right_point, entry9.rectangle.bottom_left_point, entry9.rectangle.top_right_point])

    root_entry1 = Entry(root_rectangle1, internal_node1)
    root_entry2 = Entry(root_rectangle2, internal_node2)
    root_entry3 = Entry(root_rectangle3, internal_node3)

    root_node = Node([root_entry1, root_entry2, root_entry3])
    # root_node = Node([root_entry1, root_entry2])

    leaf_node1.set_parent(internal_node1, 0)
    leaf_node2.set_parent(internal_node1, 1)
    leaf_node3.set_parent(internal_node1, 2)
    leaf_node4.set_parent(internal_node2, 0)
    leaf_node5.set_parent(internal_node2, 1)
    leaf_node6.set_parent(internal_node2, 2)
    leaf_node7.set_parent(internal_node3, 0)
    leaf_node8.set_parent(internal_node3, 1)
    leaf_node9.set_parent(internal_node3, 2)

    internal_node1.set_parent(root_node, 0)
    internal_node2.set_parent(root_node, 1)
    internal_node3.set_parent(root_node, 2)

    Node.set_max_entries(4)

    tree = [root_node, internal_node1, internal_node2, internal_node3, leaf_node1, leaf_node2, leaf_node3, leaf_node4, leaf_node5, leaf_node6, leaf_node7, leaf_node8, leaf_node9]
    # tree = [root_node, internal_node1, internal_node2, leaf_node1, leaf_node2, leaf_node4, leaf_node5, leaf_node6]

    # leaf_entry1 = LeafEntry([1, 0, 1.0, 1.0])
    # leaf_entry2 = LeafEntry([1, 1, 1.0, 4.0])
    # leaf_entry3 = LeafEntry([1, 2, 5.0, 1.0])
    #
    # leaf_entry4 = LeafEntry([1, 3, 3.0, 3.0])
    # leaf_entry5 = LeafEntry([1, 4, 5.0, 3.0])
    # leaf_entry6 = LeafEntry([1, 5, 5.0, 5.0])
    #
    # leaf_entry7 = LeafEntry([1, 6, 4.0, 3.0])
    # leaf_entry8 = LeafEntry([1, 7, 4.0, 6.0])
    # leaf_entry9 = LeafEntry([1, 8, 3.0, 6.0])
    #
    # leaf_node1 = Node([leaf_entry1, leaf_entry2, leaf_entry3])
    # leaf_node2 = Node([leaf_entry4, leaf_entry5, leaf_entry6])
    # leaf_node3 = Node([leaf_entry7, leaf_entry8, leaf_entry9])
    #
    # rectangle1 = Rectangle([leaf_entry1.point, leaf_entry2.point, leaf_entry3.point])
    # rectangle2 = Rectangle([leaf_entry4.point, leaf_entry5.point, leaf_entry6.point])
    # rectangle3 = Rectangle([leaf_entry7.point, leaf_entry8.point, leaf_entry9.point])
    #
    # entry1 = Entry(rectangle1, leaf_node1)
    # entry2 = Entry(rectangle2, leaf_node2)
    # entry3 = Entry(rectangle3, leaf_node3)
    #
    # root = Node([entry1, entry2, entry3])
    # Node.set_max_entries(4)
    # leaf_node1.set_parent(root, 0)
    # leaf_node2.set_parent(root, 1)
    # leaf_node3.set_parent(root, 2)
    # tree = [root, leaf_node1, leaf_node2, leaf_node3]

    for i, n in enumerate(tree):
        print("node ", i, "level ", n.find_node_level())
        if isinstance(n.entries[0], LeafEntry):
            for j, entry in enumerate(n.entries):
                print("     leaf_entry ", j, ": ", entry.point)
        else:
            for j, entry in enumerate(n.entries):
                print("     entry ", j, ": ", entry.rectangle.bottom_left_point, " ", entry.rectangle.top_right_point)

    leaf_entry_to_find = LeafEntry([1, 1, 1.0, 2.0])
    delete_entry_from_tree(tree, leaf_entry_to_find)

    # for i, n in enumerate(tree):
    #     print("node ", i, "level ", n.find_node_level())
    #     if isinstance(n.entries[0], LeafEntry):
    #         for j, entry in enumerate(n.entries):
    #             print("     leaf_entry ", j, ": ", entry.point)
    #     else:
    #         for j, entry in enumerate(n.entries):
    #             print("     entry ", j, ": ", entry.rectangle.bottom_left_point, " ", entry.rectangle.top_right_point)
    #
    # print("new deletion:")
    leaf_entry_to_find = LeafEntry([1, 2, 1.0, 3.0])
    delete_entry_from_tree(tree, leaf_entry_to_find)
    delete_entry_from_tree(tree, LeafEntry([1, 0, 0.0, 4.0]))
    delete_entry_from_tree(tree, LeafEntry([1, 5, 4.0, 1.0]))
    delete_entry_from_tree(tree, LeafEntry([1, 3, 2.0, 2.0]))
    print("len of tree", len(tree))

    for i, n in enumerate(tree):
        print("node ", i, "level ", n.find_node_level())
        if isinstance(n.entries[0], LeafEntry):
            for j, entry in enumerate(n.entries):
                print("     leaf_entry ", j, ": ", entry.point)
        else:
            for j, entry in enumerate(n.entries):
                print("     entry ", j, ": ", entry.rectangle.bottom_left_point, " ", entry.rectangle.top_right_point)



