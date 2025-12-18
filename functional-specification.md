# Functional Specification

## Goal Of The Tool

The goal of this project is to implement a tool that creates a graphical representation of the internal data structure of a git repository for educational purposes. The input is a path to a git repository (by default the current working directory) and the output is a single image with the graph of all Git objects and a table of the Git index.

## Graphical Representation 

The graphical representation should be a directed graph with all Git objects and a table with the contents of the Git index.

The graph should contain:

- Objects
  - Commits
  - Trees
  - Blobs
  - Tag objects
- References
  - Local branches
  - Remote branches
  - Tag references
  - HEAD

The table of index entries should contain:

- Hash
- Path

## Usage

The tool should have following CLI interface:

```
git_data_graph [-o output_file_path] [path_to_git_repo] 
```

If `output_file_path` is not specified then a file `git_data_graph.svg` shall be created in the current working path.

If `path_to_git_repo` is not specified then the current working path should be considered as the input path to the Git repo.