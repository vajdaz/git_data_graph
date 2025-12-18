"""
Data model for Git repository objects.

This module defines classes representing Git objects, references, and 
repository structure. Classes are designed for Python 3.6 compatibility.
"""

from enum import Enum
from typing import Dict, List, Optional


class RefType(Enum):
    """Enumeration of Git reference types."""
    LOCAL_BRANCH = "local"
    REMOTE_BRANCH = "remote"
    TAG = "tag"
    HEAD = "head"


class GitObject(object):
    """Base class for Git objects."""
    
    def __init__(self, hash_value):
        # type: (str) -> None
        """
        Initialize a Git object.
        
        Args:
            hash_value: The SHA-1 hash of the object.
        """
        self._hash = hash_value
    
    @property
    def hash(self):
        # type: () -> str
        """Get the full hash of the object."""
        return self._hash
    
    @property
    def short_hash(self):
        # type: () -> str
        """Get the abbreviated hash (7 characters)."""
        return self._hash[:7] if self._hash else ""
    
    def __repr__(self):
        # type: () -> str
        return "{}({})".format(self.__class__.__name__, self.short_hash)
    
    def __eq__(self, other):
        # type: (object) -> bool
        if not isinstance(other, GitObject):
            return False
        return self._hash == other._hash
    
    def __hash__(self):
        # type: () -> int
        return hash(self._hash)


class GitCommit(GitObject):
    """Represents a Git commit object."""
    
    def __init__(self, hash_value, tree_hash, parent_hashes=None, message="", author=""):
        # type: (str, str, Optional[List[str]], str, str) -> None
        """
        Initialize a Git commit.
        
        Args:
            hash_value: The SHA-1 hash of the commit.
            tree_hash: The hash of the tree object this commit points to.
            parent_hashes: List of parent commit hashes.
            message: The commit message (first line).
            author: The commit author.
        """
        super(GitCommit, self).__init__(hash_value)
        self.tree_hash = tree_hash
        self.parent_hashes = parent_hashes if parent_hashes is not None else []
        self.message = message
        self.author = author
    
    def __repr__(self):
        # type: () -> str
        return "GitCommit({}, message='{}')".format(
            self.short_hash, 
            self.message[:20] + "..." if len(self.message) > 20 else self.message
        )


class TreeEntry(object):
    """Represents an entry in a Git tree object."""
    
    def __init__(self, mode, obj_type, hash_value, name):
        # type: (str, str, str, str) -> None
        """
        Initialize a tree entry.
        
        Args:
            mode: File mode (e.g., "100644" for regular file, "040000" for tree).
            obj_type: Object type ("blob" or "tree").
            hash_value: Hash of the referenced object.
            name: Name of the file or directory.
        """
        self.mode = mode
        self.obj_type = obj_type
        self.hash = hash_value
        self.name = name
    
    @property
    def short_hash(self):
        # type: () -> str
        """Get the abbreviated hash (7 characters)."""
        return self.hash[:7] if self.hash else ""
    
    def __repr__(self):
        # type: () -> str
        return "TreeEntry({} {} {})".format(self.mode, self.obj_type, self.name)


class GitTree(GitObject):
    """Represents a Git tree object."""
    
    def __init__(self, hash_value, entries=None):
        # type: (str, Optional[List[TreeEntry]]) -> None
        """
        Initialize a Git tree.
        
        Args:
            hash_value: The SHA-1 hash of the tree.
            entries: List of TreeEntry objects.
        """
        super(GitTree, self).__init__(hash_value)
        self.entries = entries if entries is not None else []
    
    def __repr__(self):
        # type: () -> str
        return "GitTree({}, {} entries)".format(self.short_hash, len(self.entries))


class GitBlob(GitObject):
    """Represents a Git blob object."""
    
    def __init__(self, hash_value, size=0):
        # type: (str, int) -> None
        """
        Initialize a Git blob.
        
        Args:
            hash_value: The SHA-1 hash of the blob.
            size: Size of the blob content in bytes.
        """
        super(GitBlob, self).__init__(hash_value)
        self.size = size
    
    def __repr__(self):
        # type: () -> str
        return "GitBlob({}, {} bytes)".format(self.short_hash, self.size)


class GitTag(GitObject):
    """Represents a Git annotated tag object."""
    
    def __init__(self, hash_value, target_hash, name="", message="", tagger=""):
        # type: (str, str, str, str, str) -> None
        """
        Initialize a Git tag.
        
        Args:
            hash_value: The SHA-1 hash of the tag object.
            target_hash: The hash of the object this tag points to.
            name: The tag name.
            message: The tag message.
            tagger: The tagger identity.
        """
        super(GitTag, self).__init__(hash_value)
        self.target_hash = target_hash
        self.name = name
        self.message = message
        self.tagger = tagger
    
    def __repr__(self):
        # type: () -> str
        return "GitTag({}, name='{}')".format(self.short_hash, self.name)


