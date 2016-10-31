class QuadTree:
    def __init__(self, frm, to):
        self.frm = frm
        self.to = to
        self.children = {}
        self.empty = True
        # [self.insert(point) for point in points]

    def has_in_range(self, point):
        return  self.frm[0] <= point[0] and \
                self.frm[1] <= point[1] and \
                self.to[0] > point[0] and \
                self.to[1] > point[1]

    def insert_points(self, points):
        # print("Inserting %s points into [(%s, %s), (%s, %s)]\n" % (len(points), self.frm[0], self.frm[1], self.to[0], self.to[1]))
        [self.insert(point) for point in points]

    def insert(self, point):
        # print("Inserting (%s, %s) into [(%s, %s), (%s, %s)]\n" % (point[0], point[1], self.frm[0], self.frm[1], self.to[0], self.to[1]))
        if self.empty and len(self.children) == 0:
            self.point = point
            self.empty = False

        elif len(self.children) == 0:
            points = [point, self.point]
            del self.point
            self.empty = True
            middle = ((self.frm[0]+self.to[0])/2, (self.frm[1]+self.to[1])/2)
            self.children = {"SW": QuadTree(self.frm, middle),
                             "SE": QuadTree((middle[0], self.frm[1]), (self.to[0], middle[1])),
                             "NE": QuadTree(middle, self.to),
                             "NW": QuadTree((self.frm[0], middle[1]), (middle[0], self.to[1]))}
            for child in list(self.children.values()):
                child.insert_points([point for point in points if child.has_in_range(point)])

        else:
            [child.insert(point) for child in list(self.children.values()) if child.has_in_range(point)]


    def find(self, frm, to):
        if len(self.children) == 0:
            if not self.empty:
                if frm[0] <= self.point[0] and \
                        frm[1] <= self.point[1] and \
                        to[0] > self.point[0] and \
                        to[1] > self.point[1]:
                    return [self.point]
                else:
                    return []
            else:
                return []
        else:
            x_mid = (self.frm[0] + self.to[0]) / 2
            y_mid = (self.frm[1] + self.to[1]) / 2
            res = []

            if frm[0] <= x_mid:
                if frm[1] < y_mid:
                    res.extend(self.children["SW"].find(frm, (x_mid, y_mid)))
                if to[1] > y_mid:
                    res.extend(self.children["NW"].find((frm[0], y_mid), (x_mid, to[1])))
            if to[0] > x_mid:
                if frm[1] < y_mid:
                    res.extend(self.children["SE"].find((x_mid, frm[0]), (to[0], y_mid)))
                if to[1] > y_mid:
                    res.extend(self.children["NE"].find((x_mid, y_mid), to))

            return res


    def to_str(self, depth):
        padding = "\t" * depth
        message = "%sFrom: (%s, %s)\n" % (padding, self.frm[0], self.frm[1])
        message += "%sTo: (%s, %s)\n" % (padding, self.to[0], self.to[1])
        try:
            message += "%s\tPoint: (%s, %s)\n" % (padding, self.point[0], self.point[1])
        except AttributeError:
            pass
        if len(self.children) > 0:
            message += "%sChildren:\n" % padding
            for child in list(self.children.values()):
                message += child.to_str(depth+1)
        return message + "\n"

    def _print(self):
        print(self.to_str(0))
