import networkx as nx
import pyforms
from networkx.drawing.nx_agraph import graphviz_layout
from pyforms import BaseWidget
from pyforms.Controls import *

from kdtree import *
from quadtree import QuadTree

X_SIZE, Y_SIZE = 100, 100


class GUI(BaseWidget):
    def __init__(self):
        super(GUI, self).__init__('Simple example 1')

        self._q_structure = ControlMatplotlib('Quad tree structure')
        self._q_plain = ControlMatplotlib('Quad tree plain')
        self._kd_structure = ControlMatplotlib('KD tree structure')
        self._kd_plain = ControlMatplotlib('KD tree plain')
        self._x_coord = ControlNumber('X')
        self._y_coord = ControlNumber('Y')
        self._button = ControlButton('Add point')
        self._button.value = self._add_button_action
        self._formset = [
            '_x_coord', '||', '_y_coord', '||', '_button', '=',
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

        self._qt = QuadTree((0, 0), (X_SIZE, Y_SIZE), lambda x: self.add_q_node(x),
                            lambda x, y: self.connect_q_node(x, y))
        self._kdt = KDTree((0, 0), (X_SIZE, Y_SIZE), lambda x: self.add_kd_node(x),
                           lambda x, y: self.connect_kd_node(x, y))

        self._refresh_graphs()

    def _add_point_action(self, event):
        if event.xdata is not None and event.ydata is not None:
            self._qt.insert((event.xdata, event.ydata))
            self._kdt.insert((event.xdata, event.ydata))
            self._refresh_graphs()

    def _add_button_action(self):
        x = float(self._x_coord.value)
        y = float(self._y_coord.value)
        self._qt.insert((x, y))
        self._kdt.insert((x, y))
        self._refresh_graphs()

    def add_q_node(self, node):
        self._q_graph.add_node(node)

    def connect_q_node(self, parent, node):
        self._q_graph.add_edge(parent, node)

    def add_kd_node(self, node):
        self._kd_graph.add_node(node)

    def connect_kd_node(self, parent, node):
        self._kd_graph.add_edge(parent, node)

    def _refresh_kd_structure(self):
        self._kd_graph_fig.clear()
        kd_graph_ax = self._kd_graph_fig.add_subplot(111)
        kd_graph_ax.get_xaxis().set_visible(False)
        kd_graph_ax.get_yaxis().set_visible(False)
        kd_graph_labels = {x: x.label() for x in self._kd_graph}
        kd_graph_pos = graphviz_layout(self._kd_graph, prog='dot')
        nx.draw_networkx(self._kd_graph, kd_graph_pos, ax=kd_graph_ax, labels=kd_graph_labels, with_labels=True,
                         arrows=False, node_size=1500, node_color='#FFFFFF', font_size=10)
        self._kd_graph_fig.canvas.draw()

    def _refresh_q_structure(self):
        self._q_graph_fig.clear()
        q_graph_ax = self._q_graph_fig.add_subplot(111)
        q_graph_ax.get_xaxis().set_visible(False)
        q_graph_ax.get_yaxis().set_visible(False)
        q_graph_labels = {x: x.label() for x in self._q_graph}
        q_graph_pos = graphviz_layout(self._q_graph, prog='dot')
        nx.draw_networkx(self._q_graph, q_graph_pos, ax=q_graph_ax, labels=q_graph_labels, with_labels=True, arrows=False,
                         node_size=1500, node_color='#FFFFFF', font_size=10)
        self._q_graph_fig.canvas.draw()

    def _refresh_kd_plain(self):
        self._kd_plain_fig.clear()
        kd_plain_ax = self._kd_plain_fig.add_subplot(111)
        kd_plain_ax.set_xlim(0, X_SIZE)
        kd_plain_ax.set_ylim(0, Y_SIZE)

        for n in self._kd_graph.__iter__():
            if n.point is not None:
                if n.orient == X:
                    kd_plain_ax.plot((n.frm[0], n.to[0]), (n.point[1], n.point[1]), 'r-')
                else:
                    kd_plain_ax.plot((n.point[0], n.point[0]), (n.frm[1], n.to[1]), 'b-')

        for n in self._kd_graph.__iter__():
            if n.point is not None:
                if n.orient == X:
                    kd_plain_ax.plot([n.point[0]], [n.point[1]], 'or')
                else:
                    kd_plain_ax.plot([n.point[0]], [n.point[1]], 'ob')

        self._kd_plain_fig.canvas.draw()

    def _refresh_q_plain(self):
        self._q_plain_fig.clear()
        q_plain_ax = self._q_plain_fig.add_subplot(111)
        q_plain_ax.set_xlim(0, X_SIZE)
        q_plain_ax.set_ylim(0, Y_SIZE)

        #TODO

        self._q_plain_fig.canvas.draw()

    def _refresh_graphs(self):
        self._refresh_kd_structure()
        self._refresh_q_structure()
        self._refresh_kd_plain()
        self._refresh_q_plain()


g = GUI
pyforms.startApp(g)
