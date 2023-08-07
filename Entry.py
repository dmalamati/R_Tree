
class Entry:
    def __init__(self, rectangle, child_node):
        self.rectangle = rectangle
        self.child_node = child_node


class LeafEntry:
    def __init__(self, point, record_id):
        self.point = point
        self.record_id = record_id


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

# class Rectangle:
#     # points the list of points the rectangle will contain
#     def __int__(self, number_of_dimensions, points):
#         self.mbr = []
#         min = []
#         max = []
#         for i in range(0, number_of_dimensions + 1):
#             pass
#             # sort points by each dimension - take max & min
#         #  turn min & max list into Points ( bottom_left and top_right points of the rectangle )


# Example usage for 2D rectangle
# points_2d = [[1.0, 2.0], [4.0, 5.0], [0.0, 2.5]]
# rectangle_2d = Rectangle(points_2d)
#
# print("Bottom Left:", rectangle_2d.bottom_left_point.coordinates)
# print("Top Right:", rectangle_2d.top_right_point.coordinates)


