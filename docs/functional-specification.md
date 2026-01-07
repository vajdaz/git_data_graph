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

### Visual Styling

Each object type should be visually distinct for educational clarity:

| Object Type | Shape | Color |
|-------------|-------|-------|
| Commits | Ellipse | Yellow |
| Trees | Folder | Green |
| Blobs | Cylinder | Blue |
| Tag Objects | Note | Orange |
| References | Box | Gray |

### Hash Display

Object hashes should be displayed in abbreviated form (7 characters) for readability.

### Object Scope

The tool should display ALL objects in the repository, including unreachable/orphaned objects. This supports educational use cases where students can observe garbage collection candidates.

## Usage

The tool should have following CLI interface:

```
git_data_graph [-h] [-o OUTPUT] [--no-index] [-s] [--force] [path]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `path` | Path to Git repository (default: current working directory) |
| `-o, --output` | Output file path (default: `git_data_graph.svg`) |
| `--no-index` | Exclude index table from output |
| `-s, --short` | Short mode: show only references and commits (hide trees, blobs, and index) |
| `--force` | Skip confirmation prompt for large repositories |
| `-h, --help` | Show help message |

### Output Formats

The output format is determined by the file extension of the output path:

- `.svg` - Scalable Vector Graphics (default)
- `.png` - PNG image
- `.pdf` - PDF document

### Default Behavior

- If `output_file_path` is not specified, a file `git_data_graph.svg` shall be created in the current working directory.
- If `path_to_git_repo` is not specified, the current working directory is used as the input path to the Git repository.

## Large Repository Handling

For educational purposes, the tool is designed for small demonstration repositories. When the repository contains more than 100 objects:

1. The tool displays a warning message with the object count
2. The user is prompted to confirm continuation
3. The `--force` flag bypasses this confirmation

## Error Handling

The tool should provide clear error messages for common issues:

| Scenario | Behavior |
|----------|----------|
| Path is not a Git repository | Exit with error message and code 1 |
| Git CLI not installed | Exit with error message and code 2 |
| Graphviz not installed | Exit with error message and code 3 |
| User aborts large repo prompt | Exit with code 4 |
| Cannot write output file | Exit with error message and code 5 |

## External Dependencies

The tool requires the following external programs to be installed:

- **Git** - for reading repository data
- **Graphviz** - for rendering the graph

## Platform Support

The tool must work on:

- Linux
- Windows

Path handling must use cross-platform compatible methods.
