import csv

from hilbertcurve.hilbertcurve import HilbertCurve

from Entry import Rectangle, Entry, LeafEntry, Point
from Node import Node


def compute_hilbert_value(point, dimensions):
    p = 10
    hilbert_curve = HilbertCurve(p, dimensions)
    return hilbert_curve.distance_from_point(point)


def compute_mbr_centroid(mbr):
    """Compute centroid for an MBR."""
    x_avg = (mbr.bottom_left_point.coordinates[0] + mbr.top_right_point.coordinates[0]) / 2
    y_avg = (mbr.bottom_left_point.coordinates[1] + mbr.top_right_point.coordinates[1]) / 2
    return [x_avg, y_avg]


def bulk_load_higher_level_nodes(lower_level_nodes, max_entries):
    """Bulk load higher-level nodes."""
    # Sort nodes based on the Hilbert value of their MBR's centroid
    sorted_nodes = sorted(lower_level_nodes, key=lambda x: compute_hilbert_value(compute_mbr_centroid(x.mbr)))
    for node in sorted_nodes:
        print(node.mbr)
    higher_level_nodes = []

    # Create higher-level nodes based on max_entries
    while sorted_nodes:
        nodes_for_higher_level_node = sorted_nodes[:max_entries]
        mbrs = [node.mbr for node in nodes_for_higher_level_node]

        points = []
        for mbr in mbrs:
            points.extend([mbr.bottom_left_point.coordinates, mbr.top_right_point.coordinates])

        combined_mbr = Rectangle(points)

        new_node = Node(entries=nodes_for_higher_level_node)
        new_node.mbr = combined_mbr
        higher_level_nodes.append(new_node)

        # Remove the nodes now included in a higher-level node
        sorted_nodes = sorted_nodes[max_entries:]

    return higher_level_nodes


def print_tree(node, level=1, indent="  "):
    """Prints the tree starting from the given node in a structured format."""
    if node is None:
        return

    # Print current node's MBR
    print(indent * level + f"Level {level} - Node MBR: {node.mbr}")

    # If the entries of the node are other nodes (i.e., non-leaf nodes),
    # recursively print those nodes.
    if node.entries and isinstance(node.entries[0], Node):
        for child_node in node.entries:
            # For non-leaf nodes, print the MBR of each child node
            print(indent * (level + 1) + f"Contained Rectangle: {child_node.mbr}")
            print_tree(child_node, level + 1)

    # If the entries of the node are LeafEntry (i.e., leaf nodes),
    # print the leaf node data.
    elif node.entries and isinstance(node.entries[0], LeafEntry):
        for leaf in node.entries:
            print(indent * (level + 1) + f"Point: {leaf.point}")


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


input_file = "datafile.csv"

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
            lat = point_data[2]
            long = point_data[3]
            record = [block_id, slot, lat, long]
            leaf_entry = LeafEntry(record)
            leaf_entries.append(leaf_entry)

    # Sorting leaf entries by Hilbert value
    leaf_entries_sorted_by_hilbert = sorted(leaf_entries,
                                            key=lambda entry: compute_hilbert_value(entry.point, len(entry.point)))

    # Creating Nodes (which will act as LeafNodes in this context) based on max_entries
    leaf_nodes = []
    current_entries = []
    Node.set_max_entries(max_entries)
    for entry in leaf_entries_sorted_by_hilbert:
        if len(current_entries) < Node.max_entries:
            current_entries.append(entry)
        else:
            # Once we hit the max, we create a new Node and start a new list of entries
            leaf_nodes.append(Node(current_entries))
            current_entries = [entry]

    # Don't forget the last set of entries if they exist
    if current_entries:
        leaf_nodes.append(Node(current_entries))

    # Now, 'leaf_nodes' is a list containing all your Nodes acting as leaf nodes with entries up to max_entries.

    print(f"Created {len(leaf_nodes)} leaf nodes.")

    for i, node in enumerate(leaf_nodes):
        print(f"Node {i + 1}:")
        print(node)  # Using the __str__ method
        for entry in node.entries:
            print(f" - Record ID: {entry.record_id}, Point: {entry.point}")
        print("------")

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
            internal_nodes.append(Node(current_entry_list))
            current_entry_list = [entry]

    # Don't forget the last set of entries if they exist
    if current_entry_list:
        internal_nodes.append(Node(current_entry_list))

    # Printing the created nodes with their entries
    print(f"Created {len(internal_nodes)} internal nodes.")
    for i, node in enumerate(internal_nodes):
        print(f"Node {i + 1}:")
        for entry in node.entries:
            print(f" - MBR: {entry.rectangle}, Child Node: {entry.child_node}")
        print("------")

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
