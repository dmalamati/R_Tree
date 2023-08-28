from Entry import Entry, LeafEntry, Rectangle
from Node import Node
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom


def save_tree_to_xml(tree, filename):
    def build_xml(node_elem, node, nodes):
        for entry in node.entries:
            if isinstance(entry, Entry):
                child_node_index = nodes.index(entry.child_node) if entry.child_node else -1
                entry.to_xml(node_elem, child_node_index)
            else:
                entry.to_xml(node_elem)
        if node.parent is not None:
            parent_node_index = nodes.index(node.parent)
            ET.SubElement(node_elem, "ParentNodeIndex").text = str(parent_node_index)
            ET.SubElement(node_elem, "SlotInParent").text = str(node.slot_in_parent)

    root_elem = ET.Element("Nodes")

    for node in tree:
        node_elem = ET.SubElement(root_elem, "Node")
        build_xml(node_elem, node, tree)

    xml_string = ET.tostring(root_elem, encoding="utf-8")
    pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ", newl="\n")

    with open(filename, "w") as f:
        f.write(pretty_xml)


def load_tree_from_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    nodes = []  # To store nodes in order

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

    return nodes


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

root_rectangle1 = Rectangle(
    [entry1.rectangle.bottom_left_point, entry1.rectangle.top_right_point,
     entry2.rectangle.bottom_left_point, entry2.rectangle.top_right_point,
     entry3.rectangle.bottom_left_point, entry3.rectangle.top_right_point])
# root_rectangle1 = Rectangle([entry1.rectangle.bottom_left_point, entry1.rectangle.top_right_point, entry2.rectangle.bottom_left_point, entry2.rectangle.top_right_point])
root_rectangle2 = Rectangle(
    [entry4.rectangle.bottom_left_point, entry4.rectangle.top_right_point,
     entry5.rectangle.bottom_left_point, entry5.rectangle.top_right_point,
     entry6.rectangle.bottom_left_point, entry6.rectangle.top_right_point])
root_rectangle3 = Rectangle(
    [entry7.rectangle.bottom_left_point, entry7.rectangle.top_right_point,
     entry8.rectangle.bottom_left_point, entry8.rectangle.top_right_point,
     entry9.rectangle.bottom_left_point, entry9.rectangle.top_right_point])

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

tree = [root_node, internal_node1, internal_node2, internal_node3, leaf_node1, leaf_node2, leaf_node3, leaf_node4,
        leaf_node5, leaf_node6, leaf_node7, leaf_node8, leaf_node9]
save_tree_to_xml(tree, "indexfile.xml")
reconstructed_rtree = load_tree_from_xml("indexfile.xml")

print("tree len = ", len(tree))
for i, node in enumerate(tree):
    print("node", i, "level=", node.find_node_level(), "num of entries = ", len(node.entries))
    for j, entry in enumerate(node.entries):
        if isinstance(entry, LeafEntry):
            print("       leaf_entry", j, ":", entry.record_id, entry.point)
        else:
            print("       entry", j, ":", entry.rectangle.bottom_left_point, " ", entry.rectangle.top_right_point)
            print("       entry's child node, level=", entry.child_node.find_node_level(), "num of entries = ", len(entry.child_node.entries))
            for k, entr in enumerate(entry.child_node.entries):
                if isinstance(entr, LeafEntry):
                    print("             leaf_entry", k, ":", entr.record_id, entr.point)
                else:
                    print("             entry", k, ":", entr.rectangle.bottom_left_point, " ",
                          entr.rectangle.top_right_point)

print("\n")

print("tree len = ", len(reconstructed_rtree))
for i, node in enumerate(reconstructed_rtree):
    print("node", i, "level=", node.find_node_level(), "num of entries = ", len(node.entries))
    for j, entry in enumerate(node.entries):
        if isinstance(entry, LeafEntry):
            print("       leaf_entry", j, ":", entry.record_id, entry.point)
        else:
            print("       entry", j, ":", entry.rectangle.bottom_left_point, " ", entry.rectangle.top_right_point)
            print("       entry's child node, level=", entry.child_node.find_node_level(), "num of entries = ",
                  len(entry.child_node.entries))
            for k, entr in enumerate(entry.child_node.entries):
                if isinstance(entr, LeafEntry):
                    print("             leaf_entry", k, ":", entr.record_id, entr.point)
                else:
                    print("             entry", k, ":", entr.rectangle.bottom_left_point, " ",
                          entr.rectangle.top_right_point)
