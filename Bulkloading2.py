import csv

from hilbertcurve.hilbertcurve import HilbertCurve

from Entry import Rectangle, Entry, LeafEntry
from Node import Node


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
                # print("overlap: ", overlap_enlargement)
                # print("area: ", area_enlargement)

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
                # print("area enlargement: ", area_enlargement)
                # print("new area: ", new_area)

                if area_enlargement < min_area_cost or (area_enlargement == min_area_cost and new_area < min_area):
                    min_area_cost = area_enlargement
                    min_area = new_area
                    chosen_entry = entry

        N = chosen_entry.child_node

    return N  # the most suitable leaf node for the new leaf_entry


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
        for axis in range(len(entries[0].rectangle.bottom_left_point.coordinates)):
            entries.sort(key=lambda entry: entry.rectangle.bottom_left_point.coordinates[axis])

            sum_margin = 0
            for i in range(min_entries, len(entries) - min_entries + 1):
                rect1_points = []
                for entry in entries[:i]:
                    rect1_points.append(entry.rectangle.bottom_left_point.coordinates)
                    rect1_points.append(entry.rectangle.top_right_point.coordinates)
                rect1 = Rectangle(rect1_points)

                rect2_points = []
                for entry in entries[i:]:
                    rect2_points.append(entry.rectangle.bottom_left_point.coordinates)
                    rect2_points.append(entry.rectangle.top_right_point.coordinates)
                rect2 = Rectangle(rect2_points)

                sum_margin += rect1.calculate_margin() + rect2.calculate_margin()

            if sum_margin < min_sum_margin:
                min_sum_margin = sum_margin
                chosen_axis = axis

            # entries.sort(key=lambda entry: entry.rectangle.top_right_point.coordinates[axis])

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
            # print(" overlap of rect1 ", rect1.bottom_left_point.coordinates, " ", rect1.top_right_point.coordinates," and rect2 ", rect2.bottom_left_point.coordinates, " ", rect2.top_right_point.coordinates, " :", overlap)
            # print("overall area: ", overall_area)
            if overlap < min_overlap or (overlap == min_overlap and overall_area < min_area):
                min_overlap = overlap
                min_area = overall_area
                chosen_index = i
    else:
        entries.sort(key=lambda entry: entry.rectangle.bottom_left_point.coordinates[split_axis])

        min_overlap = float('inf')
        min_area = float('inf')
        chosen_index = None

        for i in range(min_entries, len(entries) - min_entries + 1):
            rect1_points = []
            for entry in entries[:i]:
                rect1_points.append(entry.rectangle.bottom_left_point.coordinates)
                rect1_points.append(entry.rectangle.top_right_point.coordinates)
            rect1 = Rectangle(rect1_points)

            rect2_points = []
            for entry in entries[i:]:
                rect2_points.append(entry.rectangle.bottom_left_point.coordinates)
                rect2_points.append(entry.rectangle.top_right_point.coordinates)
            rect2 = Rectangle(rect2_points)

            overlap = rect1.calculate_overlap_value(rect2)
            overall_area = rect1.calculate_area() + rect2.calculate_area()
            # print(" overlap of rect1 ", rect1.bottom_left_point.coordinates, " ", rect1.top_right_point.coordinates," and rect2 ", rect2.bottom_left_point.coordinates, " ", rect2.top_right_point.coordinates, " :", overlap)
            # print("overall area: ", overall_area)

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
            # print("split root by leaf")
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
            # print("split root by internal")
            new_node1 = Node(entry_group1)
            new_node2 = Node(entry_group2)

            rect1_points = []
            for entry in entry_group1:
                rect1_points.append(entry.rectangle.bottom_left_point.coordinates)
                rect1_points.append(entry.rectangle.top_right_point.coordinates)
            rect1 = Rectangle(rect1_points)
            root_entry1 = Entry(rect1, new_node1)

            rect2_points = []
            for entry in entry_group2:
                rect2_points.append(entry.rectangle.bottom_left_point.coordinates)
                rect2_points.append(entry.rectangle.top_right_point.coordinates)
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
            new_leaf_node1 = Node(entry_group1)
            new_leaf_node2 = Node(entry_group2)

            rect1 = Rectangle([entry.point for entry in entry_group1])
            internal_entry1 = Entry(rect1, new_leaf_node1)
            rect2 = Rectangle([entry.point for entry in entry_group2])
            internal_entry2 = Entry(rect2, new_leaf_node2)

            node.parent.entries = node.parent.entries[:node.slot_in_parent] + [internal_entry1, internal_entry2] + node.parent.entries[node.slot_in_parent + 1:]

            new_leaf_node1.set_parent(node.parent, node.parent.entries.index(internal_entry1))
            new_leaf_node2.set_parent(node.parent, node.parent.entries.index(internal_entry2))

            # replace the old node with the new ones
            index_to_replace = tree.index(node)
            # tree = tree[:index_to_replace] + [new_leaf_node1, new_leaf_node2] + tree[index_to_replace + 1:]
            tree.insert(index_to_replace, new_leaf_node1)
            tree.insert(index_to_replace + 1, new_leaf_node2)
            tree.remove(node)

            # print("length of tree:", len(tree))
            # for k, entr in enumerate(node.parent.entries):
            #     print("rect", k, ": ", entr.rectangle.bottom_left_point.coordinates, " ", entr.rectangle.top_right_point.coordinates)

            if len(node.parent.entries) > Node.max_entries:
                overflow_treatment(new_leaf_node1.parent, level_of_node-1, tree)
            else:
                adjust_rectangles(new_leaf_node1.parent)
        else:
            # split internal node
            new_node1 = Node(entry_group1)
            new_node2 = Node(entry_group2)

            rect1_points = []
            for entry in entry_group1:
                rect1_points.append(entry.rectangle.bottom_left_point.coordinates)
                rect1_points.append(entry.rectangle.top_right_point.coordinates)
            rect1 = Rectangle(rect1_points)
            internal_entry1 = Entry(rect1, new_node1)

            rect2_points = []
            for entry in entry_group2:
                rect2_points.append(entry.rectangle.bottom_left_point.coordinates)
                rect2_points.append(entry.rectangle.top_right_point.coordinates)
            rect2 = Rectangle(rect2_points)
            internal_entry2 = Entry(rect2, new_node2)

            node.parent.entries = node.parent.entries[:node.slot_in_parent] + [internal_entry1, internal_entry2] + node.parent.entries[node.slot_in_parent + 1:]

            new_node1.set_parent(node.parent, node.parent.entries.index(internal_entry1))
            new_node2.set_parent(node.parent, node.parent.entries.index(internal_entry2))

            for i, entry in enumerate(new_node1.entries):
                entry.child_node.set_parent(new_node1, i)
            for i, entry in enumerate(new_node2.entries):
                entry.child_node.set_parent(new_node2, i)

            # replace the old node with the new ones
            index_to_replace = tree.index(node)
            # tree = tree[:index_to_replace] + [new_node1, new_node2] + tree[index_to_replace + 1:]
            tree.insert(index_to_replace, new_node1)
            tree.insert(index_to_replace + 1, new_node2)
            tree.remove(node)

            # print(" Internal node split")
            # for k, entr in enumerate(node.parent.entries):
            #     print("rect", k, ": ", entr.rectangle.bottom_left_point.coordinates, " ", entr.rectangle.top_right_point.coordinates)

            if len(node.parent.entries) > Node.max_entries:
                overflow_treatment(new_node1.parent, level_of_node - 1, tree)
            else:
                adjust_rectangles(new_node1.parent)
            #  something is sus


