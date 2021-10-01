import pytest

from noti import XbarItem
from noti import XbarSeperator

class TestXbarSDK:

    @pytest.fixture
    def item(self):
        return XbarItem("test")

    def test_shell(self, item):
        item.shell("vi hello")

        assert str(item) == "test | shell=\"vi hello\" terminal=false"

    # `alternate=false` shouldn't be there since it is the default behaviour  
    def test_alternate(self, item):
        item.alternate(False)

        assert str(item) == "test"
    
    # There shouldn't be any `-----`
    def test_single_child(self, item):
        item.append_child(XbarItem("child"))

        assert str(item) == "test\n---\nchild"

    def test_separator(self, item):
        item.append_child(XbarItem("child1"))
        item.append_child(XbarSeperator())
        item.append_child(XbarItem("child2"))

        assert str(item) == "test\n---\nchild1\n---\nchild2"

    def test_wrong_child(self, item):
        with pytest.raises(TypeError):
            assert item.append_child(1234)
        
    def test_escape(self, item):
        item.length(89)
        assert str(item).endswith("| length=89")

    def test_nested(self, item):
        child1 = XbarItem("child1", level=2)
        child1.append_child(XbarItem("child1_1", level=3))

        child2 = XbarItem("child2", level=2)
        child2.append_child(XbarItem("child2_1", level=3))
        child2.append_child(XbarSeperator())
        child2.append_child(XbarItem("child2_2", level=3))

        item.append_child(child1)
        item.append_child(child2)

        assert str(item) == (
            "test\n"
            "---\n"
            "child1\n"
            "--child1_1\n"
            "child2\n"
            "--child2_1\n"
            "-----\n"
            "--child2_2")