import os
import copy
from copy import deepcopy
import subprocess
from time import strftime, localtime
from samflow.helper import fetch

class AbstractCommand(object):
    def __init__(self, template=None, tool=None, param={}, input=[], output=[], name=""):
        self.name = name
        self.input = input
        self.output = output
        self.param = param
        self.template = template
        self.tool = tool
        self.result = None
        self.verbose_level = 1
        self.dry_run_mode = False
        self.resume = False
        self.fetch_output = False

        self.allow_fail = False
        self.allow_dangling = False

        # if the parent of a command is itself, it's a root
        self._parent = self
        self._commands = []
        self._allow_zero_byte_file = True

    def add_back(self, command):
        """ For workflow only, add a command into current workflow """
        raise NotImplemented

    def add_front(self, command):
        raise NotImplemented

    def update(self, **kwargs):
        for k, v in kwargs.items():
            getattr(self, k).update(v)
        return self

    def set(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        return self

    @property
    def have_dangling(self):
        dangling_inputs = self._dangling_inputs
        if dangling_inputs:
            if self.allow_dangling:
                self._print_log("Warn", "Dangling inputs ", dangling_inputs)
            else:
                self._print_log("Error!", "Dangling inputs ", dangling_inputs)
                return True
        return False

    def invoke(self):
        """
        Invoke the command, return True if no trouble encountered.
        Dry run mode check files `dangling` for only input
        Non-dry run mode check `missing` for both input and output
        """
        try:
            if self.have_dangling:
                return False

            if self.dry_run_mode:
                self.result = self._simulate()
                return True

            missing_i = self._missing_inputs
            if missing_i:
                self._print_log("Error!", "Missing inputs", missing_i)
                return False
            execute_success = self._execute()
            if self.allow_fail:
                return True
            if not execute_success:
                return False

            missing_o = self._missing_outputs
            if missing_o:
                self._print_log("Error!", "Missing outputs", missing_o)
                return False
            return True
        except:
            print("Exception encountered @", self.name)
            print("template", self.template)
            print("input: ", self.input)
            print("output: ", self.output)
            print("param: ", self.param)
            raise

    def __deepcopy__(self, visit):
        return type(self)(template=deepcopy(self.template), tool=deepcopy(self.tool), param=deepcopy(self.param),
            input=deepcopy(self.input), output=deepcopy(self.output), name=deepcopy(self.name))

    def set_option(self, **args):
        """
        :type verbose_level: int
        verbose_level:  1 - only show fatal errors          (quiet mode)
                        2 - show fatal errors and warnings  (normal mode)
                        3 - show workflow details           (verbose mode)
                        4 - debug mode                      (debug mode)
        """
        for k, v in args.items():
            setattr(self, k, v)

    @property
    def clone(self):
        return copy.deepcopy(self)

    @property
    def _is_root(self):
        return self._parent == self

    def _simulate(self):
        """ Hook method for `invoke` in dry run mode: Pretend to run but not invoke anything """
        pass

    def _print_log(self, head, *args):
        if isinstance(self, ShellCommand) and head in ["Run", "Dry-run"]:
            start_with = ""
        else:
            start_with = "#"
        print("#[{time:<12}] {head:<10}  {name:<50} \n{prefix}".format(
            head=head,
            name=self.name,
            time=strftime("%Y-%m-%d %H:%M:%S", localtime()),
            prefix=start_with), *args)
        print()

    def _execute(self):
        """
        Hook method for `invoke`
        Return True if no trouble encountered
        """
        return True

    @property
    def _dummy_files(self):
        """
        Return a list of files that produced by leaves before current node in the tree
        """
        if self._is_root:
            # if current command is not a leaf of a tree, it shouldn't have dummy files.
            return []
        ret = []
        for a_command in self._root:
            if a_command == self:
                break
            else:
                ret += a_command._outputs
        return ret

    def _missing(self, files):
        missing = []
        files = fetch(files)

        try:
            for i in files:
                if not os.path.exists(i):
                    missing.append(i)
                    continue
                if self._allow_zero_byte_file:
                    continue
                if os.path.isfile(i) and os.path.getsize(i) == 0:
                    missing.append(i)
                    continue
            return missing
        except:
            print("Exception encountered @", self.name, self.template)
            raise

    @property
    def _missing_inputs(self):
        """
        Return a list of files that are current command's input but doesn't exist in filesystem .
        This method is called before real invoke current command.
        """
        return self._missing(self._inputs)

    @property
    def _missing_outputs(self):
        """
        Return a list of files that are current command's output but doesn't exist in filesystem .
        This method is called after real invoke current command.
        """
        return self._missing(self._outputs)

    @property
    def _dangling_inputs(self):
        """
        Return a list of files that are current commands' input but:
        (1) doesn't exist in filesystem
        (2) can't be found as some commands' output before current command

        This Hook method is called:
        (1) on each leaf before both dry run and real dry

        If current command doesn't belong to a tree, just return missing inputs
        """
        if self._is_root:
            return self._missing_inputs
        else:
            return [i for i in self._missing_inputs if i not in self._dummy_files]

    @property
    def _root(self):
        """
        Return the root of the tree in which current command is
        """
        return self if self._is_root else self._parent._root

    def _collect(self, obj):
        ret = []
        if isinstance(obj, dict):
            for i in obj.values():
                ret.extend(self._collect(i))
        elif isinstance(obj, str):
            ret = [obj]
        elif isinstance(obj, list):
            ret = obj

        return ret


    @property
    def _inputs(self):
        """ Return the inputs as a list """
        return self._collect(self.input)

    @property
    def _outputs(self):
        """ Return the outputs as a list """
        return self._collect(self.output)


class ShellCommand(AbstractCommand):
    def __init__(self, template=None, tool=None, param={}, input=[], output=[], name=""):
        AbstractCommand.__init__(self, template, tool, param, input, output, name)
        self.fetch_output = False

    def _simulate(self):
        self._print_log("Dry-run", self._render())

    def _execute(self):
        cmd_rendered = self._render()
        self._print_log("Run", cmd_rendered)
        can_skip = not self._missing_outputs
        if self.resume and can_skip:
            print("Resumed from existing result.. Skip")
            return True
        if self.fetch_output:
            try:
                self.result = subprocess.check_output(cmd_rendered, shell=True, universal_newlines=True,
                    executable="/bin/bash")
            except subprocess.CalledProcessError:
                return False
        else:
            try:
                self.result = subprocess.check_call(cmd_rendered, shell=True, executable="/bin/bash")
            except subprocess.CalledProcessError:
                return False
        return True

    def _render(self):
        """ Method that return the rendered content  """
        cmd = self.template.format(input=self.input, output=self.output, param=self.param, tool=self.tool)
        return cmd

    def set_stdout_collecting(self):
        self.fetch_output = True
        return self


class ThrowableShellCommand(ShellCommand):
    def _execute(self):
        if not ShellCommand._execute(self):
            raise BaseException


class PythonCommand(AbstractCommand):
    def _render(self):
        return "%s < %s > %s" % (self.template, self._inputs, self._outputs)

    def _execute(self):
        self._print_log("Execute: ", self._render())

        self.result = self.template(input=self.input, output=self.output, param=self.param)
        return True

    def _simulate(self):
        self._print_log("Dry-run", self._render())
        return None