def reinsert(tree, leaf_node):
    new_rectangle = Rectangle([entry.point for entry in leaf_node.entries])
    sorted_entries = sorted(leaf_node.entries, key=lambda entry: new_rectangle.euclidean_distance(entry.point), reverse=True)
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
                new_points.append(entry.rectangle.bottom_left_point.coordinates)
                new_points.append(entry.rectangle.top_right_point.coordinates)
            node.parent.entries[node.slot_in_parent].set_rectangle(new_points)
        adjust_rectangles(node.parent)


def insert_entry_to_tree(tree, leaf_entry):
    N = choose_subtree(leaf_entry, tree)  # N is a leaf_node
    # leaf_level = find_node_level(N)
    leaf_level = N.find_node_level()  # level of N is leaf_level
    if len(N.entries) < Node.max_entries:
        N.entries.append(leaf_entry)
        adjust_rectangles(N)
    elif len(N.entries) == Node.max_entries:
        N.entries.append(leaf_entry)
        overflow_treatment(N, leaf_level, tree)

def compute_hilbert_value(point, dimensions):
    p = 10
    hilbert_curve = HilbertCurve(p, dimensions)
    return hilbert_curve.distance_from_point(point)


def gather_leaf_nodes_from_node(node):
    """Recursively gather all leaf nodes descending from a given node."""
    if not node.entries or isinstance(node.entries[0], LeafEntry):
        return [node]

    leaf_nodes = []
    for entry in node.entries:
        leaf_nodes.extend(gather_leaf_nodes_from_node(entry.child_node))
    return leaf_nodes

