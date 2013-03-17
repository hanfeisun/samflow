class Lazy(object):
    def __init__(self, ref_obj, action_wrapper):
        self._obj = ref_obj
        self._wrapper = action_wrapper
    def fetch(self):
        return self._wrapper(self._obj)
class LazyCollector(Lazy):
    def __init__(self, ref_obj_container, **args):
        self._obj_container = ref_obj_container
        self._wrapper = {}
        for k, v in args.items():
            self._wrapper[k] = v
    def fetch(self):
        return {k: [v(obj_i) for obj_i in self._obj_container] for k,v in self._wrapper.items()}



def fetch(lazy_obj):
    if isinstance(lazy_obj, Lazy):
        return lazy_obj.fetch()
    if isinstance(lazy_obj, dict):
        return {k: fetch(v) for k,v in lazy_obj.items()}
    if isinstance(lazy_obj, list):
        return [fetch(i) for i in lazy_obj]
    return lazy_obj

