import networkx as nx
import pyforms
from networkx.drawing.nx_agraph import graphviz_layout
from pyforms import BaseWidget
from pyforms.Controls import *
import matplotlib.patches as patches

from kdtree import *
from quadtree import QuadTree, QuadStep

X_SIZE, Y_SIZE = 100, 100
NO_FIND, FIND1, FIND2, DISPLAYING = 0, 1, 2, 3


class _KDFindStep:
    def __init__(self, nodes, color, visual_info=(False, True)):
        self.nodes = nodes
        self.color = color
        self.visual_info = visual_info


class GUI(BaseWidget):
    def __init__(self):
        super(GUI, self).__init__('Simple example 1')

        self.find_stage = False
        self.find_points = []
        self.find_frm = None
        self.find_to = None
        self.kd_find_steps = []
        self.kd_find_result = None
        self.find_step_no = 0
        self.q_find_steps = []
        self.q_find_result = []
        self._q_found_points = []

        self._q_structure = ControlMatplotlib('Quad tree structure')
        self._q_plain = ControlMatplotlib('Quad tree plain')
        self._kd_structure = ControlMatplotlib('KD tree structure')
        self._kd_plain = ControlMatplotlib('KD tree plain')
        self._find_button = ControlButton('Find')
        self._step_button = ControlButton('Step')
        self._clear_button = ControlButton('Clear')
        self._find_button.value = self._on_find
        self._step_button.value = self._on_step
        self._clear_button.value = self._clear_all
        self._formset = [
            '_find_button', '||', '_step_button', '||', "_clear_button", '=',
            {
                'Quad tree': ['_q_structure', '||', '_q_plain'],
                'KD tree': ['_kd_structure', '||', '_kd_plain']
            }]

        self._q_graph = nx.DiGraph()
        self._kd_graph = nx.DiGraph()

        self._q_graph_fig = self._q_structure.fig
        self._q_plain_fig = self._q_plain.fig
        self._kd_graph_fig = self._kd_structure.fig
        self._kd_plain_fig = self._kd_plain.fig

        self._kd_plain_fig.canvas.mpl_connect('button_press_event', lambda x: self._add_point_action(x))
        self._q_plain_fig.canvas.mpl_connect('button_press_event', lambda x: self._add_point_action(x))

        self._qt = QuadTree((0, 0), (X_SIZE, Y_SIZE),
                            lambda x: self.add_q_node(x),
                            lambda x, y: self.connect_q_node(x, y))
        self._kdt = KDTree((0, 0), (X_SIZE, Y_SIZE),
                           lambda x: self.add_kd_node(x),
                           lambda x, y: self.connect_kd_node(x, y),
                           lambda x, y, z=(False, True): self.highlight_kd_nodes(x, y, z))

        self._refresh_graphs()

    def _add_point_action(self, event):
        if event.xdata is not None and event.ydata is not None:
            if self.find_stage == NO_FIND:
                self._qt.insert((event.xdata, event.ydata))
                self._kdt.insert((event.xdata, event.ydata))
                self._refresh_graphs()
            elif self.find_stage == FIND1:
                self.find_points.append((event.xdata, event.ydata))
                self._refresh_graphs()
                self.find_stage = FIND2
            elif self.find_stage == FIND2:
                self.find_points.append((event.xdata, event.ydata))
                self.find_frm = (min(map(lambda x: x[0], self.find_points)), min(map(lambda x: x[1], self.find_points)))
                self.find_to = (max(map(lambda x: x[0], self.find_points)), max(map(lambda x: x[1], self.find_points)))
                self._refresh_graphs()
                self.find_points = []
                self.kd_find_result = self._kdt.find(self.find_frm, self.find_to)
                (self.q_find_result, self.q_find_steps) = self._qt.find(self.find_frm, self.find_to)
                self._q_found_points = []
                self.find_stage = DISPLAYING

    def _on_find(self):
        if self.find_stage == NO_FIND:
            self.find_stage = FIND1

    def _on_step(self):
        if self.find_stage == DISPLAYING:
            if self.find_step_no >= len(self.kd_find_steps) and self.find_step_no >= len(self.q_find_steps):
                self.find_points = []
                self.find_frm = None
                self.find_to = None
                self.kd_find_result = None
                self.kd_find_steps = []
                self.find_step_no = 0
                self.find_stage = NO_FIND
                self.q_find_steps = []
                self.q_find_result = []
                self._q_found_points = []
                self._refresh_graphs()
            else:
                self.find_step_no += 1
                self._refresh_graphs()

    def _clear_all(self):
        self.find_points = []
        self.find_frm = None
        self.find_to = None
        self.kd_find_result = None
        self.kd_find_steps = []
        self.find_step_no = 0
        self.find_stage = NO_FIND
        self.q_find_steps = []
        self.q_find_result = []
        self._q_found_points = []

        self._q_graph = nx.DiGraph()
        self._kd_graph = nx.DiGraph()

        self._qt = QuadTree((0, 0), (X_SIZE, Y_SIZE),
                            lambda x: self.add_q_node(x),
                            lambda x, y: self.connect_q_node(x, y))
        self._kdt = KDTree((0, 0), (X_SIZE, Y_SIZE),
                           lambda x: self.add_kd_node(x),
                           lambda x, y: self.connect_kd_node(x, y),
                           lambda x, y, z=(False, True): self.highlight_kd_nodes(x, y, z))

        self._refresh_graphs()

    def add_q_node(self, node):
        self._q_graph.add_node(node)

    def connect_q_node(self, parent, node):
        self._q_graph.add_edge(parent, node)

    def add_kd_node(self, node):
        self._kd_graph.add_node(node)

    def connect_kd_node(self, parent, node):
        self._kd_graph.add_edge(parent, node)

    def highlight_kd_nodes(self, nodes, color, visual_info=(False, True)):
        self.kd_find_steps.append(_KDFindStep(nodes, color, visual_info))

    def _refresh_kd_structure(self):
        self._kd_graph_fig.clear()
        kd_graph_ax = self._kd_graph_fig.add_subplot(111)
        kd_graph_ax.get_xaxis().set_visible(False)
        kd_graph_ax.get_yaxis().set_visible(False)
        kd_graph_labels = {x: x.label() for x in self._kd_graph}

        kd_graph_sizes = [(100 if x.point is None else 1500) for x in self._kd_graph]
        kd_graph_colors = []
        for node in self._kd_graph.__iter__():
            steps = [x for x in self.kd_find_steps[:self.find_step_no] if node in x.nodes]
            if len(steps) > 0:
                kd_graph_colors.append(steps[-1].color)
            else:
                kd_graph_colors.append('#FF8888' if node.orient == X else '#8888FF')

        kd_graph_pos = graphviz_layout(self._kd_graph, prog='dot')
        nx.draw_networkx(self._kd_graph, kd_graph_pos, ax=kd_graph_ax, labels=kd_graph_labels, with_labels=True,
                         node_color=kd_graph_colors, arrows=False, node_size=kd_graph_sizes, font_size=10)
        self._kd_graph_fig.canvas.draw()

    def _refresh_q_structure(self):
        self._q_graph_fig.clear()
        q_graph_ax = self._q_graph_fig.add_subplot(111)
        q_graph_ax.get_xaxis().set_visible(False)
        q_graph_ax.get_yaxis().set_visible(False)
        q_graph_labels = {x: x.label() for x in self._q_graph}
        q_graph_pos = graphviz_layout(self._q_graph, prog='dot')
        q_graph_nodelist = [x for x in self._q_graph]
        q_graph_sizes = [(50 if x.empty else 1000) for x in q_graph_nodelist]
        color_map = {}
        for step in self.q_find_steps[:self.find_step_no]:
            for node in step.node:
                color_map[node] = step.color

        if self.find_stage == DISPLAYING and self.q_find_steps and self.find_step_no <= len(self.q_find_steps) and len(self.q_find_steps[self.find_step_no - 1].node) > 0:
            color_map[self.q_find_steps[self.find_step_no - 1].node[0]] = "#B4B4B4"

        q_graph_colors = [color_map[x] if x in color_map else "#FFFFFF" for x in self._q_graph]

        nx.draw_networkx(self._q_graph, q_graph_pos, ax=q_graph_ax, labels=q_graph_labels, with_labels=True,
                         arrows=False,
                         nodelist=q_graph_nodelist, node_size=q_graph_sizes, node_color=q_graph_colors, font_size=8)
        self._q_graph_fig.canvas.draw()

    def _refresh_kd_plain(self):
        self._kd_plain_fig.clear()
        kd_plain_ax = self._kd_plain_fig.add_subplot(111)
        kd_plain_ax.set_xlim(0, X_SIZE)
        kd_plain_ax.set_ylim(0, Y_SIZE)

        for step in self.kd_find_steps[:self.find_step_no]:
            color = step.color
            nodes = step.nodes
            for node in nodes:
                if step.visual_info[1]:
                    kd_plain_ax.add_patch(
                        patches.Rectangle(node.frm, node.to[0] - node.frm[0], node.to[1] - node.frm[1],
                                          facecolor=color))
                else:
                    kd_plain_ax.add_patch(
                        patches.Rectangle(node.frm, node.to[0] - node.frm[0], node.to[1] - node.frm[1],
                                          facecolor='#FFFFFF'))

        for n in self._kd_graph.__iter__():
            if n.point is not None:
                if n.orient == X:
                    kd_plain_ax.plot((n.frm[0], n.to[0]), (n.point[1], n.point[1]), 'r-')
                else:
                    kd_plain_ax.plot((n.point[0], n.point[0]), (n.frm[1], n.to[1]), 'b-')

        steps_with_found = [x for x in self.kd_find_steps[:self.find_step_no] if x.visual_info[0]]
        found_nodes = reduce(lambda x, y: x + y, [x.nodes for x in steps_with_found], [])
        for n in self._kd_graph.__iter__():
            if n.point is not None:
                if n in found_nodes:
                    kd_plain_ax.plot([n.point[0]], [n.point[1]], 'sg')
                elif n.orient == X:
                    kd_plain_ax.plot([n.point[0]], [n.point[1]], 'or')
                else:
                    kd_plain_ax.plot([n.point[0]], [n.point[1]], 'ob')

        if self.find_stage == FIND2 or self.find_stage == DISPLAYING:
            kd_plain_ax.plot((self.find_frm[0], self.find_frm[0]), (self.find_frm[1], self.find_to[1]), 'k-')
            kd_plain_ax.plot((self.find_frm[0], self.find_to[0]), (self.find_to[1], self.find_to[1]), 'k-')
            kd_plain_ax.plot((self.find_to[0], self.find_to[0]), (self.find_to[1], self.find_frm[1]), 'k-')
            kd_plain_ax.plot((self.find_to[0], self.find_frm[0]), (self.find_frm[1], self.find_frm[1]), 'k-')
        elif self.find_stage == FIND1:
            kd_plain_ax.plot([self.find_points[0][0]], [self.find_points[0][1]], 'ok')

        self._kd_plain_fig.canvas.draw()

    def draw_quad(self, q_plain_ax, node, c=None):
        step = self.q_find_steps[self.find_step_no - 1] \
            if self.find_stage == DISPLAYING and self.q_find_steps and self.find_step_no <= len(self.q_find_steps) \
            else None
        if c is None:
            color = "#AAAAAA" if step and len(step.node) > 0 and step.node[0].frm == node.frm and step.node[0].to == node.to else "#FFFFFF"
        else:
            color = c
        q_plain_ax.add_patch(
            patches.Rectangle(node.frm, node.to[0] - node.frm[0], node.to[1] - node.frm[1], facecolor=color))
        if len(node.children.keys()) > 0:
            for child in node.children.keys():
                self.draw_quad(q_plain_ax, node.children[child], c)

    def quad_points(self, node):
        points = [node.point] if node.point is not None else []
        for child in node.children.keys():
            points.extend(self.quad_points(node.children[child]))
        return points

    def _refresh_q_plain(self):
        self._q_plain_fig.clear()
        q_plain_ax = self._q_plain_fig.add_subplot(111)
        q_plain_ax.set_xlim(0, X_SIZE)
        q_plain_ax.set_ylim(0, Y_SIZE)

        self.draw_quad(q_plain_ax, self._qt)

        for step in self.q_find_steps[:self.find_step_no]:
            if step.color == "#B4FEB4" or step.color == "#444444":
                self.draw_quad(q_plain_ax, step.node[0], step.color)

        found_points = []
        for step in self.q_find_steps[:self.find_step_no]:
            if step.color == "#B4FFB4" or step.color == "#B4FEB4":
                for node in step.node:
                    found_points.append(node.point)

        for point in self.quad_points(self._qt):
            color = 'og' if point in found_points else 'ob'
            q_plain_ax.plot([point[0]], [point[1]], color)

        if self.find_stage == FIND2 or self.find_stage == DISPLAYING:
            q_plain_ax.plot((self.find_frm[0], self.find_frm[0]), (self.find_frm[1], self.find_to[1]), 'r-')
            q_plain_ax.plot((self.find_frm[0], self.find_to[0]), (self.find_to[1], self.find_to[1]), 'r-')
            q_plain_ax.plot((self.find_to[0], self.find_to[0]), (self.find_to[1], self.find_frm[1]), 'r-')
            q_plain_ax.plot((self.find_to[0], self.find_frm[0]), (self.find_frm[1], self.find_frm[1]), 'r-')
        elif self.find_stage == FIND1:
            q_plain_ax.plot([self.find_points[0][0]], [self.find_points[0][1]], 'ok')

        self._q_plain_fig.canvas.draw()

    def _refresh_graphs(self):
        self._refresh_kd_structure()
        self._refresh_kd_plain()
        self._refresh_q_structure()
        self._refresh_q_plain()


g = GUI
pyforms.startApp(g)
