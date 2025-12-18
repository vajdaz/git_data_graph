# Basic Architectureal Decisions

- This project is a Python project.
- The code should be compatible with Python 3.6.
- The code should be portable between Unix/Linux and Windows (e.g. don't use "/" direclty as path separator).
- The progam may use external tools like `git` or `dot`.
- Usage of third party modules is allowed, however, the number of third party module dependencies should be as minimal as possible.
- This project uses nuitka to create executables for Linux and Windows.

# Project File Structure

- Documentation is in the `/docs` subdirectory in the project root.
- The functional specification is defined in `/docs/functional-specification.md`.
- Source code shall be in `/src`