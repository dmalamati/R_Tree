
class Entry:
    def __init__(self, rectangle, child_node):
        self.rectangle = rectangle
        self.child_node = child_node

#
# class LeafEntry:
#     def __init__(self, point, record_id):
#         self.point = point
#         self.record_id = record_id


class LeafEntry:
    def __init__(self, record):
        self.record_id = (record[0], record[1])
        self.point = record[2:]


class Point:
    # coordinates is a list with the coordinates for one point
    def __init__(self, coordinates):
        self.coordinates = coordinates


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

        self.bottom_left_point = Point(self.bottom_left_point)
        self.top_right_point = Point(self.top_right_point)

    def calculate_overlap_enlargement(self, new_leaf_entry, index, node):
        # Create a new rectangle using the existing corners and the new_leaf_entry's point
        new_rectangle_points = [
            self.bottom_left_point.coordinates,
            self.top_right_point.coordinates,
            new_leaf_entry.point
        ]
        new_rectangle = Rectangle(new_rectangle_points)

        # Calculate the overlap enlargement cost
        overlap_enlargement = 0
        number_of_dimensions = len(self.bottom_left_point.coordinates)

        for i, entry in enumerate(node.entries):
            if i == index:
                continue
            # bottom_left_point = [float('inf')] * number_of_dimensions
            # top_right_point = [float('-inf')] * number_of_dimensions
            # for d in range(number_of_dimensions):
            #     bottom_left_point[d] = max(new_rectangle.bottom_left_point.coordinates[d], entry.rectangle.bottom_left_point.coordinates[d])
            #     top_right_point[d] = min(new_rectangle.top_right_point.coordinates[d], entry.rectangle.top_right_point.coordinates[d])
            # # find intersected area
            # overlap = 1
            # for d in range(number_of_dimensions):
            #     overlap *= top_right_point[d] - bottom_left_point[d]
            #
            # if overlap <= 0:
            #     overlap_enlargement += 0
            # else:
            #     overlap_enlargement += overlap
            overlap_enlargement += entry.rectangle.calculate_overlap_value(new_rectangle)
        print(new_rectangle.bottom_left_point.coordinates, " ", new_rectangle.top_right_point.coordinates)

        return overlap_enlargement

    def calculate_area_enlargement(self, new_leaf_entry):
        # Create a new rectangle using the existing corners and the new_leaf_entry's point
        new_rectangle_points = [
            self.bottom_left_point.coordinates,
            self.top_right_point.coordinates,
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

        for i in range(len(self.bottom_left_point.coordinates)):
            area *= self.top_right_point.coordinates[i] - self.bottom_left_point.coordinates[i]

        return area

    def calculate_margin(self):
        margin = 0

        for i in range(len(self.bottom_left_point.coordinates)):
            margin += self.top_right_point.coordinates[i] - self.bottom_left_point.coordinates[i]

        return margin

    def calculate_overlap_value(self, other_rectangle):
        overlap_value = 1

        for i in range(len(self.bottom_left_point.coordinates)):
            overlap_extent = min(self.top_right_point.coordinates[i], other_rectangle.top_right_point.coordinates[i]) -\
                             max(self.bottom_left_point.coordinates[i],
                                 other_rectangle.bottom_left_point.coordinates[i])
            if overlap_extent > 0:
                overlap_value *= overlap_extent
            else:
                overlap_value *= 0
        # print(overlap_value)
        return overlap_value

    # def calculate_overlap_value(self, other_rectangle):
    #     overlap_value = 0
    #     number_of_dimensions = len(self.bottom_left_point.coordinates)
    #
    #     bottom_left_point = [float('inf')] * number_of_dimensions
    #     top_right_point = [float('-inf')] * number_of_dimensions
    #     for d in range(number_of_dimensions):
    #         bottom_left_point[d] = max(other_rectangle.bottom_left_point.coordinates[d],
    #                                    self.bottom_left_point.coordinates[d])
    #         top_right_point[d] = min(other_rectangle.top_right_point.coordinates[d],
    #                                  self.top_right_point.coordinates[d])
    #     # find intersected area
    #     overlap = 1
    #     for d in range(number_of_dimensions):
    #         overlap *= top_right_point[d] - bottom_left_point[d]
    #
    #     if overlap <= 0:
    #         overlap_value += 0
    #     else:
    #         overlap_value += overlap
    #
    #     return overlap_value


# Example usage for 2D rectangle
# points_2d = [[1.0, 2.0], [2.0, 3.0], [0.0, 4.0]]
# rectangle_2d = Rectangle(points_2d)
# print("Bottom Left:", rectangle_2d.bottom_left_point.coordinates)
# print("Top Right:", rectangle_2d.top_right_point.coordinates)
# record = [0, 1, 5.0, 6.0]
# new_leaf = LeafEntry(record)
# area = rectangle_2d.calculate_area_enlargement(new_leaf)
# print(area)
# enlarge = rectangle_2d.calculate_overlap_enlargement(new_leaf)
# print(enlarge)

# print("Bottom Left:", rectangle_2d.bottom_left_point.coordinates)
# print("Top Right:", rectangle_2d.top_right_point.coordinates)

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