def gather_leaf_entries_from_node(node):
    """
    Recursively traverse from an internal node to its leaf nodes,
    collecting leaf entries along the way.
    """
    if isinstance(node.entries[0], LeafEntry):
        return node.entries
    else:
        leaf_entries = []
        for entry in node.entries:
            leaf_entries.extend(gather_leaf_entries_from_node(entry.child_node))
        return leaf_entries
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


input_file = "datafile2.csv"

with open(input_file, "r", newline="", encoding="utf-8") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)
    metadata = next(csv_reader)

    total_entries = int(metadata[1])
    total_blocks = int(metadata[2])
    block_size = int(metadata[3])
    max_entries = round(block_size / total_blocks)
    blocks = []
    for block_id in range(1, total_blocks + 1):
        csv_file.seek(0)
        next(csv_reader)
        next(csv_reader)
        block_data = read_block_data(csv_reader, block_id)
        blocks.append(block_data)

    # Process blocks to create leaf entries
    leaf_entries = []
    for block in blocks:
        for point_data in block:
            block_id = point_data[0]
            slot = point_data[1]
            coordinates = point_data[2:]
            record = [block_id, slot]
            for x in coordinates:
                record.append(x)
            leaf_entry = LeafEntry(record)
            leaf_entries.append(leaf_entry)

    # Sorting leaf entries by Hilbert value
    leaf_entries_sorted_by_hilbert = sorted(leaf_entries,
                                            key=lambda entry: compute_hilbert_value(entry.point, len(entry.point)))

    # Creating Nodes (which will act as LeafNodes in this context) based on max_entries
    leaf_nodes = []
    current_entries = []
    Node.set_max_entries(round(0.7 * max_entries))
    entries_to_be_inserted = []
    print(Node.max_entries)
    print(Node.min_entries)
    for entry in leaf_entries_sorted_by_hilbert:
        if len(current_entries) < Node.max_entries:
            current_entries.append(entry)
        else:
            # Once we hit the max, we create a new Node and start a new list of entries
            leaf_nodes.append(Node(current_entries))
            current_entries = [entry]

    # At the end of loop, check the number of entries in current_entries
    if len(current_entries) >= Node.min_entries:
        # If they are more than the minimum, create a new Node
        leaf_nodes.append(Node(current_entries))
    else:
        # If less than minimum, append them to entries_to_be_inserted
        entries_to_be_inserted.extend(current_entries)

    print("++++++++++++")

    # Print details of entries_to_be_inserted
    print("Entries to be Inserted:")
    for leaf_entry in entries_to_be_inserted:
        print(f"Record ID: {leaf_entry.record_id}, Point: {leaf_entry.point}")
    print("++++++++++++")

    # Now, 'leaf_nodes' is a list containing all your Nodes acting as leaf nodes with entries up to max_entries.

    print(f"Created {len(leaf_nodes)} leaf nodes.")


    # 1. Calculate MBR for each leaf node
    for node in leaf_nodes:
        # Extract all points from the node's entries
        points = [entry.point for entry in node.entries]

        # Calculate MBR using the Rectangle class
        node.mbr = Rectangle(points)  # Assuming Node class has the attribute mbr

    # 2. Create Entry instances
    entries = [Entry(node.mbr, node) for node in leaf_nodes]

    # 3. Create new nodes based on the Entry instances
    internal_nodes = []  # List of nodes to store the Entry instances
    current_entry_list = []

    for entry in entries:
        if len(current_entry_list) < Node.max_entries:
            current_entry_list.append(entry)
        else:
            # Once we hit the max, we create a new Node and start a new list of entries
            new_node = Node(current_entry_list)
            internal_nodes.append(new_node)
            # Set the parent for the child nodes
            for ent in current_entry_list:
                ent.child_node.set_parent(new_node, current_entry_list.index(ent))
            current_entry_list = [entry]

    # Don't forget the last set of entries if they exist
    if current_entry_list:
        new_node = Node(current_entry_list)
        internal_nodes.append(new_node)
        # Set the parent for the child nodes
        for ent in current_entry_list:
            ent.child_node.set_parent(new_node, current_entry_list.index(ent))

    # Printing the created nodes with their entries
    print(f"Created {len(internal_nodes)} internal nodes.")

    # If only one internal node is created, set it as root
    if len(internal_nodes) == 1:
        root = internal_nodes[0]
        tree = [root]
        for node in leaf_nodes:
            tree.append(node)
        for i, node in enumerate(tree):
            print("node", i, "level=", node.find_node_level())
            for j, entry in enumerate(node.entries):
                if isinstance(entry, LeafEntry):
                    print("       leaf_entry", j, ":", entry.point)
                else:
                    print("       entry", j, ":", entry.rectangle.bottom_left_point.coordinates, " ",
                          entry.rectangle.top_right_point.coordinates)

        overflow_treatment_level = tree[-1].find_node_level()
        Node.set_max_entries(max_entries)
        for leaf_entry in entries_to_be_inserted:
            insert_entry_to_tree(tree, leaf_entry)
        print("---------------------------------------")
        for i, node in enumerate(tree):
            print("node", i, "level=", node.find_node_level())
            for j, entry in enumerate(node.entries):
                if isinstance(entry, LeafEntry):
                    print("       leaf_entry", j, ":", entry.point)
                else:
                    print("       entry", j, ":", entry.rectangle.bottom_left_point.coordinates, " ",
                          entry.rectangle.top_right_point.coordinates)

        print("The single internal node has been set as the root.")
    else:
        tree1 = []
        for node in internal_nodes:
            tree1.append(node)
        for node in leaf_nodes:
            tree1.append(node)
        for i, node in enumerate(tree1):
            print("node", i, "level=", node.find_node_level())
            for j, entry in enumerate(node.entries):
                if isinstance(entry, LeafEntry):
                    print("       leaf_entry", j, ":", entry.point)
                else:
                    print("       entry", j, ":", entry.rectangle.bottom_left_point.coordinates, " ",
                          entry.rectangle.top_right_point.coordinates)
        print("---------------------------")
        # If the last internal node has entries less than the minimum required
        # Check if the last internal node has fewer entries than the minimum
        if len(internal_nodes[-1].entries) < Node.min_entries:
            # Retrieve the leaf entries from the internal node and append them to `entries_to_be_inserted`
            leaf_entries_from_last_node = gather_leaf_entries_from_node(internal_nodes[-1])
            entries_to_be_inserted.extend(leaf_entries_from_last_node)

            # Gather the leaf nodes of the last internal node
            leaf_nodes_from_last_node = gather_leaf_nodes_from_node(internal_nodes[-1])

            # Remove these leaf nodes from leaf_nodes
            for leaf_node in leaf_nodes_from_last_node:
                if leaf_node in leaf_nodes:
                    leaf_nodes.remove(leaf_node)

            # Remove this last internal node
            internal_nodes = internal_nodes[:-1]

        # Group the internal nodes to create upper-level nodes
        upper_level_nodes = internal_nodes
        while len(upper_level_nodes) > 1:
            next_level_nodes = []

            # Group the nodes based on max_entries
            group = []
            for node in upper_level_nodes:
                if len(group) < Node.max_entries:
                    group.append(node)
                else:
                    # Form a new internal node with the group
                    mbr = Rectangle(
                        [entry.mbr.bottom_left_point for entry in group] +
                        [entry.mbr.top_right_point for entry in group]
                    )  # calculate MBR
                    new_internal = Node([Entry(mbr, node) for node in group])
                    next_level_nodes.append(new_internal)

                    # Set the parent for the child nodes
                    for i, entry in enumerate(new_internal.entries):
                        entry.child_node.set_parent(new_internal, i)

                    group = [node]

            # Handle the remaining group, if any
            if group:
                mbr = Rectangle(
                    [entry.mbr.bottom_left_point for entry in group] +
                    [entry.mbr.top_right_point for entry in group]
                )  # calculate MBR
                new_internal = Node([Entry(mbr, node) for node in group])
                next_level_nodes.append(new_internal)

                # Set the parent for the child nodes
                for i, entry in enumerate(new_internal.entries):
                    entry.child_node.set_parent(new_internal, i)

            # Set the next_level_nodes as the upper_level_nodes for the next iteration
            upper_level_nodes = next_level_nodes

        # If there's only one node left, consider it as the root
        if len(upper_level_nodes) == 1:
            root = upper_level_nodes[0]

        tree = [root] + [node for node in upper_level_nodes if node != root] + leaf_nodes

        for i, node in enumerate(tree):
            print("node", i, "level=", node.find_node_level())
            for j, entry in enumerate(node.entries):
                if isinstance(entry, LeafEntry):
                    print("       leaf_entry", j, ":", entry.point)
                else:
                    print("       entry", j, ":", entry.rectangle.bottom_left_point.coordinates, " ",
                          entry.rectangle.top_right_point.coordinates)

        print("Entries to be Inserted:")
        for leaf_entry in entries_to_be_inserted:
            print(f"Record ID: {leaf_entry.record_id}, Point: {leaf_entry.point}")
        print("++++++++++++")

        # Insert the leaf entries from the node that was not included in the tree
        overflow_treatment_level = tree[-1].find_node_level()
        Node.set_max_entries(max_entries)
        for leaf_entry in entries_to_be_inserted:
            insert_entry_to_tree(tree, leaf_entry)
        print("---------------")
        for i, node in enumerate(tree):
            print("node", i, "level=", node.find_node_level())
            for j, entry in enumerate(node.entries):
                if isinstance(entry, LeafEntry):
                    print("       leaf_entry", j, ":", entry.point)
                else:
                    print("       entry", j, ":", entry.rectangle.bottom_left_point.coordinates, " ",
                          entry.rectangle.top_right_point.coordinates)

        print("Done")


    print(Node.max_entries)
    print(Node.min_entries)
    '''
    # You already have the leaf nodes
    current_level_nodes = leaf_nodes

    # Create higher level nodes until the root is reached
    all_levels = [current_level_nodes]  # List to store nodes at all levels

    while len(current_level_nodes) > 1:
        current_level_nodes = bulk_load_higher_level_nodes(current_level_nodes, max_entries)
        all_levels.append(current_level_nodes)

    # The root node
    root = all_levels[-1][0]

    # Print nodes at each level
    for level, nodes in enumerate(all_levels, start=1):
        print(f"Level {level} Nodes:")
        for node in nodes:
            print(node.mbr)

    print(max_entries)
    print_tree(root)

'''
