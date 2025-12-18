# Implementation Tasks

This checklist provides the step-by-step implementation order for the git_data_graph tool.

## Phase 1: Project Setup

- [ ] Create project directory structure (`src/`, `tests/`)
- [ ] Create `src/__init__.py` with version info
- [ ] Create `setup.py` or `pyproject.toml` for packaging
- [ ] Create `.gitignore` for Python projects

## Phase 2: Core Utilities

- [ ] Implement `src/utils.py`
  - [ ] Cross-platform path normalization
  - [ ] Subprocess wrapper with error handling
  - [ ] Git repository validation function
  - [ ] External tool availability check (git, dot)

## Phase 3: Data Model

- [ ] Implement `src/model.py`
  - [ ] Create `GitObject` base class
  - [ ] Create `GitCommit` dataclass
  - [ ] Create `GitTree` and `TreeEntry` dataclasses
  - [ ] Create `GitBlob` dataclass
  - [ ] Create `GitTag` dataclass
  - [ ] Create `GitRef` dataclass with `RefType` enum
  - [ ] Create `IndexEntry` dataclass
  - [ ] Create `Repository` container class

## Phase 4: Git Reader

- [ ] Implement `src/git_reader.py`
  - [ ] Function to list all objects (`git cat-file --batch-check --batch-all-objects`)
  - [ ] Function to parse object content (`git cat-file -p`)
  - [ ] Function to read commit details
  - [ ] Function to read tree entries
  - [ ] Function to read blob metadata
  - [ ] Function to read tag objects
  - [ ] Function to list references (`git for-each-ref`)
  - [ ] Function to resolve HEAD (`git symbolic-ref`)
  - [ ] Function to read index entries (`git ls-files --stage`)
  - [ ] Main function to build Repository model

## Phase 5: DOT Generator

- [ ] Implement `src/dot_generator.py`
  - [ ] DOT header/footer generation
  - [ ] Commit node generation (yellow ellipse)
  - [ ] Tree node generation (green folder)
  - [ ] Blob node generation (blue cylinder)
  - [ ] Tag node generation (orange note)
  - [ ] Reference node generation (gray box)
  - [ ] Edge generation for all relationship types
  - [ ] Index table generation as HTML table
  - [ ] Hash abbreviation (7 chars)
  - [ ] Main function to generate complete DOT source

## Phase 6: Renderer

- [ ] Implement `src/renderer.py`
  - [ ] Output format detection from file extension
  - [ ] Graphviz dot command invocation
  - [ ] Error handling for rendering failures
  - [ ] Support for SVG, PNG, PDF output

## Phase 7: CLI and Main

- [ ] Implement `src/main.py`
  - [ ] Argument parser setup with argparse
  - [ ] Input validation (repository path)
  - [ ] External tool availability check
  - [ ] Large repository warning and prompt
  - [ ] Workflow orchestration
  - [ ] Exit codes implementation
  - [ ] Entry point function

## Phase 8: Packaging

- [ ] Create executable entry point
- [ ] Test nuitka compilation on Linux
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

- [ ] Create README.md with usage instructions
- [ ] Document installation requirements
- [ ] Add example output images
- [ ] Create CONTRIBUTING.md if needed
