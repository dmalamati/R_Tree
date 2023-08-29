import math
import xml.etree.ElementTree as ET


class Entry:
    def __init__(self, rectangle, child_node):
        self.rectangle = rectangle
        self.child_node = child_node

    def set_rectangle(self, points):
        self.rectangle = Rectangle(points)

    def set_child_node(self, new_child_node):
        self.child_node = new_child_node

    def to_xml(self, parent, child_node_index):
        entry_elem = ET.SubElement(parent, "Entry")
        self.rectangle.to_xml(entry_elem)
        ET.SubElement(entry_elem, "ChildNodeIndex").text = str(child_node_index)


class LeafEntry:
    def __init__(self, record):
        self.record_id = (record[0], record[1])
        self.point = record[2:]

    def to_xml(self, parent):
        leaf_entry_elem = ET.SubElement(parent, "LeafEntry")
        record_id_elem = ET.SubElement(leaf_entry_elem, "RecordID")
        record_id_elem.text = str(self.record_id[0]) + "," + str(self.record_id[1])
        point_elem = ET.SubElement(leaf_entry_elem, "Point")
        point_elem.text = " ".join(map(str, self.point))


class Rectangle:
    def __init__(self, points):
        self.bottom_left_point = None
        self.top_right_point = None

        num_of_dimensions = len(points[0])

        self.bottom_left_point = [float('inf')] * num_of_dimensions  # list initialized with the value positive infinity
        self.top_right_point = [float('-inf')] * num_of_dimensions  # list initialized with the value minimum infinity

        for point in points:
            for i in range(num_of_dimensions):
                self.bottom_left_point[i] = min(self.bottom_left_point[i], point[i])  # min of all dimensions
                self.top_right_point[i] = max(self.top_right_point[i], point[i])  # max of all dimensions

    def center(self):
        num_of_dimensions = len(self.bottom_left_point)
        center_point = []

        for i in range(num_of_dimensions):
            a = self.bottom_left_point[i]
            b = self.top_right_point[i]
            center_point.append((a + b) / 2)

        return center_point

    def euclidean_distance(self, point):
        center_of_rectangle = self.center()
        squared_diff_sum = 0
        for i in range(len(center_of_rectangle)):
            squared_diff_sum += (center_of_rectangle[i] - point[i]) ** 2

        return math.sqrt(squared_diff_sum)

    def calculate_overlap_enlargement(self, new_leaf_entry, index, node):
        # Create a new rectangle using the existing corners and the new_leaf_entry's point
        new_rectangle_points = [
            self.bottom_left_point,
            self.top_right_point,
            new_leaf_entry.point
        ]
        new_rectangle = Rectangle(new_rectangle_points)

        # Calculate the overlap enlargement cost
        overlap_enlargement = 0
        # number_of_dimensions = len(self.bottom_left_point)

        for i, entry in enumerate(node.entries):
            if i == index:
                continue
            overlap_enlargement += entry.rectangle.calculate_overlap_value(new_rectangle)
        # print(new_rectangle.bottom_left_point, " ", new_rectangle.top_right_point)

        return overlap_enlargement

    def __str__(self):
        return f"[[{self.bottom_left_point[0]}, {self.bottom_left_point[1]}], [{self.top_right_point[0]}, {self.top_right_point[1]}]]"

    def calculate_area_enlargement(self, new_leaf_entry):
        # Create a new rectangle using the existing corners and the new_leaf_entry's point
        new_rectangle_points = [
            self.bottom_left_point,
            self.top_right_point,
            new_leaf_entry.point
        ]
        new_rectangle = Rectangle(new_rectangle_points)
        # Calculate the area enlargement cost
        area_before = self.calculate_area()
        area_after = new_rectangle.calculate_area()

        return area_after - area_before

    def calculate_area(self):
        # Calculate the area of the current rectangle
        area = 1

        for i in range(len(self.bottom_left_point)):
            area *= self.top_right_point[i] - self.bottom_left_point[i]

        return area

    def calculate_margin(self):
        margin = 0

        for i in range(len(self.bottom_left_point)):
            margin += self.top_right_point[i] - self.bottom_left_point[i]

        return margin

    def calculate_overlap_value(self, other_rectangle):
        overlap_value = 1

        for i in range(len(self.bottom_left_point)):
            overlap_extent = min(self.top_right_point[i], other_rectangle.top_right_point[i]) -\
                             max(self.bottom_left_point[i],
                                 other_rectangle.bottom_left_point[i])
            if overlap_extent > 0:
                overlap_value *= overlap_extent
            else:
                overlap_value *= 0
        # print(overlap_value)
        return overlap_value

    def overlaps_with_rectangle(self, other_rectangle):
        for i in range(len(self.bottom_left_point)):
            if self.top_right_point[i] < other_rectangle.bottom_left_point[i] or \
                    self.bottom_left_point[i] > other_rectangle.top_right_point[i]:
                return False
        return True

    def overlaps_with_point(self, point):
        for i in range(len(self.bottom_left_point)):
            if not(self.bottom_left_point[i] <= point[i] <= self.top_right_point[i]):
                return False
        return True

    # RANGE QUERY IN RECTANGLE
    def find_points_in_rectangle(self, root_node):
        result = []
        if isinstance(root_node.entries[0], Entry):
            for entry in root_node.entries:
                # if entry.rectangle.calculate_overlap_value(rectangle) > 0:
                if self.overlaps_with_rectangle(entry.rectangle):
                    result.extend(self.find_points_in_rectangle(entry.child_node))
        else:
            for leaf_entry in root_node.entries:
                if self.overlaps_with_point(leaf_entry.point):
                    result.append(leaf_entry)
        return result

    def to_xml(self, parent):
        rectangle_elem = ET.SubElement(parent, "Rectangle")
        bottom_left_point_elem = ET.SubElement(rectangle_elem, "BottomLeftPoint")
        top_right_point_elem = ET.SubElement(rectangle_elem, "TopRightPoint")
        bottom_left_point_elem.text = " ".join(map(str, self.bottom_left_point))
        top_right_point_elem.text = " ".join(map(str, self.top_right_point))

