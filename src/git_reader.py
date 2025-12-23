"""
Git repository data reader.

This module provides functions to read Git repository data using the git CLI.
"""

from typing import List, Optional, Tuple

from .model import (
    Repository, GitCommit, GitTree, GitBlob, GitTag,
    GitRef, RefType, IndexEntry, TreeEntry
)
from .utils import run_command, CommandError


def list_all_objects(repo_path):
    # type: (str) -> List[Tuple[str, str, int]]
    """
    List all objects in the repository.
    
    Uses: git cat-file --batch-check --batch-all-objects
    
    Args:
        repo_path: Path to the Git repository.
        
    Returns:
        List of tuples: (hash, type, size).
    """
    returncode, stdout, stderr = run_command(
        ["git", "cat-file", "--batch-check", "--batch-all-objects"],
        cwd=repo_path,
        check=True
    )
    
    objects = []
    for line in stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 3:
            obj_hash = parts[0]
            obj_type = parts[1]
            obj_size = int(parts[2])
            objects.append((obj_hash, obj_type, obj_size))
    
    return objects


def read_commit(repo_path, commit_hash):
    # type: (str, str) -> GitCommit
    """
    Read commit object details.
    
    Uses: git cat-file -p <hash>
    
    Args:
        repo_path: Path to the Git repository.
        commit_hash: Hash of the commit object.
        
    Returns:
        GitCommit object.
    """
    returncode, stdout, stderr = run_command(
        ["git", "cat-file", "-p", commit_hash],
        cwd=repo_path,
        check=True
    )
    
    tree_hash = ""
    parent_hashes = []
    author = ""
    message = ""
    
    lines = stdout.split("\n")
    in_message = False
    message_lines = []
    
    for line in lines:
        if in_message:
            message_lines.append(line)
        elif line == "":
            in_message = True
        elif line.startswith("tree "):
            tree_hash = line[5:].strip()
        elif line.startswith("parent "):
            parent_hashes.append(line[7:].strip())
        elif line.startswith("author "):
            # Parse author line: author Name <email> timestamp timezone
            author_part = line[7:]
            # Extract just the name and email
            if " <" in author_part:
                author = author_part.split(" <")[0]
            else:
                author = author_part.split()[0] if author_part else ""
    
    message = "\n".join(message_lines).strip()
    # Get just the first line of the message
    first_line = message.split("\n")[0] if message else ""
    
    return GitCommit(
        hash_value=commit_hash,
        tree_hash=tree_hash,
        parent_hashes=parent_hashes,
        message=first_line,
        author=author
    )


def read_tree(repo_path, tree_hash):
    # type: (str, str) -> GitTree
    """
    Read tree object details.
    
    Uses: git cat-file -p <hash>
    
    Args:
        repo_path: Path to the Git repository.
        tree_hash: Hash of the tree object.
        
    Returns:
        GitTree object with entries.
    """
    returncode, stdout, stderr = run_command(
        ["git", "cat-file", "-p", tree_hash],
        cwd=repo_path,
        check=True
    )
    
    entries = []
    for line in stdout.strip().split("\n"):
        if not line:
            continue
        # Format: <mode> <type> <hash>\t<name>
        parts = line.split("\t", 1)
        if len(parts) == 2:
            meta = parts[0].split()
            name = parts[1]
            if len(meta) >= 3:
                mode = meta[0]
                obj_type = meta[1]
                obj_hash = meta[2]
                entries.append(TreeEntry(
                    mode=mode,
                    obj_type=obj_type,
                    hash_value=obj_hash,
                    name=name
                ))
    
    return GitTree(hash_value=tree_hash, entries=entries)


def read_blob_metadata(repo_path, blob_hash, size):
    # type: (str, str, int) -> GitBlob
    """
    Create a GitBlob from metadata.
    
    We don't read the actual content, just use the size from batch-check.
    
    Args:
        repo_path: Path to the Git repository.
        blob_hash: Hash of the blob object.
        size: Size of the blob in bytes.
        
    Returns:
        GitBlob object.
    """
    return GitBlob(hash_value=blob_hash, size=size)


