"""
Graphviz renderer for DOT source.

This module invokes the Graphviz dot command to render DOT source
into various output formats (SVG, PNG, PDF).
"""

import subprocess
import tempfile
import os

from typing import Optional

from .utils import run_command, get_output_format, CommandError


class RenderError(Exception):
    """Exception raised when rendering fails."""
    
    def __init__(self, message, details=""):
        # type: (str, str) -> None
        self.message = message
        self.details = details
        super(RenderError, self).__init__(message)


def render_dot_to_file(dot_source, output_path):
    # type: (str, str) -> None
    """
    Render DOT source to an output file.
    
    The output format is determined by the file extension.
    
    Args:
        dot_source: DOT language source string.
        output_path: Path to the output file.
        
    Raises:
        RenderError: If rendering fails.
    """
    # Determine output format from extension
    output_format = get_output_format(output_path)
    
    # Create a temporary file for the DOT source
    # Using delete=False so we can pass the filename to dot
    fd, temp_dot_path = tempfile.mkstemp(suffix=".dot")
    try:
        # Write DOT source to temp file
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(dot_source)
        
        # Invoke Graphviz dot command
        # dot -T<format> -o <output> <input>
        try:
            returncode, stdout, stderr = run_command(
                ["dot", "-T{}".format(output_format), "-o", output_path, temp_dot_path],
                check=False
            )
            
            if returncode != 0:
                raise RenderError(
                    "Graphviz dot command failed",
                    details=stderr
                )
                
        except CommandError as e:
            raise RenderError(
                "Failed to execute Graphviz dot command",
                details=str(e)
            )
            
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_dot_path)
        except OSError:
            pass


def render_dot_to_string(dot_source, output_format="svg"):
    # type: (str, str) -> str
    """
    Render DOT source and return the result as a string.
    
    This is useful for formats like SVG that are text-based.
    
    Args:
        dot_source: DOT language source string.
        output_format: Output format (svg, png, pdf).
        
    Returns:
        Rendered output as string (for text formats like SVG).
        
    Raises:
        RenderError: If rendering fails.
    """
    # Create temporary files
    fd_in, temp_dot_path = tempfile.mkstemp(suffix=".dot")
    fd_out, temp_out_path = tempfile.mkstemp(suffix=".{}".format(output_format))
    
    try:
        # Close the output fd, we'll use the path
        os.close(fd_out)
        
        # Write DOT source to temp file
        with os.fdopen(fd_in, "w", encoding="utf-8") as f:
            f.write(dot_source)
        
        # Invoke Graphviz dot command
        try:
            returncode, stdout, stderr = run_command(
                ["dot", "-T{}".format(output_format), "-o", temp_out_path, temp_dot_path],
                check=False
            )
            
            if returncode != 0:
                raise RenderError(
                    "Graphviz dot command failed",
                    details=stderr
                )
            
            # Read the output
            with open(temp_out_path, "r", encoding="utf-8") as f:
                return f.read()
                
        except CommandError as e:
            raise RenderError(
                "Failed to execute Graphviz dot command",
                details=str(e)
            )
            
    finally:
        # Clean up temporary files
        for path in [temp_dot_path, temp_out_path]:
            try:
                os.unlink(path)
            except OSError:
                pass


def get_supported_formats():
    # type: () -> list
    """
    Get list of supported output formats.
    
    Returns:
        List of format strings.
    """
    return ["svg", "png", "pdf"]


def validate_format(output_path):
    # type: (str) -> Optional[str]
    """
    Validate that the output path has a supported format.
    
    Args:
        output_path: Path to check.
        
    Returns:
        Error message if invalid, None if valid.
    """
    fmt = get_output_format(output_path)
    supported = get_supported_formats()
    
    if fmt not in supported:
        return "Unsupported output format '.{}'. Supported formats: {}".format(
            fmt,
            ", ".join(".{}".format(f) for f in supported)
        )
    
    return None