# Example usage for 2D rectangle
# points_2d = [[1.0, 2.0], [2.0, 3.0], [0.0, 4.0]]
# rectangle_2d = Rectangle(points_2d)
# print("Bottom Left:", rectangle_2d.bottom_left_point)
# print("Top Right:", rectangle_2d.top_right_point)
# record = [0, 1, 5.0, 6.0]
# new_leaf = LeafEntry(record)
# area = rectangle_2d.calculate_area_enlargement(new_leaf)
# print(area)
# enlarge = rectangle_2d.calculate_overlap_enlargement(new_leaf)
# print(enlarge)

# print("Bottom Left:", rectangle_2d.bottom_left_point)
# print("Top Right:", rectangle_2d.top_right_point)

# entry = [1, 0, 41.5163899, 26.5291294, 44.23, 56.322]
# new = LeafEntry(entry)
# print(new.point)
# print(new.record_id)
# Example usage



# leaf_node = [LeafEntry([1, 0, 0.0, 0.0]), LeafEntry([1, 1, 1.0, 1.0]), LeafEntry([1, 2, 0.5, 6.0]), LeafEntry([1, 3, 2.0, 3.0]), LeafEntry([1, 4, 4.0, 5.0]), LeafEntry([1, 4, 5.0, 2.0]), LeafEntry([1, 4, 3.0, 4.0])]
# # leaf_node = [LeafEntry([1, 0, 1.0, 2.0]), LeafEntry([1, 1, 2.0, 3.0]), LeafEntry([1, 2, 0.0, 4.0]), LeafEntry([1, 3, 5.0, 5.0]), LeafEntry([1, 4, 1.0, 3.0])]
# # leaf_node = [LeafEntry([1, 0, 0.0, 2.0]), LeafEntry([1, 0, 0.0, 3.0]), LeafEntry([1, 0, 1.0, 2.0]), LeafEntry([1, 0, 1.0, 3.0])]
# # leaf_node = [LeafEntry([1, 0, 0.0, 2.0]), LeafEntry([1, 0, 0.0, 3.0]), LeafEntry([1, 0, 0.0, 4.0]), LeafEntry([1, 0, 2.0, 3.0]), LeafEntry([1, 0, 2.0, 4.0]), LeafEntry([1, 0, 2.0, 5.0])]
# minimum = 3
# group1, group2 = split(leaf_node, minimum)
# print("Group 1:")
# for entry in group1:
#     print(entry.point)
# print("Group 2:")
# for entry in group2:
#     print(entry.point)

# leaf_entry13 = LeafEntry([1, 3, 0.0, 0.0])
# leaf_entry14 = LeafEntry([1, 4, 1.0, 1.0])
# leaf_entry15 = LeafEntry([1, 5, 4.0, 4.0])
#
# rectangle5 = Rectangle([leaf_entry13.point, leaf_entry14.point, leaf_entry15.point])
# print(rectangle5.bottom_left_point, " ", rectangle5.top_right_point)
# print(rectangle5.overlaps_with_point([4.0, 0.0001]))
