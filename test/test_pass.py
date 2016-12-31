import unittest
from dric import Pass, get_pass_manager

class TestPass(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_type_error(self):
        def add():
            class MyPass(object):
                pass
            get_pass_manager().add_pass(MyPass())
        def add_no_load():
            class MyPass(Pass):
                pass
            get_pass_manager().add_pass(MyPass())
        def remove():
            class MyPass(object):
                pass
            get_pass_manager().remove_pass(MyPass())
        self.assertRaises(TypeError, add)
        self.assertRaises(TypeError, add_no_load)
        self.assertRaises(TypeError, remove)


    def test_remove_unknown_pass(self):
        class MyPass(Pass):
            def load(self, plugin):
                pass
        def remove():
            get_pass_manager().remove_pass(MyPass())
        self.assertRaises(ValueError, remove)

    def test_add_load_remove(self):
        plugin = [0, 0] # the plugin is a simple array
        class MyPass(Pass):
            def load(self, plugin):
                plugin[0] = 1
        class MyPass2(Pass):
            def load(self, plugin):
                plugin[1] = 1
        get_pass_manager().add_pass(MyPass())
        my_pass2 = MyPass2()
        get_pass_manager().add_pass(my_pass2)
        get_pass_manager().remove_pass(my_pass2)
        for pass_ in get_pass_manager():
            pass_.load(plugin)
        self.assertListEqual(plugin, [1, 0])
        
    
if __name__ == '__main__':
    unittest.main()
