class Lazy(object):
    def __init__(self, ref_obj, action_wrapper):
        self._obj = ref_obj
        self._wrapper = action_wrapper

    def fetch(self):
        return self._wrapper(self._obj)

    def fake(self):
        return "[not init]"

class LazyCollector(Lazy):
    def __init__(self, ref_obj_container, **args):
        self._obj_container = ref_obj_container
        self._wrapper = {}
        for k, v in args.items():
            self._wrapper[k] = v

    def fetch(self):
        ret_dict = {}
        for k, v in self._wrapper.items():
            ret_dict[k] = []
            for obj_i in self._obj_container:
                try:
                    ret_dict[k].append(v(obj_i))
                except:
                    print(k, v, obj_i)
                    raise

        return ret_dict



def fetch(lazy_obj):
    if isinstance(lazy_obj, Lazy):
        return lazy_obj.fetch()
    if isinstance(lazy_obj, dict):
        return {k: fetch(v) for k,v in lazy_obj.items()}
    if isinstance(lazy_obj, list):
        return [fetch(i) for i in lazy_obj]
    return lazy_obj

def fake_fetch(lazy_obj):
    if isinstance(lazy_obj, Lazy):
        return lazy_obj.fake()
    if isinstance(lazy_obj, dict):
        return {k: fake_fetch(v) for k,v in lazy_obj.items()}
    if isinstance(lazy_obj, list):
        return [fake_fetch(i) for i in lazy_obj]
    return lazy_obj

def print_command_details(cmd):
    print("template", cmd.template)
    print("input: ", cmd.input)
    print("output: ", cmd.output)
    print("param: ", cmd.param)