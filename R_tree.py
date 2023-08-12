import csv
from Entry import Entry, LeafEntry, Rectangle, Point
from Node import Node
import pandas as pd

input_file = "datafile.csv"


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

#################################################################works
# def choose_subtree(tree, leaf_level, new_leaf_entry):
#     N = tree[0]  # Start at the root node
#
#     if len(N) == 0:
#         return N
#     while not isinstance(N[0], LeafEntry):  # While N is not a leaf
#         if isinstance(N[0].child_node, LeafEntry):  # if the children of N are leafs
#             min_overlap_cost = float('inf')
#             min_area_cost = float('inf')
#             chosen_entry = None
#
#             for entry in N:  # for every entry in N where N a node whose child is a leaf
#                 overlap_enlargement = entry.rectangle.calculate_overlap_enlargement(new_leaf_entry)
#                 area_enlargement = entry.rectangle.calculate_area_enlargement(new_leaf_entry)
#
#                 if overlap_enlargement < min_overlap_cost or (overlap_enlargement == min_overlap_cost and area_enlargement < min_area_cost):
#                     min_overlap_cost = overlap_enlargement
#                     min_area_cost = area_enlargement
#                     chosen_entry = entry
#         else:
#             min_area_cost = float('inf')
#             chosen_entry = None
#
#             for entry in N:  # for every entry in N where N a node whose child is not a leaf
#                 area_enlargement = entry.rectangle.calculate_area_enlargement(new_leaf_entry)
#
#                 if area_enlargement < min_area_cost:
#                     min_area_cost = area_enlargement
#                     chosen_entry = entry
#
#         N = chosen_entry.child_node
#
#     return N


# def split(leaf_node, min_entries):
#     split_axis = choose_split_axis(leaf_node, min_entries)
#     group1, group2 = choose_split_index(leaf_node, split_axis, min_entries)
#
#     return group1, group2

# ---------------------------------------------- works with Node objects
def choose_subtree(tree, leaf_level, new_leaf_entry):
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

                if area_enlargement < min_area_cost or (area_enlargement == min_area_cost and new_area < min_area):
                    min_area_cost = area_enlargement
                    min_area = new_area
                    chosen_entry = entry

        N = chosen_entry.child_node

    return N


def split(node_entries, min_entries):
    split_axis = choose_split_axis(node_entries, min_entries)
    group1, group2 = choose_split_index(node_entries, split_axis, min_entries)

    return group1, group2


# def choose_split_axis(entries, min_entries):
#     min_sum_margin = float('inf')
#     chosen_axis = None
#
#     for axis in range(len(entries[0].point)):
#         entries.sort(key=lambda entry: entry.point[axis])
#
#         sum_margin = 0
#         for i in range(min_entries, len(entries) - min_entries + 1):
#             prev_rect = Rectangle([entry.point for entry in entries[:i]])
#             next_rect = Rectangle([entry.point for entry in entries[i:]])
#             sum_margin += prev_rect.calculate_margin() + next_rect.calculate_margin()
#
#         if sum_margin < min_sum_margin:
#             min_sum_margin = sum_margin
#             chosen_axis = axis
#         # print("min_sum_margin: ", min_sum_margin, "from axis: ", axis)
#     # print("axis: ", chosen_axis)
#     return chosen_axis

def choose_split_axis(entries, min_entries):
    min_sum_margin = float('inf')
    chosen_axis = None
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


# def choose_split_index(entries, split_axis, min_entries):
#     entries.sort(key=lambda entry: entry.point[split_axis])
#
#     min_overlap = float('inf')
#     min_area = float('inf')
#     chosen_index = None
#
#     for i in range(min_entries, len(entries) - min_entries + 1):
#         prev_rect = Rectangle([entry.point for entry in entries[:i]])
#         # for entry in entries[:i]:
#         #     print(entry.point)
#         # print("\n")
#         next_rect = Rectangle([entry.point for entry in entries[i:]])
#         # for entry in entries[i:]:
#         #     print(entry.point)
#         overlap = prev_rect.calculate_overlap_value(next_rect)
#         # print(" overlap of rect1 ", prev_rect.bottom_left_point.coordinates, " ", prev_rect.top_right_point.coordinates," and rect2 ", next_rect.bottom_left_point.coordinates, " ", next_rect.top_right_point.coordinates, " :", overlap)
#         overall_area = prev_rect.calculate_area() + next_rect.calculate_area()
#         # print("overall area: ", overall_area)
#         if overlap < min_overlap or (overlap == min_overlap and overall_area < min_area):
#             min_overlap = overlap
#             min_area = overall_area
#             chosen_index = i
#
#     return entries[:chosen_index], entries[chosen_index:]


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
            print(" overlap of rect1 ", rect1.bottom_left_point.coordinates, " ", rect1.top_right_point.coordinates," and rect2 ", rect2.bottom_left_point.coordinates, " ", rect2.top_right_point.coordinates, " :", overlap)
            print("overall area: ", overall_area)
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
            print(" overlap of rect1 ", rect1.bottom_left_point.coordinates, " ", rect1.top_right_point.coordinates," and rect2 ", rect2.bottom_left_point.coordinates, " ", rect2.top_right_point.coordinates, " :", overlap)
            print("overall area: ", overall_area)

            if overlap < min_overlap or (overlap == min_overlap and overall_area < min_area):
                min_overlap = overlap
                min_area = overall_area
                chosen_index = i

    return entries[:chosen_index], entries[chosen_index:]


