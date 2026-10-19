"""Build a Cartesian tree from an array of comparable values.

A Cartesian tree is a heap-ordered binary tree whose in-order walk
reproduces the original array indices. This module implements the
standard O(n) stack-based construction with two tie-breaking choices
fixed up-front so that the result is fully deterministic:

1. Duplicates: ties favour the earlier index. When a new value equals
   the value at the top of the right-spine stack, we keep the existing
   node above the new one. This means the first occurrence of any value
   is closest to the root along its spine, which keeps the tree shallow
   for sorted input with repeats and matches the left-to-right reading
   most users expect.
2. Heap polarity: min-heap only. The root holds the minimum value.
   Max-heap behaviour is left to the caller, who can negate values or
   supply a reverse key function.

The construction never inspects the root value; it only pops and pushes
from the right spine, so it works for empty arrays and single-element
arrays as well.
"""

from __future__ import annotations

from typing import Callable, Iterator, List, Optional


class Node:
    """A node in a Cartesian tree.

    Children are mutable so that the builder can rewire pointers
    during construction without allocating new nodes. Once the tree
    is handed back to the caller, mutating it is the caller's choice
    and the tree does not defend against it.
    """

    __slots__ = ("index", "value", "left", "right")

    def __init__(
        self,
        index: int,
        value: object,
        left: Optional["Node"] = None,
        right: Optional["Node"] = None,
    ) -> None:
        self.index = index
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"Node(index={self.index}, value={self.value!r})"


class CartesianTree:
    """A min-heap Cartesian tree over an indexed sequence.

    Build with ``CartesianTree(values)`` where ``values`` is any
    sequence of mutually comparable objects. Pass ``key`` to compare
    a derived value instead (same semantics as ``sorted``).

    The tree stores the original *indices* (0-based) alongside values
    so that callers can map back to positions in the source array even
    when values are equal.
    """

    __slots__ = ("_root", "_n")

    def __init__(
        self,
        values: object,
        key: Optional[Callable[[object], object]] = None,
    ) -> None:
        self._root: Optional[Node] = CartesianTree._build(values, key)
        self._n = len(values) if hasattr(values, "__len__") else 0

    @staticmethod
    def _build(
        values: object,
        key: Optional[Callable[[object], object]],
    ) -> Optional[Node]:
        # Right spine of the tree so far, newest last. We only ever
        # need to look at this spine because each new node is appended
        # at the rightmost position and may cut off the lower part of
        # the spine that is no longer on the path from root to the new
        # rightmost leaf.
        spine: List[Node] = []

        i = 0
        for raw in values:
            v = key(raw) if key is not None else raw

            last = None
            # Walk up the spine as long as the spine node is strictly
            # greater than the new value. "Strictly" matters: equal
            # values keep the earlier node above the later one (tie
            # break #1 above). Compare using the same key function so
            # that key-derived comparisons stay consistent across the
            # whole spine.
            while spine and CartesianTree._key_of(spine[-1].value, key) > v:
                last = spine.pop()

            new = Node(i, raw, left=last)
            if spine:
                spine[-1].right = new
            spine.append(new)
            i += 1

        if not spine:
            return None
        return spine[0]

    @staticmethod
    def _key_of(
        value: object,
        key: Optional[Callable[[object], object]],
    ) -> object:
        return key(value) if key is not None else value

    @property
    def root(self) -> Optional[Node]:
        """The tree root, or ``None`` for an empty tree."""
        return self._root

    @property
    def size(self) -> int:
        """Number of nodes, or 0 for an empty tree."""
        return self._n

    def in_order(self) -> Iterator[Node]:
        """Yield nodes in array-index order.

        Implemented iteratively so very deep trees (e.g. sorted input)
        do not overflow the interpreter stack.
        """
        stack: List[Node] = []
        node = self._root
        while stack or node is not None:
            while node is not None:
                stack.append(node)
                node = node.left
            node = stack.pop()
            yield node
            node = node.right

    def pre_order(self) -> Iterator[Node]:
        """Yield nodes root-first. Useful for serialising the tree."""
        if self._root is None:
            return
        stack: List[Node] = [self._root]
        while stack:
            node = stack.pop()
            yield node
            # Push right first so left is processed first (LIFO).
            if node.right is not None:
                stack.append(node.right)
            if node.left is not None:
                stack.append(node.left)

    def __len__(self) -> int:
        return self._n
