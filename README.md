# Samflow 

Samflow is a Python library to help user write robust and concise codes for workflow.

## Design patterns

Samflow utilizes the [composite pattern](https://www.wikiwand.com/en/Composite_pattern) to let the client to 
treat individual objects (Command) and compositions (Workflow) uniformly. It also encourages 
[prototype pattern](https://www.wikiwand.com/en/Prototype_pattern) to build the similar command object concisely.

## Template syntax

Samflow uses a consistent template syntax to make the codes more readiable, below is an example

```
ShellCommand(
    "{tool} -p {param[NUM_THREADS]} -S -m 1 {param[index]} {input[fastq]} {output[sam]}",
    tool = "bowtie",
    input = {"fastq": target + ".fastq"},
    output = {"sam": target + ".sam"},
    param = {"NUM_THREADS": conf.threads,
             "index": conf.get_path("statics_root", "genome_index")},
    name = "bowtie aln")
```

## Dependency detection

File mismatches and (third-party tool) runtime errors are common issues when writing workflows. 
It is necessary to detect the issues as early as possible.

Samflow checks the existing input/output information linearly for each commands in the whole workflow and throws error when it detects a "dangling" input, which is usually caused by runtime error from third-party tools or input files missing.

The dependency detection happends both in load-time (when the configuration is loaded) and in run-time (when the pipeline is running).

## Who uses it

[Chilin](https://github.com/cfce/chilin) uses samflow currently.


