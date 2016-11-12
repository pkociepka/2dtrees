X, Y = 1, 0


class KDTree:
    def __init__(self, frm, to,
                 add_node=lambda x: None,
                 connect_node=lambda x, y: None,
                 orient=Y):
        self.frm = frm
        self.to = to
        self.orient = orient
        self.lower = None
        self.higher = None
        self.point = None
        self.add_node = add_node
        self.connect_node = connect_node

        self.add_node(self)

    def __eq__(self, other):
        return self.frm == other.frm and \
               self.to == other.to

    def __hash__(self):
        return hash(self.frm) + 31 * hash(self.to)

    def label(self):
        return "%d, %d" % (self.point[0], self.point[1]) if self.point is not None else ''

    def insert(self, point):
        if self.orient == Y:
            if self.point is None:
                self.point = point
                self.lower = KDTree(self.frm, (point[0], self.to[1]), self.add_node, self.connect_node, X)  # ranges
                self.higher = KDTree((point[0], self.frm[1]), self.to, self.add_node, self.connect_node, X)

                self.connect_node(self, self.lower)
                self.connect_node(self, self.higher)
            else:
                if point[0] <= self.point[0]:
                    self.lower.insert(point)
                else:
                    self.higher.insert(point)
        else:
            if self.point is None:
                self.point = point
                self.lower = KDTree(self.frm, (self.to[0], point[1]), self.add_node, self.connect_node, Y)
                self.higher = KDTree((self.frm[0], point[1]), self.to, self.add_node, self.connect_node, Y)

                self.connect_node(self, self.lower)
                self.connect_node(self, self.higher)
            else:
                if point[1] <= self.point[1]:
                    self.lower.insert(point)
                else:
                    self.higher.insert(point)
