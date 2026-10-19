import unittest

from mini_cartesian_tree import CartesianTree, Node


class TestConstruction(unittest.TestCase):
    def test_empty_array_yields_no_root(self):
        t = CartesianTree([])
        self.assertIsNone(t.root)
        self.assertEqual(t.size, 0)
        self.assertEqual(len(t), 0)
        self.assertEqual(list(t.in_order()), [])

    def test_single_element(self):
        t = CartesianTree([42])
        self.assertIsNotNone(t.root)
        self.assertEqual(t.root.index, 0)
        self.assertEqual(t.root.value, 42)
        self.assertIsNone(t.root.left)
        self.assertIsNone(t.root.right)
        self.assertEqual(list(t.in_order()), [t.root])

    def test_root_is_minimum(self):
        t = CartesianTree([5, 3, 1, 4, 2])
        self.assertEqual(t.root.value, 1)
        self.assertEqual(t.root.index, 2)

    def test_in_order_recovers_indices(self):
        values = [9, 3, 7, 1, 8, 2, 6]
        t = CartesianTree(values)
        self.assertEqual([n.index for n in t.in_order()], list(range(len(values))))
        self.assertEqual([n.value for n in t.in_order()], values)

    def test_sorted_ascending_makes_left_chain(self):
        # min-heap: each new element is smaller, so it becomes the
        # new root and the old root hangs as its left child.
        t = CartesianTree([5, 4, 3, 2, 1])
        node = t.root
        self.assertEqual(node.value, 1)
        self.assertEqual(node.index, 4)
        self.assertIsNone(node.right)
        node = node.left
        self.assertEqual(node.value, 2)
        self.assertEqual(node.index, 3)
        self.assertIsNone(node.right)
        node = node.left
        self.assertEqual(node.value, 3)
        self.assertEqual(node.index, 2)
        self.assertIsNone(node.right)
        node = node.left
        self.assertEqual(node.value, 4)
        self.assertEqual(node.index, 1)
        self.assertIsNone(node.right)
        node = node.left
        self.assertEqual(node.value, 5)
        self.assertEqual(node.index, 0)
        self.assertIsNone(node.left)
        self.assertIsNone(node.right)

    def test_sorted_descending_makes_right_chain(self):
        # Each new element is larger, so it becomes the right child
        # of the previous rightmost node; the root stays fixed.
        t = CartesianTree([1, 2, 3, 4, 5])
        self.assertEqual(t.root.value, 1)
        self.assertEqual(t.root.index, 0)
        self.assertIsNone(t.root.left)
        node = t.root.right
        self.assertEqual(node.value, 2)
        self.assertEqual(node.index, 1)
        node = node.right
        self.assertEqual(node.value, 3)
        self.assertEqual(node.index, 2)
        node = node.right
        self.assertEqual(node.value, 4)
        self.assertEqual(node.index, 3)
        node = node.right
        self.assertEqual(node.value, 5)
        self.assertEqual(node.index, 4)
        self.assertIsNone(node.right)

    def test_non_monotone_input_shape(self):
        # Classic textbook example: [3, 1, 2].
        # Root is 1 (index 1). Left subtree: 3 (index 0).
        # Right subtree: 2 (index 2).
        t = CartesianTree([3, 1, 2])
        self.assertEqual(t.root.value, 1)
        self.assertEqual(t.root.index, 1)
        self.assertEqual(t.root.left.value, 3)
        self.assertEqual(t.root.left.index, 0)
        self.assertEqual(t.root.right.value, 2)
        self.assertEqual(t.root.right.index, 2)

    def test_duplicate_values_favour_earlier_index(self):
        # With duplicates equal to a spine node, the existing node
        # stays above (spine is not popped). This pins the first
        # occurrence closer to the root along its spine.
        t = CartesianTree([2, 1, 1, 1])
        self.assertEqual(t.root.value, 1)
        self.assertEqual(t.root.index, 1)
        # Index 0 (value 2) was popped when value 1 arrived and
        # became the left subtree of the root.
        self.assertEqual(t.root.left.value, 2)
        self.assertEqual(t.root.left.index, 0)
        # The new equal nodes go to the right of the previous equal.
        self.assertEqual(t.root.right.value, 1)
        self.assertEqual(t.root.right.index, 2)
        self.assertEqual(t.root.right.right.value, 1)
        self.assertEqual(t.root.right.right.index, 3)

    def test_duplicate_with_smaller_after(self):
        t = CartesianTree([2, 2, 1])
        # Root is 1 at index 2. Its left subtree is the [2,2] chain
        # built first; equal values keep earlier above later, so index 0
        # is the parent of index 1.
        self.assertEqual(t.root.value, 1)
        self.assertEqual(t.root.index, 2)
        self.assertIsNone(t.root.right)
        left = t.root.left
        self.assertEqual(left.value, 2)
        self.assertEqual(left.index, 0)
        self.assertEqual(left.right.value, 2)
        self.assertEqual(left.right.index, 1)


class TestKeyFunction(unittest.TestCase):
    def test_key_derives_comparison_value(self):
        # Use negative so min becomes max in effect.
        t = CartesianTree([1, 5, 3], key=lambda x: -x)
        self.assertEqual(t.root.value, 5)
        self.assertEqual(t.root.index, 1)

    def test_key_preserves_in_order(self):
        values = [10, 20, 30]
        t = CartesianTree(values, key=lambda x: -x)
        self.assertEqual([n.value for n in t.in_order()], values)

    def test_key_with_strings(self):
        # Compare by string length; ties keep earlier index.
        t = CartesianTree(["aaa", "b", "cc"], key=len)
        self.assertEqual(t.root.value, "b")
        self.assertEqual(t.root.index, 1)


class TestTraversals(unittest.TestCase):
    def test_pre_order_on_example(self):
        t = CartesianTree([3, 1, 2])
        pre = list(t.pre_order())
        # Root first, then left, then right.
        self.assertEqual([n.index for n in pre], [1, 0, 2])

    def test_pre_order_empty(self):
        t = CartesianTree([])
        self.assertEqual(list(t.pre_order()), [])

    def test_in_order_empty(self):
        t = CartesianTree([])
        self.assertEqual(list(t.in_order()), [])


class TestNode(unittest.TestCase):
    def test_node_repr(self):
        n = Node(3, "x")
        self.assertEqual(repr(n), "Node(index=3, value='x')")

    def test_node_default_children_none(self):
        n = Node(0, 0)
        self.assertIsNone(n.left)
        self.assertIsNone(n.right)


if __name__ == "__main__":
    unittest.main()
