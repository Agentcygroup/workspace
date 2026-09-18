from tree import Node, Tree

def test_single_node():
    r = Node("root")
    t = Tree(r)
    assert t.preorder() == ["root"]
    assert t.size() == 1
    assert t.depth() == 0

def test_two_level():
    r = Node("r")
    r.add(Node("a")); r.add(Node("b"))
    t = Tree(r)
    assert set(t.preorder()) == {"r","a","b"}
    assert t.depth() == 1
    assert t.size() == 3

def test_preorder_order():
    r = Node("r"); a = Node("a"); b = Node("b")
    r.add(a); r.add(b); a.add(Node("a1"))
    t = Tree(r)
    order = t.preorder()
    assert order[0] == "r"
    assert order.index("a1") > order.index("a")

def test_postorder():
    r = Node("r"); a = Node("a")
    r.add(a)
    t = Tree(r)
    assert t.postorder() == ["a","r"]
