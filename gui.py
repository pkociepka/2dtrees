import networkx as nx
import pyforms
from networkx.drawing.nx_agraph import graphviz_layout
from pyforms import BaseWidget
from pyforms.Controls import *

from quadtree import QuadTree


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

        self._graph = nx.DiGraph()
        self._fig = self._q_structure.fig
        self._qt = QuadTree((0, 0), (100, 100), lambda x: self.add_node(x), lambda x, y: self.connect_node(x, y))
        self.refresh_graph()

    def _add_button_action(self):
        x = float(self._x_coord.value)
        y = float(self._y_coord.value)
        self._qt.insert((x, y))
        self.refresh_graph()

    def add_node(self, node):
        self._graph.add_node(node)

    def connect_node(self, parent, node):
        self._graph.add_edge(parent, node)

    def refresh_graph(self):
        self._fig.clear()
        ax = self._fig.add_subplot(111)
        labels = {x: x.label() for x in self._graph}
        pos = graphviz_layout(self._graph, prog='dot')
        nx.draw_networkx(self._graph, pos, ax=ax, labels=labels, with_labels=True, arrows=False,
                         node_size=1500, node_color='#FFFFFF', font_size=10)
        self._fig.canvas.draw()


g = GUI
pyforms.startApp(g)