def read_tag(repo_path, tag_hash):
    # type: (str, str) -> GitTag
    """
    Read annotated tag object details.
    
    Uses: git cat-file -p <hash>
    
    Args:
        repo_path: Path to the Git repository.
        tag_hash: Hash of the tag object.
        
    Returns:
        GitTag object.
    """
    returncode, stdout, stderr = run_command(
        ["git", "cat-file", "-p", tag_hash],
        cwd=repo_path,
        check=True
    )
    
    target_hash = ""
    tag_name = ""
    tagger = ""
    message = ""
    
    lines = stdout.split("\n")
    in_message = False
    message_lines = []
    
    for line in lines:
        if in_message:
            message_lines.append(line)
        elif line == "":
            in_message = True
        elif line.startswith("object "):
            target_hash = line[7:].strip()
        elif line.startswith("tag "):
            tag_name = line[4:].strip()
        elif line.startswith("tagger "):
            tagger_part = line[7:]
            if " <" in tagger_part:
                tagger = tagger_part.split(" <")[0]
            else:
                tagger = tagger_part.split()[0] if tagger_part else ""
    
    message = "\n".join(message_lines).strip()
    first_line = message.split("\n")[0] if message else ""
    
    return GitTag(
        hash_value=tag_hash,
        target_hash=target_hash,
        name=tag_name,
        message=first_line,
        tagger=tagger
    )


def list_references(repo_path):
    # type: (str) -> List[GitRef]
    """
    List all references in the repository.
    
    Uses: git for-each-ref --format='%(refname) %(objectname) %(upstream)'
    
    Args:
        repo_path: Path to the Git repository.
        
    Returns:
        List of GitRef objects.
    """
    # Use a delimiter to handle empty upstream values
    delimiter = "|||"
    returncode, stdout, stderr = run_command(
        ["git", "for-each-ref", "--format=%(refname)" + delimiter + "%(objectname)" + delimiter + "%(upstream)"],
        cwd=repo_path,
        check=True
    )
    
    refs = []
    for line in stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split(delimiter)
        if len(parts) >= 2:
            ref_name = parts[0]
            target_hash = parts[1]
            upstream = parts[2] if len(parts) >= 3 and parts[2] else None
            
            # Determine ref type
            if ref_name.startswith("refs/heads/"):
                ref_type = RefType.LOCAL_BRANCH
            elif ref_name.startswith("refs/remotes/"):
                ref_type = RefType.REMOTE_BRANCH
            elif ref_name.startswith("refs/tags/"):
                ref_type = RefType.TAG
            else:
                ref_type = RefType.LOCAL_BRANCH  # Default
            
            refs.append(GitRef(
                name=ref_name,
                target_hash=target_hash,
                ref_type=ref_type,
                upstream=upstream
            ))
    
    return refs


def resolve_head(repo_path):
    # type: (str) -> Optional[GitRef]
    """
    Resolve HEAD to determine what it points to.
    
    Uses: git symbolic-ref HEAD (or git rev-parse HEAD for detached)
    
    Args:
        repo_path: Path to the Git repository.
        
    Returns:
        GitRef representing HEAD, or None if HEAD doesn't exist.
    """
    # Try to get symbolic reference first
    try:
        returncode, stdout, stderr = run_command(
            ["git", "symbolic-ref", "HEAD"],
            cwd=repo_path,
            check=False
        )
        
        if returncode == 0:
            # HEAD points to a branch
            ref_name = stdout.strip()
            # Get the hash that HEAD ultimately points to
            ret2, hash_out, err2 = run_command(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_path,
                check=False
            )
            target_hash = hash_out.strip() if ret2 == 0 else ""
            
            return GitRef(
                name="HEAD",
                target_hash=target_hash,
                ref_type=RefType.HEAD
            )
        else:
            # Detached HEAD state
            ret2, hash_out, err2 = run_command(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_path,
                check=False
            )
            if ret2 == 0:
                return GitRef(
                    name="HEAD",
                    target_hash=hash_out.strip(),
                    ref_type=RefType.HEAD
                )
    except CommandError:
        pass
    
    return None


