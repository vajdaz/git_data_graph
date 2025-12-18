# git_data_graph

A command-line tool that creates graphical visualizations of Git repository internals for educational purposes.

## Overview

`git_data_graph` generates a visual graph representation of the internal data structures within a Git repository. This includes all Git objects (commits, trees, blobs, tags), references (branches, tags, HEAD), and the staging area (index). The tool is designed for educational purposes to help understand how Git stores and organizes data internally.

### Features

- Visualizes all Git objects including orphaned/unreachable objects
- Shows relationships between commits, trees, blobs, and tags
- Displays all references (local branches, remote branches, tags, HEAD)
- Includes Git index (staging area) as a table
- Supports multiple output formats (SVG, PNG, PDF)
- Cross-platform support (Linux, Windows)

### Visual Styling

Each object type has a distinct visual appearance:

| Object Type | Shape | Color |
|-------------|-------|-------|
| Commits | Ellipse | Yellow |
| Trees | Folder | Green |
| Blobs | Cylinder | Blue |
| Tag Objects | Note | Orange |
| References | Box | Gray |

## Requirements

### System Requirements

- **Python 3.6** or later
- **Git** - for reading repository data
- **Graphviz** - for rendering the graph

### Installing Dependencies

#### Linux (Debian/Ubuntu)

```bash
sudo apt-get install git graphviz
```

#### Linux (Fedora/RHEL)

```bash
sudo dnf install git graphviz
```

#### Linux (Arch)

```bash
sudo pacman -S git graphviz
```

#### Windows

1. Install [Git for Windows](https://git-scm.com/download/win)
2. Install [Graphviz](https://graphviz.org/download/) and ensure it's in your PATH

#### macOS

```bash
brew install git graphviz
```

## Installation

### From Source

```bash
git clone https://github.com/your-username/git_data_graph.git
cd git_data_graph
pip install .
```

### Development Installation

```bash
pip install -e .
```

## Usage

### Basic Usage

```bash
# Visualize the current Git repository
git_data_graph

# Visualize a specific repository
git_data_graph /path/to/repo

# Output to a specific file
git_data_graph -o my_graph.svg

# Output as PNG
git_data_graph -o graph.png

# Output as PDF
git_data_graph -o graph.pdf
```

### Command-Line Options

```
usage: git_data_graph [-h] [-o OUTPUT] [--no-index] [--force] [--version] [path]

Generate a graph visualization of Git repository internals.

positional arguments:
  path                  Path to Git repository (default: current directory)

optional arguments:
  -h, --help            Show help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file path (default: git_data_graph.svg)
  --no-index            Exclude index table from output
  --force               Process large repositories without aborting
  --version             Show program version and exit
```

### Examples

```bash
# Visualize current directory, output to git_data_graph.svg
git_data_graph

# Visualize specific repository
git_data_graph /path/to/repo

# Output as PNG image
git_data_graph -o graph.png

# Exclude the index table
git_data_graph --no-index

# Process a large repository (>100 objects)
git_data_graph --force
```

### Output Formats

The output format is determined by the file extension:

| Extension | Format |
|-----------|--------|
| `.svg` | Scalable Vector Graphics (default) |
| `.png` | PNG image |
| `.pdf` | PDF document |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Path is not a Git repository |
| 2 | Git command not found |
| 3 | Graphviz not found |
| 4 | User aborted (large repository warning) |
| 5 | Cannot write output file |

## Large Repository Warning

This tool is designed for small educational repositories. When a repository contains more than 100 objects, the tool will display a warning and abort. Use the `--force` flag to process large repositories anyway:

```bash
git_data_graph --force /path/to/large/repo
```

## Building Executables

The project supports building standalone executables using [Nuitka](https://nuitka.net/):

### Linux

```bash
pip install nuitka
python -m nuitka --standalone --onefile src/git_data_graph
```

### Windows

```bash
pip install nuitka
python -m nuitka --standalone --onefile src\git_data_graph
```

## Project Structure

```
git_data_graph/
├── src/
│   ├── __init__.py          # Package metadata
│   ├── __main__.py          # Entry point for python -m
│   ├── main.py              # CLI handling and workflow
│   ├── git_reader.py        # Git CLI wrapper
│   ├── model.py             # Data classes for Git objects
│   ├── dot_generator.py     # DOT language generation
│   ├── renderer.py          # Graphviz invocation
│   └── utils.py             # Cross-platform utilities
├── tests/                   # Test suite
├── docs/                    # Documentation
├── setup.py                 # Package configuration
└── README.md                # This file
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Built using [Graphviz](https://graphviz.org/) for graph rendering
- Inspired by the need to visualize Git internals for educational purposes
