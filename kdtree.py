X, Y = 1, 0


class KDTree:
    def __init__(self, frm, to,
                 add_node=lambda x: None,
                 connect_node=lambda x, y: None,
                 highlight_nodes=lambda x, y, z=(False, True): None,
                 orient=Y):
        self.frm = frm
        self.to = to
        self.orient = orient
        self.lower = None
        self.higher = None
        self.point = None
        self.add_node = add_node
        self.connect_node = connect_node
        self.highlight_nodes = highlight_nodes

        self.add_node(self)

    def __eq__(self, other):
        return self.frm == other.frm and self.to == other.to

    def __hash__(self):
        return hash(self.frm) + 31 * hash(self.to)

    def label(self):
        return "%d, %d" % (self.point[0], self.point[1]) if self.point is not None else ''

    def insert(self, point):
        if self.orient == Y:
            if self.point is None:
                self.point = point
                self.lower = KDTree(self.frm, (point[0], self.to[1]), self.add_node, self.connect_node, self.highlight_nodes, X)
                self.higher = KDTree((point[0], self.frm[1]), self.to, self.add_node, self.connect_node, self.highlight_nodes,X)

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
                self.lower = KDTree(self.frm, (self.to[0], point[1]), self.add_node, self.connect_node, self.highlight_nodes,Y)
                self.higher = KDTree((self.frm[0], point[1]), self.to, self.add_node, self.connect_node, self.highlight_nodes,Y)

                self.connect_node(self, self.lower)
                self.connect_node(self, self.higher)
            else:
                if point[1] <= self.point[1]:
                    self.lower.insert(point)
                else:
                    self.higher.insert(point)

    def all_nodes(self):
        if self.point is None:
            return []
        else:
            return self.lower.all_nodes() + [self] + self.higher.all_nodes()

    def find(self, frm, to):
        if self.point is None:
            return []

        self.highlight_nodes([self], '#B3B3B3')

        if self.to[0] < frm[0] or self.to[1] < frm[1] or self.frm[0] > to[0] or self.frm[1] > to[1]:
            self.highlight_nodes(self.all_nodes(), '#444444')
            return []
        if self.frm[0] >= frm[0] and self.frm[1] >= frm[1] and self.to[0] <= to[0] and self.to[1] <= to[1]:
            self.highlight_nodes(self.all_nodes(), '#B4FFB4', (True, True))
            return self.all_nodes()

        point_in_range = frm[0] <= self.point[0] <= to[0] and frm[1] <= self.point[1] <= to[1]

        if point_in_range:
            self.highlight_nodes([self], '#B4FFB4', (True, False))
        else:
            self.highlight_nodes([self], '#FFFFFF')

        return self.lower.find(frm, to) + ([self.point] if point_in_range else []) + self.higher.find(frm, to)


