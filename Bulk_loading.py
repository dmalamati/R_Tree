import csv
from Node import Node
from R_tree import read_block_data

input_file = "datafile2.csv"


def hilbert_value(data):
    if len(data) == 2 and all(isinstance(point, (list, tuple)) and len(point) == 2 for point in data):
        x_mid = (data[0][0] + data[1][0]) / 2
        y_mid = (data[0][1] + data[1][1]) / 2
    elif len(data) == 4:
        x_mid = data[2]
        y_mid = data[3]
    else:
        raise ValueError(f"Unexpected data format: {data}")

    return x_mid + y_mid


def create_leaf_nodes(sorted_blocks):
    leaf_nodes = []
    for i in range(0, len(sorted_blocks), Node.max_entries):
        leaf_node = Node(entries=sorted_blocks[i:i + Node.max_entries])
        leaf_nodes.append(leaf_node)
    return leaf_nodes


def create_higher_level_nodes(nodes):
    while len(nodes) > 1:
        next_level_nodes = []
        nodes_sorted_by_creation_time = sorted(nodes, key=lambda node: id(node))
        for i in range(0, len(nodes_sorted_by_creation_time), Node.max_entries):
            internal_node = Node(entries=nodes_sorted_by_creation_time[i:i + Node.max_entries])
            next_level_nodes.append(internal_node)
        nodes = next_level_nodes
    return nodes[0]


def validate_tree(root):
    nodes_to_check = [(root, 1)]  # Each element is a tuple (node, depth/level)
    all_entries = set()  # Used to check for duplicate entries
    max_depth = 1

    while nodes_to_check:
        node, level = nodes_to_check.pop(0)

        if not isinstance(node.entries[0], Node):  # Leaf node
            max_depth = max(max_depth, level)
            for entry in node.entries:
                tuple_entry = tuple(tuple(point) for point in entry)
                if tuple_entry in all_entries:
                    raise ValueError(f"Duplicate entry found: {tuple_entry}")
                all_entries.add(tuple_entry)
            continue

        # If not a leaf node, add its children to the list of nodes to check
        nodes_to_check.extend([(child, level + 1) for child in node.entries])

    if max_depth < 2:
        raise ValueError("Tree depth is less than 2, indicating no branching has occurred.")

    print("Tree validated successfully!")


with open(input_file, "r", newline="", encoding="utf-8") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)
    metadata = next(csv_reader)

    total_entries = int(metadata[1])
    total_blocks = int(metadata[2])
    block_size = int(metadata[3])

    blocks = []
    for block_id in range(1, total_blocks + 1):
        csv_file.seek(0)
        next(csv_reader)
        next(csv_reader)

        block_data = read_block_data(csv_reader, block_id)
        blocks.append(block_data)

    sorted_blocks = sorted(blocks, key=lambda block: sum(hilbert_value(rect) for rect in block) / len(block))
    print("Sorted Blocks:")
    print("Sorted Blocks with Hilbert Values:")
    for idx, block in enumerate(sorted_blocks, start=1):
        block_hilbert_value = sum(hilbert_value(rect) for rect in block) / len(block)
        print(f"Block {idx} (Hilbert Value: {block_hilbert_value}):")
        for rect_idx, rect in enumerate(block, start=1):
            print(f"  Rectangle {rect_idx}: {rect}")
        print()


    leaf_nodes = create_leaf_nodes(sorted_blocks)

    root = create_higher_level_nodes(leaf_nodes)

