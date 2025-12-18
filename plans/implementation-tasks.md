# Implementation Tasks

This checklist provides the step-by-step implementation order for the git_data_graph tool.

## Phase 1: Project Setup

- [x] Create project directory structure (`src/`, `tests/`)
- [x] Create `src/__init__.py` with version info
- [x] Create `setup.py` or `pyproject.toml` for packaging
- [x] Create `.gitignore` for Python projects

## Phase 2: Core Utilities

- [x] Implement `src/utils.py`
  - [x] Cross-platform path normalization
  - [x] Subprocess wrapper with error handling
  - [x] Git repository validation function
  - [x] External tool availability check (git, dot)

## Phase 3: Data Model

- [x] Implement `src/model.py`
  - [x] Create `GitObject` base class
  - [x] Create `GitCommit` dataclass
  - [x] Create `GitTree` and `TreeEntry` dataclasses
  - [x] Create `GitBlob` dataclass
  - [x] Create `GitTag` dataclass
  - [x] Create `GitRef` dataclass with `RefType` enum
  - [x] Create `IndexEntry` dataclass
  - [x] Create `Repository` container class

## Phase 4: Git Reader

- [x] Implement `src/git_reader.py`
  - [x] Function to list all objects (`git cat-file --batch-check --batch-all-objects`)
  - [x] Function to parse object content (`git cat-file -p`)
  - [x] Function to read commit details
  - [x] Function to read tree entries
  - [x] Function to read blob metadata
  - [x] Function to read tag objects
  - [x] Function to list references (`git for-each-ref`)
  - [x] Function to resolve HEAD (`git symbolic-ref`)
  - [x] Function to read index entries (`git ls-files --stage`)
  - [x] Main function to build Repository model

## Phase 5: DOT Generator

- [x] Implement `src/dot_generator.py`
  - [x] DOT header/footer generation
  - [x] Commit node generation (yellow ellipse)
  - [x] Tree node generation (green folder)
  - [x] Blob node generation (blue cylinder)
  - [x] Tag node generation (orange note)
  - [x] Reference node generation (gray box)
  - [x] Edge generation for all relationship types
  - [x] Index table generation as HTML table
  - [x] Hash abbreviation (7 chars)
  - [x] Main function to generate complete DOT source

## Phase 6: Renderer

- [x] Implement `src/renderer.py`
  - [x] Output format detection from file extension
  - [x] Graphviz dot command invocation
  - [x] Error handling for rendering failures
  - [x] Support for SVG, PNG, PDF output

## Phase 7: CLI and Main

- [x] Implement `src/main.py`
  - [x] Argument parser setup with argparse
  - [x] Input validation (repository path)
  - [x] External tool availability check
  - [x] Large repository warning and prompt
  - [x] Workflow orchestration
  - [x] Exit codes implementation
  - [x] Entry point function

## Phase 8: Packaging

- [x] Create executable entry point
- [x] Test nuitka compilation on Linux
- [ ] Test nuitka compilation on Windows
- [ ] Verify cross-platform functionality

## Phase 9: Testing

- [ ] Create test repository fixtures
- [ ] Unit tests for model classes
- [ ] Unit tests for git_reader (with mocked git output)
- [ ] Unit tests for dot_generator
- [ ] Integration tests with real git repositories
- [ ] Test edge cases (empty repo, detached HEAD, etc.)

## Phase 10: Documentation

- [x] Create README.md with usage instructions
- [x] Document installation requirements
- [x] Add license information with MIT license