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