def overflow_treatment(node, leaf_level, max_entries):
    pass


# Read data from the CSV file
def insert_one_by_one(max_entries, blocks):
    tree = []
    leaf_level = 0
    root = []
    tree.append(root)
    for block in blocks:
        for record in block:
            new_entry = LeafEntry(record)
            N = choose_subtree(tree, leaf_level)
            if len(N.entries) < Node.max_entries:
                N.insert_entry(new_entry)
            elif len(N.entries) == Node.max_entries:
                return tree

    return tree
    # return full tree


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

    # print(blocks)
    # for block_data in blocks:
    #     for record in block_data:
    #         print(record)
    #         print("\n")
    ####################################################################
    # num_of_dimensions = 2
    # max_entries = 4
    # tree = []
    # root = []
    # tree.append(root)
    # leaf_level = 0
    # for block in blocks:
    #     for record in block:
    #         new_entry = LeafEntry(record)
    #         N = choose_subtree(tree, leaf_level, new_entry)
    #         if len(N) < max_entries:
    #             N.append(new_entry)
    #         elif len(N) == max_entries:
    #             break
    #
    # for node in tree:
    #     print("node")
    #     for entry in node:
    #         print(entry.record_id, " ", entry.point)
    ####################################################################

    # START TEST: choose_subtree
    # num_of_dimensions = 2
    # max_entries = 3
    # leaf_entry1 = LeafEntry([1, 0, 1.0, 2.0])
    # leaf_entry2 = LeafEntry([1, 1, 2.0, 3.0])
    # leaf_entry3 = LeafEntry([1, 2, 0.0, 4.0])
    # leaf_entry4 = LeafEntry([1, 3, 5.0, 6.0])
    # leaf_entry5 = LeafEntry([1, 4, 1.0, 3.0])
    # leaf_entry6 = LeafEntry([1, 5, 2.0, 2.0])
    # leaf_entry7 = LeafEntry([1, 5, 6.0, 4.0])
    # leaf_entry8 = LeafEntry([1, 5, 8.0, 6.0])
    #
    # # leaf_node1 = [leaf_entry3, leaf_entry1, leaf_entry5]
    # # leaf_node2 = [leaf_entry2, leaf_entry6, leaf_entry4]
    # leaf_node1 = Node([leaf_entry3, leaf_entry1, leaf_entry5])
    # leaf_node2 = Node([leaf_entry2, leaf_entry6, leaf_entry4])
    # leaf_node3 = Node([leaf_entry7, leaf_entry8])
    #
    # rectangle1 = Rectangle([[0.0, 4.0], [1.0, 2.0], [1.0, 3.0]])
    # rectangle2 = Rectangle([[2.0, 3.0], [2.0, 2.0], [5.0, 6.0]])
    # rectangle3 = Rectangle([[6.0, 4.0], [8.0, 5.0]])
    #
    # entry1 = Entry(rectangle1, leaf_node1)
    # entry2 = Entry(rectangle2, leaf_node2)
    # entry3 = Entry(rectangle3, leaf_node3)
    #
    # big_rect = Rectangle([[0.0, 4.0], [1.0, 2.0], [1.0, 3.0], [2.0, 3.0], [2.0, 2.0], [5.0, 6.0], [6.0, 4.0], [8.0, 5.0]])
    # # internal_node1 = Node([entry1, entry2, entry3])
    # # il_entry = Entry(big_rect, internal_node1)
    #
    # # root = [entry1, entry2]
    # root = Node([entry1, entry2, entry3])
    # leaf_node1.set_parent(root)
    # leaf_node2.set_parent(root)
    # leaf_node3.set_parent(root)
    # tree = [root, leaf_node1, leaf_node2, leaf_node3]
    # new_leaf_entry = LeafEntry([2, 1, 7.0, 6.0])
    # N = choose_subtree(tree, 1, new_leaf_entry)

    # if len(N) < max_entries:
    #     N.append(new_leaf_entry)
    # elif len(N) == max_entries:  # overflow_treatment
    #     N.append(new_leaf_entry)

    # for entry in N:
    #     print(entry.point)
    # END TEST: choose_subtree

    # START TEST: split
    leaf_entry1 = LeafEntry([1, 0, 1.0, 2.0])
    leaf_entry2 = LeafEntry([1, 1, 2.0, 3.0])
    leaf_entry3 = LeafEntry([1, 2, 0.0, 4.0])
    leaf_entry4 = LeafEntry([1, 3, 5.0, 6.0])
    leaf_entry5 = LeafEntry([1, 4, 1.0, 3.0])
    leaf_entry6 = LeafEntry([1, 5, 2.0, 2.0])
    leaf_entry7 = LeafEntry([1, 5, 6.0, 4.0])
    leaf_entry8 = LeafEntry([1, 5, 8.0, 6.0])
    leaf_entry9 = LeafEntry([1, 5, 7.0, 5.0])

    leaf_node1 = Node([leaf_entry3, leaf_entry1, leaf_entry5])
    leaf_node2 = Node([leaf_entry2, leaf_entry6, leaf_entry4])
    leaf_node3 = Node([leaf_entry7, leaf_entry8, leaf_entry9])

    rectangle1 = Rectangle([[0.0, 4.0], [1.0, 3.0], [1.0, 2.0]])
    rectangle2 = Rectangle([[2.0, 2.0], [2.0, 3.0], [5.0, 6.0]])
    rectangle3 = Rectangle([[6.0, 4.0], [8.0, 6.0], [7.0, 5.0]])

    # rectangle1 = Rectangle([[0.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    # rectangle2 = Rectangle([[2.0, 1.0], [3.0, 2.0], [2.5, 1.5]])
    # rectangle3 = Rectangle([[5.0, 3.0], [5.0, 4.0], [6.0, 4.0]])
    # rectangle4 = Rectangle([[5.0, 2.0], [5.5, 1.0], [6.0, 1.5]])
    entry1 = Entry(rectangle1, leaf_node1)
    entry2 = Entry(rectangle2, leaf_node2)
    entry3 = Entry(rectangle3, leaf_node3)
    # entry4 = Entry(rectangle4, leaf_node2)
    # node = [entry1, entry2, entry3, entry4]
    # node = Node([entry1, entry2, entry3])
    leaf_node2.entries.append(LeafEntry([1, 5, 3.0, 3.0]))
    node = leaf_node2
    group1, group2 = split(node.entries, 2)
    if isinstance(node.entries[0], LeafEntry):
        print("Leaf")
        print("Group 1:")
        for entry in group1:
            print(entry.point)
        print("Group 2:")
        for entry in group2:
            print(entry.point)
    else:
        print("Not Leaf")
        print("Group 1:")
        for entry in group1:
            print(entry.rectangle.bottom_left_point.coordinates, " ", entry.rectangle.top_right_point.coordinates)
        print("Group 2:")
        for entry in group2:
            print(entry.rectangle.bottom_left_point.coordinates, " ", entry.rectangle.top_right_point.coordinates)
    # END TEST: split

    # leaf_node = [LeafEntry([1, 0, 0.0, 0.0]), LeafEntry([1, 1, 1.0, 1.0]), LeafEntry([1, 2, 0.5, 6.0]), LeafEntry([1, 3, 2.0, 3.0]), LeafEntry([1, 4, 4.0, 5.0]), LeafEntry([1, 4, 5.0, 2.0]), LeafEntry([1, 4, 3.0, 4.0])]
    # minimum = 3
    # group1, group2 = split(leaf_node, minimum)
    # print("Group 1:")
    # for entry in group1:
    #     print(entry.point)
    # print("Group 2:")
    # for entry in group2:
    #     print(entry.point)

# Process and print the blocks outside the loop
# for block_id, block_data in enumerate(blocks, start=1):
#     columns = ["block_id", "slot", "lat", "lon"]
#     df = pd.DataFrame(block_data, columns=columns)
#
#     print(f"Block {block_id}:")
#     print(df)
#
#     print("\n")  # Separate blocks with an empty line
