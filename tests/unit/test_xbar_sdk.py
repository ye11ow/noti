from noti import XbarItem

class TestXbarSDK:

    def test_shell(self):
        item = XbarItem("test").shell("vi hello")

        assert str(item) == "test | shell=\"vi hello\" terminal=false"

    # `alternate=false` shouldn't be there since it is the default behaviour  
    def test_alternate(self):
        item = XbarItem("test").alternate(False)

        assert str(item) == "test"
    
    # There shouldn't be any `-----`
    def test_single_child(self):
        item = XbarItem("test")

        item._children.append(XbarItem("child"))

        assert str(item) == "test\nchild"