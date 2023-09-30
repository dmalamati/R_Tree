from hilbertcurve.hilbertcurve import HilbertCurve
from Entry import Rectangle, Entry, LeafEntry
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from Node import Node
import time


def read_all_blocks_from_datafile(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    # read data from block0
    block0 = root.find(".//Block[@id='" + str(0) + "']")

    blocks = [] # it won't contain block0
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

start_time = time.time()
blocks_from_file = read_all_blocks_from_datafile("datafile.xml")
max_entries = Node.max_entries
leaf_entries = []
for block in blocks_from_file:
    for record in block:
        new_leaf_entry = LeafEntry(record)
        leaf_entries.append(new_leaf_entry)

# Sorting leaf entries by Hilbert value
leaf_entries_sorted_by_hilbert = sorted(leaf_entries, key=lambda entry: compute_hilbert_value(entry.point, len(entry.point)))

# Creating Nodes (which will act as LeafNodes in this context) based on max_entries
leaf_nodes = []
current_entries = []
Node.set_max_entries(round(0.7 * max_entries))
entries_to_be_inserted = []
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



# If only one internal node is created, set it as root
if len(internal_nodes) == 1:
    root = internal_nodes[0]
    tree = [root]
    for node in leaf_nodes:
        tree.append(node)
    overflow_treatment_level = tree[-1].find_node_level()
    Node.set_max_entries(max_entries)
    for leaf_entry in entries_to_be_inserted:
        insert_entry_to_tree(tree, leaf_entry)
else:
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

    # Insert the leaf entries from the node that was not included in the tree
    overflow_treatment_level = tree[-1].find_node_level()
    Node.set_max_entries(max_entries)
    for leaf_entry in entries_to_be_inserted:
        insert_entry_to_tree(tree, leaf_entry)

end_time = time.time()
print(end_time-start_time, " sec")
save_tree_to_xml(tree, "indexfile_bulk.xml")