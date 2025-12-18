"""
Cross-platform utilities for git_data_graph.

This module provides utility functions for path handling, subprocess execution,
and external tool validation.
"""

from __future__ import print_function

import os
import subprocess
import sys

# Type hints compatible with Python 3.6
from typing import Optional, Tuple, List


class CommandError(Exception):
    """Exception raised when a command execution fails."""

    def __init__(self, command, returncode, stderr):
        # type: (str, int, str) -> None
        self.command = command
        self.returncode = returncode
        self.stderr = stderr
        super(CommandError, self).__init__(
            "Command '{}' failed with code {}: {}".format(
                command, returncode, stderr
            )
        )


def normalize_path(path):
    # type: (str) -> str
    """
    Normalize a path for cross-platform compatibility.
    
    Args:
        path: The path to normalize.
        
    Returns:
        The normalized absolute path.
    """
    return os.path.normpath(os.path.abspath(path))


def run_command(args, cwd=None, check=True):
    # type: (List[str], Optional[str], bool) -> Tuple[int, str, str]
    """
    Execute a command and return its output.
    
    Args:
        args: Command and arguments as a list.
        cwd: Working directory for the command.
        check: If True, raise CommandError on non-zero exit code.
        
    Returns:
        Tuple of (returncode, stdout, stderr).
        
    Raises:
        CommandError: If check is True and command returns non-zero exit code.
    """
    try:
        # Use subprocess.PIPE for capturing output
        # shell=False for security
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            # Ensure text mode output on Python 3
            universal_newlines=True
        )
        stdout, stderr = process.communicate()
        returncode = process.returncode
        
        if check and returncode != 0:
            raise CommandError(" ".join(args), returncode, stderr)
            
        return returncode, stdout, stderr
        
    except OSError as e:
        # Command not found or other OS error
        raise CommandError(" ".join(args), -1, str(e))


def is_git_repository(path):
    # type: (str) -> bool
    """
    Check if the given path is inside a Git repository.
    
    Args:
        path: Path to check.
        
    Returns:
        True if the path is inside a Git repository, False otherwise.
    """
    try:
        returncode, stdout, stderr = run_command(
            ["git", "rev-parse", "--git-dir"],
            cwd=path,
            check=False
        )
        return returncode == 0
    except CommandError:
        return False


def get_git_dir(path):
    # type: (str) -> Optional[str]
    """
    Get the .git directory for a repository.
    
    Args:
        path: Path to the repository.
        
    Returns:
        Absolute path to the .git directory, or None if not a repository.
    """
    try:
        returncode, stdout, stderr = run_command(
            ["git", "rev-parse", "--git-dir"],
            cwd=path,
            check=False
        )
        if returncode == 0:
            git_dir = stdout.strip()
            # If relative path, make it absolute
            if not os.path.isabs(git_dir):
                git_dir = os.path.join(path, git_dir)
            return normalize_path(git_dir)
        return None
    except CommandError:
        return None


def check_git_available():
    # type: () -> Tuple[bool, str]
    """
    Check if git CLI is available.
    
    Returns:
        Tuple of (available, version_or_error_message).
    """
    try:
        returncode, stdout, stderr = run_command(
            ["git", "--version"],
            check=False
        )
        if returncode == 0:
            return True, stdout.strip()
        return False, "git command returned error"
    except CommandError as e:
        return False, str(e)


def check_graphviz_available():
    # type: () -> Tuple[bool, str]
    """
    Check if Graphviz dot command is available.
    
    Returns:
        Tuple of (available, version_or_error_message).
    """
    try:
        returncode, stdout, stderr = run_command(
            ["dot", "-V"],
            check=False
        )
        # dot -V outputs to stderr, not stdout
        if returncode == 0:
            version = stderr.strip() if stderr.strip() else stdout.strip()
            return True, version
        return False, "dot command returned error"
    except CommandError as e:
        return False, str(e)


def validate_output_path(path):
    # type: (str) -> Tuple[bool, str]
    """
    Validate that the output path is writable.
    
    Args:
        path: The output file path to validate.
        
    Returns:
        Tuple of (valid, error_message). error_message is empty if valid.
    """
    # Normalize the path
    path = normalize_path(path)
    
    # Get the directory
    directory = os.path.dirname(path)
    if not directory:
        directory = "."
    
    # Check if directory exists
    if not os.path.exists(directory):
        return False, "Directory '{}' does not exist".format(directory)
    
    # Check if directory is writable
    if not os.access(directory, os.W_OK):
        return False, "Directory '{}' is not writable".format(directory)
    
    # If file exists, check if it's writable
    if os.path.exists(path) and not os.access(path, os.W_OK):
        return False, "File '{}' is not writable".format(path)
    
    return True, ""


def get_output_format(path):
    # type: (str) -> str
    """
    Determine output format from file extension.
    
    Args:
        path: Output file path.
        
    Returns:
        Format string: 'svg', 'png', or 'pdf'. Defaults to 'svg'.
    """
    _, ext = os.path.splitext(path)
    ext = ext.lower()
    
    format_map = {
        ".svg": "svg",
        ".png": "png",
        ".pdf": "pdf",
    }
    
    return format_map.get(ext, "svg")


def abbreviate_hash(hash_str, length=7):
    # type: (str, int) -> str
    """
    Abbreviate a Git hash to the specified length.
    
    Args:
        hash_str: Full hash string.
        length: Number of characters to keep (default: 7).
        
    Returns:
        Abbreviated hash.
    """
    return hash_str[:length] if hash_str else ""
