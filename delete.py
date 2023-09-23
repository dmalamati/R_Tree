from Entry import Entry, LeafEntry, Rectangle
from Node import Node
import xml.etree.ElementTree as ET


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


def delete_entry_from_tree(tree, leaf_entry):
    N = find_leaf_node(leaf_entry, tree[0]) # removes the leaf_entry from the tree if it exists
    if N is not None:
        # if the node from which the leaf_entry was removed doesn't have enough entries
        if len(N.entries) < Node.min_entries:
            condense_tree(tree, N)
        else:
            adjust_rectangles(N)
    else:
        print("no such entry in tree")


def find_leaf_node(leaf_entry, root_node):
    nodes_to_be_examined = [root_node]
    # while we have internal nodes to examine
    while not isinstance(nodes_to_be_examined[0].entries[0], LeafEntry):
        old_nodes_index = len(nodes_to_be_examined)
        # for every old internal node in the nodes_to_be_examined list
        for i in range(old_nodes_index):
            for entry in nodes_to_be_examined[i].entries:
                # find the children that overlap with the point we want to delete and append them to the list
                if entry.rectangle.overlaps_with_point(leaf_entry.point):
                    nodes_to_be_examined.append(entry.child_node)
        # if the list hasn't grown then the point we are looking for doesn't exist
        if len(nodes_to_be_examined) == old_nodes_index:
            return None
        else:
            # remove the old nodes that we examined from the list
            nodes_to_be_examined = nodes_to_be_examined[old_nodes_index:]

    # now the list contains only leaf nodes that may contain the record(leaf_entry) we are looking for
    for leaf_node in nodes_to_be_examined:
        for entry in leaf_node.entries:
            """ if we want to delete a record only based on its point the use this if statement:
            if leaf_entry.point == entry.point:"""
            if leaf_entry.record_id == entry.record_id and leaf_entry.point == entry.point:
                # if the leaf_entry is found in a leaf_node it removes it
                leaf_node.entries.remove(entry)
                return leaf_node
    return None


def get_leaf_entries_from_node(node):
    leaf_entries = []
    nodes_to_extract_leaf_entries = [node]
    # while we have node to examine
    while len(nodes_to_extract_leaf_entries) > 0:
        # if the current node, aka the first node of the nodes_to_extract_leaf_entries list, is a leaf
        if isinstance(nodes_to_extract_leaf_entries[0].entries[0], LeafEntry):
            for entry in nodes_to_extract_leaf_entries[0].entries:
                # export the node's entries into the result list, leaf_entries
                leaf_entries.append(entry)
            nodes_to_extract_leaf_entries.pop(0)
        else:
            # if the current node is internal
            for entry in nodes_to_extract_leaf_entries[0].entries:
                # insert into the list the children of the current node
                nodes_to_extract_leaf_entries.append(entry.child_node)
            nodes_to_extract_leaf_entries.pop(0)
    return leaf_entries


def remove_children_from_tree(tree, node):
    children_of_nodes_to_be_removed = [node]
    # while we have nodes to examine
    while len(children_of_nodes_to_be_removed) > 0:
        # if the current node, aka the first node of the children_of_nodes_to_be_removed list, is internal
        if isinstance(children_of_nodes_to_be_removed[0].entries[0], Entry):
            for entry in children_of_nodes_to_be_removed[0].entries:
                # we append the child node in the children_of_nodes_to_be_removed list
                children_of_nodes_to_be_removed.append(entry.child_node)
                # and remove the child node from the tree
                tree.remove(entry.child_node)
        children_of_nodes_to_be_removed.pop(0)


def condense_tree(tree, leaf_node):
    node = leaf_node
    eliminated_nodes = []
    # while the current node is not the root
    while node.parent is not None:
        # if the current node doesn't contain enough entries
        if len(node.entries) < Node.min_entries:
            # we keep the node in the eliminated_nodes list
            eliminated_nodes.append(node)
            # and remove the corresponding entry from the parent node
            node.parent.entries.remove(node.parent.entries[node.slot_in_parent])
            # update slot_in_parent for all the children nodes of the parent node's entries
            for i, entry in enumerate(node.parent.entries):
                entry.child_node.set_slot_in_parent(i)
            tree.remove(node)
            # if current node is internal then remove its children from the tree
            if isinstance(node.entries[0], Entry):
                remove_children_from_tree(tree, node)
            node = node.parent
        # if the current node contains enough entries
        else:
            adjust_rectangles(node)
            break

    root = tree[0]
    # if root has only one Entry then the child must become the new root
    if len(root.entries) == 1 and isinstance(root.entries[0], Entry) and len(tree) > 1:
        for entry in root.entries:
            entry.child_node.set_parent(None, None)
        tree.remove(root)

    Node.set_overflow_treatment_level(tree[-1].find_node_level())
    # for every node that was eliminated due to entry shortage
    for node in eliminated_nodes:
        # we get all the LeafEntries that descend from the current node
        leaf_entries_to_insert = get_leaf_entries_from_node(node)
        # and we reinsert them in the tree
        for leaf_entry in leaf_entries_to_insert:
            insert_entry_to_tree(tree, leaf_entry)


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
print("max entries = ", Node.max_entries)

for i, n in enumerate(tree):
    print("node ", i, "level ", n.find_node_level())
    if isinstance(n.entries[0], LeafEntry):
        for j, entry in enumerate(n.entries):
            print("     leaf_entry ", j, ": ", entry.point)
    else:
        for j, entry in enumerate(n.entries):
            print("     entry ", j, ": ", entry.rectangle.bottom_left_point, " ", entry.rectangle.top_right_point)

print("\n")

insert_entry_to_tree(tree, LeafEntry([1, 20, -3.0, 1.0]))
insert_entry_to_tree(tree, LeafEntry([1, 30, -5.0, 2.0]))
insert_entry_to_tree(tree, LeafEntry([1, 40, -4.0, -6.0]))
insert_entry_to_tree(tree, LeafEntry([1, 50, -7.0, -7.0]))
insert_entry_to_tree(tree, LeafEntry([1, 60, -6.0, -2.0]))
insert_entry_to_tree(tree, LeafEntry([1, 70, -8.0, -2.0]))  # κανει reinsert οποτε δεν γινει slpit για indexfile2!

for i, n in enumerate(tree):
    print("node ", i, "level ", n.find_node_level())
    if isinstance(n.entries[0], LeafEntry):
        for j, entry in enumerate(n.entries):
            print("     leaf_entry ", j, ": ", entry.point)
    else:
        for j, entry in enumerate(n.entries):
            print("     entry ", j, ": ", entry.rectangle.bottom_left_point, " ", entry.rectangle.top_right_point)
