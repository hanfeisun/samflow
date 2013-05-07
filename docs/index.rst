.. pyflow documentation master file, created by
   sphinx-quickstart on Tue Mar 12 20:50:53 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyflow's documentation!
==================================

Building flexible workflow using script language like Shell could be fallible.

For example, ``bam_maker`` is a tool that will generate ``.bam`` files. It will create ``test_reads.bam`` and ``test_reads.log`` using this command:

::

  bam_maker --name=test

``bam_reader`` is a tool that use a ``.bam`` file as input. Combined with ``bam_maker``, a workflow might be written
like this:

::

  bam_maker --name=test
  bam_reader < test.bam

However, this will introduce a bug because the output of ``bam_maker`` is ``test_reads.bam`` but the input of
``bam_reader`` is ``test.bam``. The programmer might know that the output of ``bam_maker`` is ``test_reads.bam`` but
misremember it as ``test.bam`` in ``bam_reader``.
And it would be hard to find the bug until the script is executed to ``bam_reader``, which
might takes long time to test if ``bam_maker`` is a time-consuming tool.



It would be better if there's a tool to mark the input/output of a command and detect logical errors automatically before executing the whole workflow.

Pyflow is designed to solve this problem. Using Pyflow, the workflow can be written like this:

::


  from pyflow import ShellCommand, Workflow

  root_workflow = Workflow("main")
  bam_maker = ShellCommand("bam_maker --name={params[name]}",
                            params = {"name": "test"},
                            output = {"bam": "test_reads.bam"})
  bam_reader = ShellCommand("bam_reader < {input[bam]}",
                            input  = {"bam": "test.bam"})

  root_workflow.append(bam_maker, bam_reader)
  root_workflow.invoke()

Though it needs more lines of codes, Pyflow can help to find the logical bug even before the workflow is executed. As
``bam_reader``'s input is ``test.bam``, which doesn't exist before executing the workflow. And this file doesn't exist
as some commands' output before ``bam_reader``, which is ``bam_maker``, in the ``root_workflow``. So pyflow will exit
and print the information of this error even before execute the `bam_maker` command.


For each command in the workflow, pyflow will check its input before executing, and check its output after executing it.

Moreover, pyflow provide ``dry-run`` and ``resume`` mode to help users write and test their workflow more quickly.

pyflow also contains ``PythonCommand`` to facilitate using a python function as a command, which also has the ``input``,
``output`` field to be checked.

Contents:

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