def get_head_target_ref(repo_path):
    # type: (str) -> Optional[str]
    """
    Get the reference name that HEAD points to (if not detached).
    
    Args:
        repo_path: Path to the Git repository.
        
    Returns:
        Reference name (e.g., "refs/heads/main") or None if detached.
    """
    try:
        returncode, stdout, stderr = run_command(
            ["git", "symbolic-ref", "HEAD"],
            cwd=repo_path,
            check=False
        )
        if returncode == 0:
            return stdout.strip()
    except CommandError:
        pass
    return None


def ref_exists(repo_path, ref_name):
    # type: (str, str) -> bool
    """
    Check if a reference exists in the repository.
    
    Args:
        repo_path: Path to the Git repository.
        ref_name: Full reference name (e.g., "refs/heads/main").
        
    Returns:
        True if the reference exists, False otherwise.
    """
    try:
        returncode, stdout, stderr = run_command(
            ["git", "show-ref", "--verify", "--quiet", ref_name],
            cwd=repo_path,
            check=False
        )
        return returncode == 0
    except CommandError:
        return False


def read_index_entries(repo_path):
    # type: (str) -> List[IndexEntry]
    """
    Read index (staging area) entries.
    
    Uses: git ls-files --stage
    
    Args:
        repo_path: Path to the Git repository.
        
    Returns:
        List of IndexEntry objects.
    """
    try:
        returncode, stdout, stderr = run_command(
            ["git", "ls-files", "--stage"],
            cwd=repo_path,
            check=False
        )
        
        if returncode != 0:
            return []
        
        entries = []
        for line in stdout.strip().split("\n"):
            if not line:
                continue
            # Format: <mode> <hash> <stage>\t<path>
            parts = line.split("\t", 1)
            if len(parts) == 2:
                meta = parts[0].split()
                path = parts[1]
                if len(meta) >= 3:
                    # mode = meta[0]  # Not used currently
                    obj_hash = meta[1]
                    stage = int(meta[2])
                    entries.append(IndexEntry(
                        hash_value=obj_hash,
                        path=path,
                        stage=stage
                    ))
        
        return entries
    except CommandError:
        return []


def count_objects(repo_path):
    # type: (str) -> int
    """
    Quickly count objects in the repository without reading all details.
    
    Args:
        repo_path: Path to the Git repository.
        
    Returns:
        Number of objects.
    """
    objects = list_all_objects(repo_path)
    return len(objects)


def read_repository(repo_path, include_index=True):
    # type: (str, bool) -> Repository
    """
    Read all data from a Git repository.
    
    This is the main entry point for reading repository data.
    
    Args:
        repo_path: Path to the Git repository.
        include_index: Whether to include index entries.
        
    Returns:
        Repository object with all data populated.
    """
    repo = Repository(repo_path)
    
    # List all objects
    objects = list_all_objects(repo_path)
    
    # Process each object based on type
    for obj_hash, obj_type, obj_size in objects:
        if obj_type == "commit":
            commit = read_commit(repo_path, obj_hash)
            repo.add_commit(commit)
        elif obj_type == "tree":
            tree = read_tree(repo_path, obj_hash)
            repo.add_tree(tree)
        elif obj_type == "blob":
            blob = read_blob_metadata(repo_path, obj_hash, obj_size)
            repo.add_blob(blob)
        elif obj_type == "tag":
            tag = read_tag(repo_path, obj_hash)
            repo.add_tag(tag)
    
    # Read references
    refs = list_references(repo_path)
    for ref in refs:
        repo.add_ref(ref)
    
    # Resolve HEAD
    head = resolve_head(repo_path)
    if head:
        repo.set_head(head)
    
    # Read index if requested
    if include_index:
        index_entries = read_index_entries(repo_path)
        for entry in index_entries:
            repo.add_index_entry(entry)
    
    return repo
