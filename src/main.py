#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
git_data_graph - Main entry point and CLI handler.

This module provides the command-line interface and orchestrates
the workflow for generating Git repository visualizations.
"""

from __future__ import print_function

import argparse
import sys
import os

from . import __version__
from .utils import (
    normalize_path, is_git_repository, check_git_available,
    check_graphviz_available, validate_output_path, CommandError
)
from .git_reader import count_objects, read_repository
from .dot_generator import generate_dot
from .renderer import render_dot_to_file, RenderError, validate_format


# Exit codes
EXIT_SUCCESS = 0
EXIT_NOT_GIT_REPO = 1
EXIT_GIT_NOT_FOUND = 2
EXIT_GRAPHVIZ_NOT_FOUND = 3
EXIT_USER_ABORT = 4
EXIT_OUTPUT_ERROR = 5

# Large repository threshold
LARGE_REPO_THRESHOLD = 100


def create_argument_parser():
    # type: () -> argparse.ArgumentParser
    """
    Create and configure the argument parser.
    
    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="git_data_graph",
        description="Generate a graph visualization of Git repository internals.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  git_data_graph                    # Visualize current directory
  git_data_graph /path/to/repo      # Visualize specific repository
  git_data_graph -o graph.png       # Output as PNG
  git_data_graph --no-index         # Exclude index table
  git_data_graph --force            # Process large repositories

Exit codes:
  0  Success
  1  Path is not a Git repository
  2  Git command not found
  3  Graphviz not found
  4  Repository too large (use --force to override)
  5  Cannot write output file
"""
    )
    
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to Git repository (default: current directory)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="git_data_graph.svg",
        help="Output file path (default: git_data_graph.svg)"
    )
    
    parser.add_argument(
        "--no-index",
        action="store_true",
        help="Exclude index table from output"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Process large repositories (>{} objects) without aborting".format(
            LARGE_REPO_THRESHOLD
        )
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {}".format(__version__)
    )
    
    return parser


def check_prerequisites():
    # type: () -> int
    """
    Check that required external tools are available.
    
    Returns:
        Exit code (0 if all tools available, non-zero otherwise).
    """
    # Check git
    git_available, git_info = check_git_available()
    if not git_available:
        print("Error: Git is not installed or not in PATH.", file=sys.stderr)
        print("Please install Git: https://git-scm.com/", file=sys.stderr)
        return EXIT_GIT_NOT_FOUND
    
    # Check Graphviz
    graphviz_available, graphviz_info = check_graphviz_available()
    if not graphviz_available:
        print("Error: Graphviz is not installed or not in PATH.", file=sys.stderr)
        print("Please install Graphviz: https://graphviz.org/", file=sys.stderr)
        return EXIT_GRAPHVIZ_NOT_FOUND
    
    return EXIT_SUCCESS


def main(args=None):
    # type: (list) -> int
    """
    Main entry point for the application.
    
    Args:
        args: Command line arguments (for testing). If None, uses sys.argv.
        
    Returns:
        Exit code.
    """
    # Parse arguments
    parser = create_argument_parser()
    parsed_args = parser.parse_args(args)
    
    # Check prerequisites
    prereq_result = check_prerequisites()
    if prereq_result != EXIT_SUCCESS:
        return prereq_result
    
    # Normalize and validate repository path
    repo_path = normalize_path(parsed_args.path)
    
    if not os.path.isdir(repo_path):
        print("Error: Path '{}' does not exist or is not a directory.".format(
            parsed_args.path
        ), file=sys.stderr)
        return EXIT_NOT_GIT_REPO
    
    if not is_git_repository(repo_path):
        print("Error: '{}' is not a Git repository.".format(
            parsed_args.path
        ), file=sys.stderr)
        return EXIT_NOT_GIT_REPO
    
    # Validate output path
    output_path = normalize_path(parsed_args.output)
    
    # Check output format
    format_error = validate_format(output_path)
    if format_error:
        print("Error: {}".format(format_error), file=sys.stderr)
        return EXIT_OUTPUT_ERROR
    
    # Check output path is writable
    valid, error_msg = validate_output_path(output_path)
    if not valid:
        print("Error: {}".format(error_msg), file=sys.stderr)
        return EXIT_OUTPUT_ERROR
    
    # Check repository size
    try:
        object_count = count_objects(repo_path)
    except CommandError as e:
        print("Error: Failed to read repository: {}".format(e), file=sys.stderr)
        return EXIT_NOT_GIT_REPO
    
    # Abort for large repositories unless --force is provided
    if object_count > LARGE_REPO_THRESHOLD and not parsed_args.force:
        print("Error: Repository contains {} objects (threshold: {}).".format(
            object_count, LARGE_REPO_THRESHOLD
        ), file=sys.stderr)
        print("This tool is designed for small educational repositories.", file=sys.stderr)
        print("Use --force to process large repositories anyway.", file=sys.stderr)
        return EXIT_USER_ABORT
    
    # Read repository data
    print("Reading repository data...")
    try:
        include_index = not parsed_args.no_index
        repo = read_repository(repo_path, include_index=include_index)
    except CommandError as e:
        print("Error: Failed to read repository data: {}".format(e), file=sys.stderr)
        return EXIT_NOT_GIT_REPO
    
    print("Found {} commits, {} trees, {} blobs, {} tags, {} refs".format(
        len(repo.commits),
        len(repo.trees),
        len(repo.blobs),
        len(repo.tags),
        len(repo.refs)
    ))
    
    if include_index and repo.index_entries:
        print("Found {} index entries".format(len(repo.index_entries)))
    
    # Generate DOT source
    print("Generating graph...")
    dot_source = generate_dot(repo, include_index=include_index, repo_path=repo_path)
    
    # Render to output file
    print("Rendering to {}...".format(output_path))
    try:
        render_dot_to_file(dot_source, output_path)
    except RenderError as e:
        print("Error: {}".format(e.message), file=sys.stderr)
        if e.details:
            print("Details: {}".format(e.details), file=sys.stderr)
        return EXIT_OUTPUT_ERROR
    except IOError as e:
        print("Error: Failed to write output file: {}".format(e), file=sys.stderr)
        return EXIT_OUTPUT_ERROR
    
    print("Done! Output written to: {}".format(output_path))
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