class GitRef(object):
    """Represents a Git reference (branch, tag ref, or HEAD)."""
    
    def __init__(self, name, target_hash, ref_type):
        # type: (str, str, RefType) -> None
        """
        Initialize a Git reference.
        
        Args:
            name: The full reference name (e.g., "refs/heads/main").
            target_hash: The hash this reference points to.
            ref_type: The type of reference.
        """
        self.name = name
        self.target_hash = target_hash
        self.ref_type = ref_type
    
    @property
    def short_name(self):
        # type: () -> str
        """Get the short reference name (without refs/heads/, refs/remotes/, etc.)."""
        prefixes = [
            "refs/heads/",
            "refs/remotes/",
            "refs/tags/",
        ]
        for prefix in prefixes:
            if self.name.startswith(prefix):
                return self.name[len(prefix):]
        return self.name
    
    @property
    def short_hash(self):
        # type: () -> str
        """Get the abbreviated target hash (7 characters)."""
        return self.target_hash[:7] if self.target_hash else ""
    
    def __repr__(self):
        # type: () -> str
        return "GitRef({} -> {})".format(self.name, self.short_hash)
    
    def __eq__(self, other):
        # type: (object) -> bool
        if not isinstance(other, GitRef):
            return False
        return self.name == other.name and self.target_hash == other.target_hash
    
    def __hash__(self):
        # type: () -> int
        return hash((self.name, self.target_hash))


class IndexEntry(object):
    """Represents an entry in the Git index (staging area)."""
    
    def __init__(self, hash_value, path, stage=0):
        # type: (str, str, int) -> None
        """
        Initialize an index entry.
        
        Args:
            hash_value: The hash of the blob in the index.
            path: The file path.
            stage: The merge stage (0 for normal, 1-3 for conflicts).
        """
        self.hash = hash_value
        self.path = path
        self.stage = stage
    
    @property
    def short_hash(self):
        # type: () -> str
        """Get the abbreviated hash (7 characters)."""
        return self.hash[:7] if self.hash else ""
    
    def __repr__(self):
        # type: () -> str
        return "IndexEntry({} {})".format(self.short_hash, self.path)


class Repository(object):
    """Container for all Git repository data."""
    
    def __init__(self, path):
        # type: (str) -> None
        """
        Initialize a Repository container.
        
        Args:
            path: Path to the Git repository.
        """
        self.path = path
        self.commits = []  # type: List[GitCommit]
        self.trees = []  # type: List[GitTree]
        self.blobs = []  # type: List[GitBlob]
        self.tags = []  # type: List[GitTag]
        self.refs = []  # type: List[GitRef]
        self.index_entries = []  # type: List[IndexEntry]
        self.head = None  # type: Optional[GitRef]
        
        # Internal lookup table for objects by hash
        self._objects_by_hash = {}  # type: Dict[str, GitObject]
    
    def add_commit(self, commit):
        # type: (GitCommit) -> None
        """Add a commit to the repository."""
        self.commits.append(commit)
        self._objects_by_hash[commit.hash] = commit
    
    def add_tree(self, tree):
        # type: (GitTree) -> None
        """Add a tree to the repository."""
        self.trees.append(tree)
        self._objects_by_hash[tree.hash] = tree
    
    def add_blob(self, blob):
        # type: (GitBlob) -> None
        """Add a blob to the repository."""
        self.blobs.append(blob)
        self._objects_by_hash[blob.hash] = blob
    
    def add_tag(self, tag):
        # type: (GitTag) -> None
        """Add a tag object to the repository."""
        self.tags.append(tag)
        self._objects_by_hash[tag.hash] = tag
    
    def add_ref(self, ref):
        # type: (GitRef) -> None
        """Add a reference to the repository."""
        self.refs.append(ref)
    
    def add_index_entry(self, entry):
        # type: (IndexEntry) -> None
        """Add an index entry to the repository."""
        self.index_entries.append(entry)
    
    def set_head(self, head_ref):
        # type: (GitRef) -> None
        """Set the HEAD reference."""
        self.head = head_ref
    
    def get_object_by_hash(self, hash_value):
        # type: (str) -> Optional[GitObject]
        """
        Look up an object by its hash.
        
        Args:
            hash_value: The full or partial hash.
            
        Returns:
            The GitObject, or None if not found.
        """
        # Try exact match first
        if hash_value in self._objects_by_hash:
            return self._objects_by_hash[hash_value]
        
        # Try prefix match (for abbreviated hashes)
        for full_hash, obj in self._objects_by_hash.items():
            if full_hash.startswith(hash_value):
                return obj
        
        return None
    
    @property
    def object_count(self):
        # type: () -> int
        """Get the total number of objects in the repository."""
        return len(self.commits) + len(self.trees) + len(self.blobs) + len(self.tags)
    
    @property
    def all_objects(self):
        # type: () -> List[GitObject]
        """Get all objects in the repository."""
        result = []  # type: List[GitObject]
        result.extend(self.commits)
        result.extend(self.trees)
        result.extend(self.blobs)
        result.extend(self.tags)
        return result
    
    def __repr__(self):
        # type: () -> str
        return "Repository({}, {} objects, {} refs)".format(
            self.path,
            self.object_count,
            len(self.refs)
        )
