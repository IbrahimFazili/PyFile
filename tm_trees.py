"""
"""
from __future__ import annotations
import os
import math
from random import randint
from typing import List, Tuple, Optional


class TMTree:
    """A TreeMappableTree: a tree that is compatible with the treemap
    visualiser.

    === Public Attributes ===
    rect:
        The pygame rectangle representing this node in the treemap
        visualization.
    data_size:
        The size of the data represented by this tree.

    === Private Attributes ===
    _colour:
        The RGB colour value of the root of this tree.
    _name:
        The root value of this tree, or None if this tree is empty.
    _subtrees:
        The subtrees of this tree.
    _parent_tree:
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.
    _expanded:
        Whether or not this tree is considered expanded for visualization.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.

    - _colour's elements are each in the range 0-255.

    - If _name is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.

    - if _parent_tree is not None, then self is in _parent_tree._subtrees

    - if _expanded is True, then _parent_tree._expanded is True
    - if _expanded is False, then _expanded is False for every tree
      in _subtrees
    - if _subtrees is empty, then _expanded is False
    """

    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: str
    _subtrees: List[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool

    def __init__(self, name: str, subtrees: List[TMTree],
                 data_size: int = 0) -> None:
        """Initialize a new TMTree with a random colour and the provided <name>.

        Precondition: if <name> is None, then <subtrees> is empty.
        """
        self.rect = (0, 0, 0, 0)
        self._name = name
        self._subtrees = subtrees[:]
        self._parent_tree = None
        self._expanded = False
        self._colour = (randint(0, 255), randint(0, 255), randint(0, 255))
        if not self._subtrees:
            self.data_size = data_size
        elif self._subtrees:
            self.data_size = self._sub_trees_size(subtrees)
            for sub in self._subtrees:
                sub._parent_tree = self
                sub._expanded = False

    def _sub_trees_size(self, subtrees: List[TMTree]) -> float:
        """
        Finds and returns sizes of subtrees
        """
        return_size = 0
        for sub in subtrees:
            return_size += sub.data_size
        return return_size

    def is_empty(self) -> bool:
        """Return True iff this tree is empty.
        """
        return self._name is None

    def update_rectangles(self, rect: Tuple[int, int, int, int]) -> None:

        """
        Update the rectangles in this tree and its descendents using the
        treemap algorithm to fill the area defined by pygame rectangle <rect>.
        """

        x, y, width, height = rect
        size = 0
        self.rect = rect
        for subs in self._subtrees:
            size += subs.data_size
        if height >= width:
            new_length = y
            for index in range(len(self._subtrees)):
                if index != len(self._subtrees) - 1:
                    if self.data_size == 0:
                        new_height = 0
                    else:
                        new_height = math.floor(
                            (self._subtrees[index].data_size / size) * height)
                else:
                    new_height = y + height - new_length
                self._subtrees[index].update_rectangles(
                    (x, new_length, width, new_height))
                new_length += new_height
        else:
            new_x = x
            for index in range(len(self._subtrees)):
                if index != len(self._subtrees) - 1:
                    if self.data_size == 0:
                        new_width = 0
                    else:
                        new_width = math.floor(
                            (self._subtrees[index].data_size / size) * width)
                else:
                    new_width = x + width - new_x
                self._subtrees[index].update_rectangles(
                    (new_x, y, new_width, height))
                new_x += new_width

    def get_rectangles(self) -> List[Tuple[Tuple[int, int, int, int],
                                           Tuple[int, int, int]]]:
        """Return a list with tuples for every leaf in the displayed-tree
        rooted at this tree. Each tuple consists of a tuple that defines the
        appropriate pygame rectangle to display for a leaf, and the colour
        to fill it with.
        """
        new_list = []
        if self._subtrees:
            if not self._expanded:
                return [(self.rect, self._colour)]
            else:
                for sub in self._subtrees:
                    new_list.extend(sub.get_rectangles())
                return new_list
        else:
            return [(self.rect, self._colour)]

    def get_tree_at_position(self, pos: Tuple[int, int]) -> Optional[TMTree]:

        """Return the leaf in the displayed-tree rooted at this tree whose
        rectangle contains position <pos>, or None if <pos> is outside of this
        tree's rectangle.

        If <pos> is on the shared edge between two rectangles, return the
        tree represented by the rectangle that is closer to the origin.
        """
        x, y, z, w = self.rect
        if x + z >= pos[0] and pos[1] <= w + y:
            if self._subtrees:
                if self._expanded:
                    for subtree in self._subtrees:
                        obj = subtree.get_tree_at_position(pos)
                        if obj is not None:
                            return obj
                elif not self._expanded:
                    if x + z >= pos[0] and pos[1] <= y + w and \
                            self._parent_tree is None:
                        return self
                    elif x + z >= pos[0] and pos[1] <= y + w and \
                            self._parent_tree is not None and \
                            self._parent_tree._expanded:
                        return self
            else:
                if x + z >= pos[0] and pos[1] <= y + w and \
                        self._parent_tree is not None and \
                        self._parent_tree._expanded:
                    return self
                return None
        else:
            return None

    def update_data_sizes(self) -> int:
        """Update the data_size for this tree and its subtrees, based on the
        size of their leaves, and return the new size.

        If this tree is a leaf, return its size unchanged.
        """
        data_size = 0
        for subtree in self._subtrees:
            if subtree._subtrees:
                data_size += subtree.update_data_sizes()
            else:
                data_size += subtree.data_size
        self.data_size = data_size
        return data_size

    def move(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, move this
        tree to be the last subtree of <destination>. Otherwise, do nothing.
        """
        if not self._subtrees and destination._subtrees != []:
            parent = self._parent_tree
            self._parent_tree._subtrees.remove(self)
            if not parent._subtrees:
                parent._parent_tree._subtrees.remove(parent)
            self._parent_tree = destination
            destination._subtrees.append(self)

    def change_size(self, factor: float) -> None:
        """Change the value of this tree's data_size attribute by <factor>.

        Always round up the amount to change, so that it's an int, and
        some change is made.

        Do nothing if this tree is not a leaf.
        """
        if not self._subtrees:
            if factor == 0.01:  # this means we increase
                size_increase = math.ceil(self.data_size * 0.01)
                self.data_size += size_increase
            if factor == -0.01:
                size_decrease = math.ceil(self.data_size * 0.01)
                holder = self.data_size - size_decrease
                if holder >= 1:
                    self.data_size -= size_decrease
        else:
            pass

    def expand(self) -> None:
        """"
        shows the leaves of a folder
        """
        self._expanded = True

    def expand_all(self) -> None:
        """
        expands the rectangle to show all leaves
        """
        if self._subtrees:
            self._expanded = True
            for subtree in self._subtrees:
                subtree._expanded = True
                subtree.expand_all()
        else:
            self._expanded = True

    def collapse(self) -> None:
        """
        closes leaf into folder
        """
        self._expanded = False
        if self._parent_tree is None:
            return None
        if self._parent_tree._expanded:
            self._parent_tree._expanded = False
        for subtree in self._subtrees:
            subtree.collapse()
        for subtree in self._parent_tree._subtrees:
            if subtree._expanded:
                subtree.collapse()

    def collapse_all(self) -> None:
        """
        closes all the leaves and give main rectangle
        """
        self.collapse()
        if self._parent_tree is not None:
            self._parent_tree.collapse_all()

    # Methods for the string representation
    def get_path_string(self, final_node: bool = True) -> str:
        """Return a string representing the path containing this tree
        and its ancestors, using the separator for this tree between each
        tree's name. If <final_node>, then add the suffix for the tree.
        """
        if self._parent_tree is None:
            path_str = self._name
            if final_node:
                path_str += self.get_suffix()
            return path_str
        else:
            path_str = (self._parent_tree.get_path_string(False) +
                        self.get_separator() + self._name)
            if final_node or len(self._subtrees) == 0:
                path_str += self.get_suffix()
            return path_str

    def get_separator(self) -> str:
        """Return the string used to separate names in the string
        representation of a path from the tree root to this tree.
        """
        raise NotImplementedError

    def get_suffix(self) -> str:
        """Return the string used at the end of the string representation of
        a path from the tree root to this tree.
        """
        raise NotImplementedError


class FileSystemTree(TMTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _name attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/Diane/csc148/assignments'

    The data_size attribute for regular files is simply the size of the file,
    as reported by os.path.getsize.
    """

    def __init__(self, path: str) -> None:
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer
        """
        if os.path.isdir(path):
            leaves = os.listdir(path)
            a_new_subtree = []
            for leaf in leaves:
                subtree = FileSystemTree(os.path.join(path, leaf))
                a_new_subtree.append(subtree)
            name = os.path.basename(path)
            TMTree.__init__(self, name, a_new_subtree, 1)
        else:
            basename = os.path.basename(path)
            TMTree.__init__(self, basename, [], os.path.getsize(path))

    def get_separator(self) -> str:
        """Return the file separator for this OS.
        """
        return os.sep

    def get_suffix(self) -> str:
        """Return the final descriptor of this tree.
        """
        if len(self._subtrees) == 0:
            return ' (file)'
        else:
            return ' (folder)'


# if __name__ == '__main__':
#     import python_ta
#     python_ta.check_all(config={
#         'allowed-import-modules': [
#             'python_ta', 'typing', 'math', 'random', 'os', '__future__'
#         ]
#     })
