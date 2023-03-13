import unittest

from graphviz import Digraph


class GraphVizTest(unittest.TestCase):
    def test1(self):
        dot = Digraph(comment='Test', node_attr={'shape': 'box'})

        dot.node('I0', '\n'.join(['I0', 'item0', 'item1']))
        dot.node('I1', '\n'.join(['item2', 'item3']))

        dot.edge('I0', 'I1', 'G', constraint='false')
        dot.render('test.gv', view=True)
