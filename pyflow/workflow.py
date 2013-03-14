from pprint import pprint

from pyflow.command import AbstractCommand


class Workflow(AbstractCommand):
    def __init__(self, template=None, tool=None, param = {},input=[], output=[], name=""):
        AbstractCommand.__init__(self, template=None, tool=None, param = {},input=[], output=[], name=name)
        self._commands = []

    def __iter__(self):
        for cmd_i in self._commands:
            if isinstance(cmd_i, Workflow):
                for cmd_i_j in cmd_i:
                    yield cmd_i_j
            else:
                yield cmd_i

    def add_back(self, command):
        command._parent = self
        self._commands.append(command)
        return self

    def add_front(self, command):
        command._parent = self
        self._commands.insert(0, command)
        return self

    @property
    def _dangling_inputs(self):
        dangling_dict = {}
        for cmd in self:
            not_dangling = not cmd._dangling_inputs
            if not_dangling:
                continue
            if cmd.name in dangling_dict:
                # update by union of two set
                dangling_dict[cmd.name] |= set(cmd._dangling_inputs)
            else:
                dangling_dict[cmd.name] = set(cmd._dangling_inputs)
        return dangling_dict

    def invoke(self):
        dangling_inputs = self._dangling_inputs
        if dangling_inputs:
            print("The following files might be dangling. Please check whether they exists")
            pprint(dangling_inputs)
            return False
        print("{0:-^80}".format("No dangling files. Workflow started successfully"))
        for cmd in self:
            success_invoked = cmd.invoke()
            if not success_invoked:
                print("{0:!^80}".format("Error happened! Workflow stopped!"))
                return False
        print("{0:-^80}".format("Workflow finished successfully"))
        return True

    def set_option(self, verbose_level=1, dry_run=False, recursive=True, resume=False):
        self.verbose_level = verbose_level
        self.dry_run_mode = dry_run
        self.resume = resume
        if recursive:
            for cmd in self._commands:
                cmd.set_option(verbose_level, dry_run, True, resume)

def attach_back(parent : Workflow, child : AbstractCommand):
    parent.add_back(child)
    return child

def attach_front(parent : Workflow, child : AbstractCommand):
    parent.add_front(child)
    return child
