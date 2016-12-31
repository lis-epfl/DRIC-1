import unittest
import dric

class TestEventBus(unittest.TestCase):
    def setUp(self):
        self.bus = dric.EventBus()
       
    def test_unsubscribe(self):
        called = False
        def handler():
            global called
            called = True
        self.bus.subscribe('event', handler)
        self.bus.unsubscribe('event', handler)
        self.bus.publish('event')
        self.assertFalse(called)
    
    def test_duplicates_raise(self):
        self.bus.subscribe('event', self)
        with self.assertRaises(dric.evbus.DuplicateListenerError):
            self.bus.subscribe('event', self)

    def test_duplicates_allowed(self):
        self.bus.subscribe('event', self)
        try:
            self.bus.subscribe('event', self, allow_duplicates=True)
        except dric.evbus.DuplicateListenerError as e:
            self.fail(e)
        
    def test_duplicates(self):
        called_n = []
        def handler():
            called_n.append(1)
        self.bus.subscribe('event', handler)
        self.bus.subscribe('event', handler, allow_duplicates=True)
        self.bus.subscribe('event', handler, allow_duplicates=True)
        self.bus.publish('event')
        self.assertEqual(len(called_n), 3)
    
    def test_args(self):
        def handler(positional, named):
            return positional + named
        self.bus.subscribe('event', handler)
        response = self.bus.publish('event', 'POSITIONAL&', named='NAMED')
        self.assertEqual(['POSITIONAL&NAMED'], response)

    def test_list_result(self):
        def handler1():
            return 'handler1'
        def handler2():
            return 'handler2'
        self.bus.subscribe('event', handler1)
        self.bus.subscribe('event', handler2)
        result = self.bus.publish('event')
        self.assertIsInstance(result, list)
        self.assertIn('handler1', result)
        self.assertIn('handler2', result)

    def test_async_publish(self):
        def handlers(i):
            def handler1():
                return i
            return handler1
        def callback(value):
            callback.count += 1
        callback.count = 0
        for i in range(1, 500):
            self.bus.subscribe('event', handlers(i), allow_duplicates=True)
        self.bus.publish_async('event', callback)
        self.bus.pool.waitall()
        self.assertEqual(callback.count, 499)

    def test_async_and_sync(self):
        def async_cb(v):
            async_cb.v = v
            return v
        def handler(v):
            return v
        self.bus.subscribe('event', handler)
        result = self.bus.publish('event', 'SYNC')
        self.bus.publish_async('event', async_cb, 'ASYNC')        
        self.bus.pool.waitall()
        self.assertEqual(result, ['SYNC'])
        self.assertEqual(async_cb.v, 'ASYNC')

if __name__ == '__main__':
    unittest.main()
