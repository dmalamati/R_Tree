
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
    def __int__(self, coordinates):
        self.coordinates = coordinates


class Rectangle:
    # points the list of points the rectangle will contain
    def __int__(self, number_of_dimensions, points):
        self.mbr = []
        min = []
        max = []
        for i in range(0, number_of_dimensions + 1):
            pass
            # sort points by each dimension - take max & min
        #  turn min & max list into Points ( bottom_left and top_right points of the rectangle )


