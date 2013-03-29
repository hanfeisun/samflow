from jinja2 import Environment

from samflow.command import ShellCommand


env = Environment()

class JinjaFormatShellCommand(ShellCommand):
    def __init__(self, template=None, tool=None, param={}, input=[], output=[], name="", env = env):
        ShellCommand.__init__(self, template, tool, param, input, output, name)
        self._template = env.from_string(self.template)

    def _render(self):
        cmd = self._template.render(input=self.input, output=self.output, param=self.param, tool=self.tool)
        return cmd


