# Sentinel values for the beginning and end of linked lists
INF = float('inf')


class Node(object):
    """Node wraps element values and pointers to other nodes.

    Most skiplists only have right and down pointers. For helper
    functions like `is_plateau` implementation is more obviously
    correct if we maintain up pointers too.

    Similarly, skiplist nodes don't usually need to know what level
    they are on. Keeping a level reference for debugging purposes
    is nice though.
    """
    def __init__(self, elem):
        assert type(elem) is int or elem in (INF, -INF)
        self.elem = elem
        self.level = None
        self.right = None
        self.up = None
        self.down = None

    def __str__(self):
        return str(self.elem)

    def __eq__(self, other):
        return self.elem == other.elem

    def __lt__(self, other):
        return self.elem < other.elem

    def __gt__(self, other):
        return self.elem > other.elem

    def __le__(self, other):
        return self.elem <= other.elem

    def __ge__(self, other):
        return self.elem >= other.elem

    def _debug(self, label_func=None):
        if label_func:
            return "Node{level: %s, elem:%s, label:%s}" % (self.level, self.elem, label_func(self))
        return "Node{level: %s, elem:%s}" % (self.level, self.elem)

    @property
    def is_plateau(self):
        """A boolean indicating whether the node is a "plateau" node.

        The definition of a plateau node can be found in Section 2.1
        of Goodrich's paper.
        """
        return self.up is None

    @property
    def is_tower(self):
        """A boolean indicating whether the node is a "tower" node.

        The definition of a tower node can be found in Section 2.1
        of Goodrich's paper.
        """
        return not self.is_plateau


class NegInf(Node):
    """Node with element value -Infinity.
    """
    def __init__(self):
        super(NegInf, self).__init__(-INF)


class Inf(Node):
    """Node with element value Infinity.
    """
    def __init__(self):
        super(Inf, self).__init__(INF)


class SkipList(object):

    def __init__(self, level_arrays):
        nodes = {}
        self.height = len(level_arrays)
        self.max_level = self.height-1
        for level, level_array in enumerate(reversed(level_arrays)):
            last_node = None
            # iterate over each element and create nodes
            for elem in level_array:
                node = Node(elem)
                node.level = level
                # the last node to be created needs to point to the current
                # node
                if last_node:
                    last_node.right = node
                # if there is a node with value elem a level below us, we
                # should add up/down pointers
                down_node = nodes.get((level-1, elem), None)
                if down_node:
                    node.down = down_node
                    down_node.up = node
                last_node = node
                nodes[(level, elem)] = node
        # set the starting node as the top-left-most node
        self.start = nodes[(self.max_level, -INF)]

    def _debug(self, label_func=None):
        s = "SkipList{\n"
        for i in reversed(range(self.height)):
            s += "  %d: " % i
            s += " ".join(n._debug(label_func) for n in self._level(i))
            s += "\n"
        s += "}"
        return s

    def _level(self, level_index):
        """Return the nodes at the specific level_index as a Python list
        """
        if level_index < 0 or level_index > self.max_level:
            raise IndexError('level_index %d out of bounds' % level_index)
        curr = self.start
        nodes = []
        for _ in range(self.height - level_index - 1):
            curr = curr.down
        while curr is not None:
            nodes.append(curr)
            curr = curr.right
        return nodes

    def search(self, elem):
        """Searchs for a node in the skip list with element `elem`.

        Returns the stack of nodes that were traversed during the search as
        a list.

        The Goodrich paper suggests that the last item on the stack
        is "either [elem]... or the largest element less than [elem]"
        and it is expected the last item on the search stack is on the
        base level (See e.g. Figure 4) so this isn't the most intuitive
        search.
        """
        curr = self.start
        search_stack = []
        node = Node(elem)
        while curr is not None:
            search_stack.append(curr)
            right = curr.right
            if right is None:
                curr = curr.down
                continue
            if node < right:
                curr = curr.down
                continue
            if node > right:
                curr = right
                continue
            if node == right:
                # We found the top-most node with the correct value!
                # Goodrich's implementation of a skip list requires
                # we continue moving down and return the base node, though.
                curr = right
                while curr.down is not None:
                    search_stack.append(curr)
                    curr = curr.down
                # We exited the loop before we captured the bottom-most element
                search_stack.append(curr)
                return search_stack
        return search_stack

    def get(self, elem):
        """Get the base Node with value `elem`, or None if no such Node exists.
        """
        search_stack = self.search(elem)
        last_node = search_stack.pop()
        if last_node.elem == elem:
            return last_node
        return None
