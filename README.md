# samflow 

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

File mismatch is a common mistake when writing workflows. 
Samflow utilized dependency detection to detect the mistake as early as possible, 
both in load-time (when the configuration is loaded) and run-time (when the pipeline is running).





