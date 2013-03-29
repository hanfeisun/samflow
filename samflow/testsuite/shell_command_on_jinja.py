import unittest
from samflow.command_on_jinja import JinjaFormatShellCommand as JShellCommand

class JShellCommandTestCase(unittest.TestCase):

    def touch_files(self, *files):
        self.assertTrue(JShellCommand("touch {{ output|join(' ') }}", output=files, name="touch_files").invoke())

    def delete_files(self, *files):
        self.assertTrue(JShellCommand("rm {{ input|join(' ') }}", input=files, name="delete_files").invoke())

    def test_invoke_success_status(self):
        self.assertTrue(JShellCommand("echo 'run successfully' > /dev/null", name="echo_str").invoke())
        self.assertTrue(JShellCommand("exit 0", name="exit_success").invoke())

    def test_invoke_fail_status(self):
        self.assertFalse((JShellCommand(template="exit 1")).invoke())

    def test_invoke_collect_output(self):
        echo_cmd = JShellCommand("echo test_collect", name="echo_collect").set_stdout_collecting()
        self.assertTrue(echo_cmd.invoke())
        self.assertEqual(echo_cmd.result, "test_collect\n")

    def test_invoke_non_exist_input(self):
        non_exist_input_cmd = JShellCommand("cat < {{ input }}", input="non_exist_file", name="non_exist_input")
        self.assertFalse(non_exist_input_cmd.invoke())

    def test_invoke_non_exist_output(self):
        non_exist_output_cmd = JShellCommand(
            "echo {{ output }}", output="tempfile3", name="non_exist_output",)
        self.assertFalse(non_exist_output_cmd.invoke())


    def test_invoke_exist_input(self):
        self.touch_files("temp_file", "temp_file.1")
        self.delete_files("temp_file", "temp_file.1")

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(JShellCommandTestCase))
    return suite


