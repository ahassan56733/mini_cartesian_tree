# mini_cartesian_tree

Builds a min-heap Cartesian tree from an array of comparable values. The root holds the smallest element; an in-order walk of the tree reproduces the original array order. Each node carries its source index so equal-valued elements stay distinguishable.

```python
from mini_cartesian_tree import CartesianTree

t = CartesianTree([5, 3, 1, 4, 2])
print(t.root.value)          # 1
print(t.root.index)          # 2
print([n.value for n in t.in_order()])  # [5, 3, 1, 4, 2]

# Reverse polarity by negating a key:
tmax = CartesianTree([5, 3, 1, 4, 2], key=lambda x: -x)
print(tmax.root.value)       # 5
```

Exported names: `CartesianTree` (the tree) and `Node` (a node with `index`, `value`, `left`, `right`).

## Why

Cartesian trees turn a static array into a heap-ordered binary tree in O(n) time while preserving index order in an in-order walk. They are the backbone of RMQ-by-tree and suffix-array construction. This library exists to provide that one data structure, with no third-party dependencies and no extras dragged in.

Two choices are fixed so the output is deterministic:

- **Duplicates** favour the earlier index. When a value equals the value already on the right spine, the existing node stays above the new one. The first occurrence sits closer to the root along its spine.
- **Heap polarity** is min only. For a max-heap, pass `key=lambda x: -x` (for numbers) or any reverse-comparison key of your choosing.

## Edge cases

- Empty input yields `root is None`; `in_order()` and `pre_order()` produce nothing.
- A single element yields a root with no children.
- Sorted ascending input produces a left-leaning chain; sorted descending produces a right-leaning chain. The traversals are iterative, so deep chains do not hit Python's recursion limit.
- Values must be mutually comparable with each other; the library does not catch `TypeError` for you.
