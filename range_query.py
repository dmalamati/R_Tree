import csv
from Entry import Entry, LeafEntry, Rectangle
from Node import Node


# def find_points_in_area(root_node, rectangle):
#     result = []
#     if isinstance(root_node.entries[0], Entry):
#         for entry in root_node.entries:
#             # if entry.rectangle.calculate_overlap_value(rectangle) > 0:
#             if entry.rectangle.overlaps_with_rectangle(rectangle):
#                 result.extend(find_points_in_area(entry.child_node, rectangle))
#     else:
#         for leaf_entry in root_node.entries:
#             if rectangle.overlaps_with_point(leaf_entry.point):
#                 result.append(leaf_entry)
#     return result


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
internal_node2 = Node([entry4, entry5, entry6])
internal_node3 = Node([entry7, entry8, entry9])

root_rectangle1 = Rectangle([entry1.rectangle.bottom_left_point, entry1.rectangle.top_right_point, entry2.rectangle.bottom_left_point, entry2.rectangle.top_right_point, entry3.rectangle.bottom_left_point, entry3.rectangle.top_right_point])
root_rectangle2 = Rectangle([entry4.rectangle.bottom_left_point, entry4.rectangle.top_right_point, entry5.rectangle.bottom_left_point, entry5.rectangle.top_right_point, entry6.rectangle.bottom_left_point, entry6.rectangle.top_right_point])
root_rectangle3 = Rectangle([entry7.rectangle.bottom_left_point, entry7.rectangle.top_right_point, entry8.rectangle.bottom_left_point, entry8.rectangle.top_right_point, entry9.rectangle.bottom_left_point, entry9.rectangle.top_right_point])

root_entry1 = Entry(root_rectangle1, internal_node1)
root_entry2 = Entry(root_rectangle2, internal_node2)
root_entry3 = Entry(root_rectangle3, internal_node3)

root_node = Node([root_entry1, root_entry2, root_entry3])

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

search_rectangle = Rectangle([[3.0, 5.0], [8.0, 10.0]])
print("search rect is: ", search_rectangle.bottom_left_point, " ", search_rectangle.top_right_point)
# points = find_points_in_area(tree[0], search_rectangle)
points = search_rectangle.find_points_in_rectangle(tree[0])
print(" found points in search rect:")
for i, leaf_entry in enumerate(points):
    print("entry ", i, ": ", leaf_entry.point)

