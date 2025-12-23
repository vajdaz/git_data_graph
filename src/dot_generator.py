"""
DOT language generator for Git repository visualization.

This module converts Git repository data into Graphviz DOT format
with appropriate visual styling for educational purposes.
"""

from typing import List

from .model import (
    Repository, GitCommit, GitTree, GitBlob, GitTag,
    GitRef, RefType, IndexEntry
)
from .git_reader import get_head_target_ref, ref_exists


# Visual styling constants
COLORS = {
    "commit": "#ffff99",      # Yellow
    "tree": "#99ff99",        # Green
    "blob": "#99ccff",        # Blue
    "tag": "#ffcc99",         # Orange
    "ref": "#cccccc",         # Gray
}

SHAPES = {
    "commit": "ellipse",
    "tree": "folder",
    "blob": "cylinder",
    "tag": "note",
    "ref": "box",
}


def escape_dot_string(s):
    # type: (str) -> str
    """
    Escape special characters for DOT labels.
    
    Args:
        s: String to escape.
        
    Returns:
        Escaped string safe for DOT labels.
    """
    # Escape backslashes first, then quotes
    s = s.replace("\\", "\\\\")
    s = s.replace('"', '\\"')
    s = s.replace("\n", "\\n")
    s = s.replace("\r", "")
    # Escape angle brackets for HTML-like labels
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    return s


def escape_html_string(s):
    # type: (str) -> str
    """
    Escape special characters for HTML table labels in DOT.
    
    Args:
        s: String to escape.
        
    Returns:
        Escaped string safe for HTML labels.
    """
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    return s


def generate_header():
    # type: () -> str
    """
    Generate DOT file header.
    
    Returns:
        DOT header string.
    """
    lines = [
        "digraph git_repository {",
        "    // Graph settings",
        "    rankdir=LR;",
        "    node [fontname=\"Helvetica\", fontsize=10];",
        "    edge [fontname=\"Helvetica\", fontsize=9];",
        "",
    ]
    return "\n".join(lines)


def generate_footer():
    # type: () -> str
    """
    Generate DOT file footer.
    
    Returns:
        DOT footer string.
    """
    return "}\n"


def generate_commit_node(commit):
    # type: (GitCommit) -> str
    """
    Generate DOT node for a commit.
    
    Args:
        commit: GitCommit object.
        
    Returns:
        DOT node definition string.
    """
    label = "{}\\n{}".format(
        commit.short_hash,
        escape_dot_string(commit.message[:30]) if commit.message else ""
    )
    return '    "{}" [label="{}", shape={}, style=filled, fillcolor="{}"];'.format(
        commit.hash,
        label,
        SHAPES["commit"],
        COLORS["commit"]
    )


def generate_tree_node(tree):
    # type: (GitTree) -> str
    """
    Generate DOT node for a tree.
    
    Args:
        tree: GitTree object.
        
    Returns:
        DOT node definition string.
    """
    label = "tree\\n{}".format(tree.short_hash)
    return '    "{}" [label="{}", shape={}, style=filled, fillcolor="{}"];'.format(
        tree.hash,
        label,
        SHAPES["tree"],
        COLORS["tree"]
    )


def generate_blob_node(blob):
    # type: (GitBlob) -> str
    """
    Generate DOT node for a blob.
    
    Args:
        blob: GitBlob object.
        
    Returns:
        DOT node definition string.
    """
    label = "blob\\n{}\\n({} bytes)".format(blob.short_hash, blob.size)
    return '    "{}" [label="{}", shape={}, style=filled, fillcolor="{}"];'.format(
        blob.hash,
        label,
        SHAPES["blob"],
        COLORS["blob"]
    )


def generate_tag_node(tag):
    # type: (GitTag) -> str
    """
    Generate DOT node for an annotated tag.
    
    Args:
        tag: GitTag object.
        
    Returns:
        DOT node definition string.
    """
    label = "tag: {}\\n{}".format(
        escape_dot_string(tag.name),
        tag.short_hash
    )
    return '    "{}" [label="{}", shape={}, style=filled, fillcolor="{}"];'.format(
        tag.hash,
        label,
        SHAPES["tag"],
        COLORS["tag"]
    )


def generate_ref_node(ref, is_head_target=False):
    # type: (GitRef, bool) -> str
    """
    Generate DOT node for a reference.
    
    Args:
        ref: GitRef object.
        is_head_target: True if this ref is pointed to by HEAD.
        
    Returns:
        DOT node definition string.
    """
    # Use short name for display
    label = escape_dot_string(ref.short_name)
    
    # Node ID uses the full name to avoid conflicts
    node_id = "ref_" + ref.name.replace("/", "_").replace(".", "_")
    
    style = "filled"
    if is_head_target:
        style = "filled,bold"
    
    return '    "{}" [label="{}", shape={}, style="{}", fillcolor="{}"];'.format(
        node_id,
        label,
        SHAPES["ref"],
        style,
        COLORS["ref"]
    )


def generate_nonexistent_ref_node(ref_name):
    # type: (str) -> str
    """
    Generate DOT node for a non-existing reference (e.g., unborn branch).
    
    This is used when HEAD points to a branch that doesn't exist yet,
    such as in an empty repository.
    
    Args:
        ref_name: Full reference name (e.g., "refs/heads/main").
        
    Returns:
        DOT node definition string with dashed style.
    """
    # Extract short name from full ref name
    prefixes = [
        "refs/heads/",
        "refs/remotes/",
        "refs/tags/",
    ]
    short_name = ref_name
    for prefix in prefixes:
        if ref_name.startswith(prefix):
            short_name = ref_name[len(prefix):]
            break
    
    label = escape_dot_string(short_name)
    
    # Node ID uses the full name to avoid conflicts
    node_id = "ref_" + ref_name.replace("/", "_").replace(".", "_")
    
    # Use dashed style for non-existing references
    return '    "{}" [label="{}", shape={}, style="dashed,bold", fillcolor="{}"];'.format(
        node_id,
        label,
        SHAPES["ref"],
        COLORS["ref"]
    )


def generate_head_node(head):
    # type: (GitRef) -> str
    """
    Generate DOT node for HEAD.
    
    Args:
        head: GitRef representing HEAD.
        
    Returns:
        DOT node definition string.
    """
    return '    "HEAD" [label="HEAD", shape={}, style="filled,bold", fillcolor="{}"];'.format(
        SHAPES["ref"],
        COLORS["ref"]
    )


def generate_commit_edges(commit):
    # type: (GitCommit) -> List[str]
    """
    Generate edges from a commit to its parents and tree.
    
    Args:
        commit: GitCommit object.
        
    Returns:
        List of DOT edge definition strings.
    """
    edges = []
    
    # Edge to tree
    if commit.tree_hash:
        edges.append('    "{}" -> "{}" [color=darkgreen];'.format(
            commit.hash,
            commit.tree_hash
        ))
    
    # Edges to parents
    for parent_hash in commit.parent_hashes:
        edges.append('    "{}" -> "{}" [color=black];'.format(
            commit.hash,
            parent_hash
        ))
    
    return edges


def generate_tree_edges(tree):
    # type: (GitTree) -> List[str]
    """
    Generate edges from a tree to its entries.
    
    Args:
        tree: GitTree object.
        
    Returns:
        List of DOT edge definition strings.
    """
    edges = []
    
    for entry in tree.entries:
        # Add label with entry name
        edges.append('    "{}" -> "{}" [color=darkgreen, label="{}"];'.format(
            tree.hash,
            entry.hash,
            escape_dot_string(entry.name)
        ))
    
    return edges


def generate_tag_edges(tag):
    # type: (GitTag) -> List[str]
    """
    Generate edge from a tag to its target.
    
    Args:
        tag: GitTag object.
        
    Returns:
        List of DOT edge definition strings.
    """
    edges = []
    
    if tag.target_hash:
        edges.append('    "{}" -> "{}" [style=dashed, color=orange];'.format(
            tag.hash,
            tag.target_hash
        ))
    
    return edges


def generate_ref_edges(ref):
    # type: (GitRef) -> List[str]
    """
    Generate edge from a reference to its target.
    
    Args:
        ref: GitRef object.
        
    Returns:
        List of DOT edge definition strings.
    """
    edges = []
    
    node_id = "ref_" + ref.name.replace("/", "_").replace(".", "_")
    
    if ref.target_hash:
        edges.append('    "{}" -> "{}" [style=solid, color=gray];'.format(
            node_id,
            ref.target_hash
        ))
    
    return edges


def generate_upstream_edges(refs):
    # type: (List[GitRef]) -> List[str]
    """
    Generate edges from local branches to their remote tracking branches.
    
    Args:
        refs: List of GitRef objects.
        
    Returns:
        List of DOT edge definition strings.
    """
    edges = []
    
    # Build a set of existing ref names for quick lookup
    existing_refs = set(ref.name for ref in refs)
    
    for ref in refs:
        if ref.ref_type == RefType.LOCAL_BRANCH and ref.upstream:
            # Check if the upstream ref exists in our refs list
            if ref.upstream in existing_refs:
                local_node_id = "ref_" + ref.name.replace("/", "_").replace(".", "_")
                upstream_node_id = "ref_" + ref.upstream.replace("/", "_").replace(".", "_")
                edges.append('    "{}" -> "{}" [style=dashed, color=gray];'.format(
                    local_node_id,
                    upstream_node_id
                ))
    
    return edges


def generate_head_edges(head, head_target_ref_name):
    # type: (GitRef, str) -> List[str]
    """
    Generate edges from HEAD.
    
    Args:
        head: GitRef representing HEAD.
        head_target_ref_name: Name of the ref HEAD points to (or empty if detached).
        
    Returns:
        List of DOT edge definition strings.
    """
    edges = []
    
    if head_target_ref_name:
        # HEAD points to a branch
        target_node_id = "ref_" + head_target_ref_name.replace("/", "_").replace(".", "_")
        edges.append('    "HEAD" -> "{}" [style=bold, color=gray];'.format(
            target_node_id
        ))
    elif head.target_hash:
        # Detached HEAD - points directly to commit
        edges.append('    "HEAD" -> "{}" [style=dotted, color=gray];'.format(
            head.target_hash
        ))
    
    return edges


def generate_index_table(entries):
    # type: (List[IndexEntry]) -> str
    """
    Generate HTML table for index entries.
    
    Args:
        entries: List of IndexEntry objects.
        
    Returns:
        DOT subgraph with HTML table label.
    """
    if not entries:
        return ""
    
    lines = [
        "    // Index table",
        "    subgraph cluster_index {",
        "        label=\"Git Index\";",
        "        style=filled;",
        "        fillcolor=\"#f0f0f0\";",
        "        node [shape=plaintext];",
        "        index_table [label=<",
        "            <TABLE BORDER=\"1\" CELLBORDER=\"1\" CELLSPACING=\"0\" CELLPADDING=\"4\">",
        "                <TR><TD BGCOLOR=\"#dddddd\"><B>Hash</B></TD><TD BGCOLOR=\"#dddddd\"><B>Path</B></TD></TR>",
    ]
    
    for entry in entries:
        lines.append('                <TR><TD>{}</TD><TD>{}</TD></TR>'.format(
            escape_html_string(entry.short_hash),
            escape_html_string(entry.path)
        ))
    
    lines.extend([
        "            </TABLE>",
        "        >];",
        "    }",
    ])
    
    return "\n".join(lines)


def generate_rank_constraints(repo, head_target_ref_name, head_target_exists=True):
    # type: (Repository, str, bool) -> List[str]
    """
    Generate rank constraints to keep object types at the same level.
    
    Args:
        repo: Repository object with all data.
        head_target_ref_name: Name of the ref HEAD points to.
        head_target_exists: Whether the HEAD target reference exists.
        
    Returns:
        List of DOT rank constraint strings.
    """
    parts = []
    
    # Keep all references (branches, tags, HEAD) at the same rank
    ref_node_ids = []
    for ref in repo.refs:
        node_id = "ref_" + ref.name.replace("/", "_").replace(".", "_")
        ref_node_ids.append('"{}"'.format(node_id))
    
    # Include non-existing reference node if HEAD points to unborn branch
    if head_target_ref_name and not head_target_exists:
        node_id = "ref_" + head_target_ref_name.replace("/", "_").replace(".", "_")
        ref_node_ids.append('"{}"'.format(node_id))
    
    if repo.head:
        ref_node_ids.append('"HEAD"')
    
    if ref_node_ids:
        parts.append("    // Rank constraint: references at same level")
        parts.append("    {{ rank=same; {} }}".format("; ".join(ref_node_ids)))
        parts.append("")
    
    # Keep all commits at the same rank
    if repo.commits:
        commit_ids = ['"{}"'.format(c.hash) for c in repo.commits]
        parts.append("    // Rank constraint: commits at same level")
        parts.append("    {{ rank=same; {} }}".format("; ".join(commit_ids)))
        parts.append("")
    
    # Keep all blobs at the same rank
    if repo.blobs:
        blob_ids = ['"{}"'.format(b.hash) for b in repo.blobs]
        parts.append("    // Rank constraint: blobs at same level")
        parts.append("    {{ rank=same; {} }}".format("; ".join(blob_ids)))
        parts.append("")
    
    # Note: Trees are NOT constrained to the same rank because they
    # represent a directory structure with different nesting levels
    
    return parts


def generate_dot(repo, include_index=True, repo_path=None):
    # type: (Repository, bool, str) -> str
    """
    Generate complete DOT source for a repository.
    
    Args:
        repo: Repository object with all data.
        include_index: Whether to include the index table.
        repo_path: Path to the repository (for HEAD resolution).
        
    Returns:
        Complete DOT source string.
    """
    parts = []
    
    # Header
    parts.append(generate_header())
    
    # Determine HEAD target for highlighting
    head_target_ref_name = ""
    head_target_exists = True
    if repo_path:
        head_target_ref_name = get_head_target_ref(repo_path) or ""
        # Check if the HEAD target reference actually exists
        if head_target_ref_name:
            head_target_exists = ref_exists(repo_path, head_target_ref_name)
    
    # Generate nodes section
    parts.append("    // Commit nodes")
    for commit in repo.commits:
        parts.append(generate_commit_node(commit))
    parts.append("")
    
    parts.append("    // Tree nodes")
    for tree in repo.trees:
        parts.append(generate_tree_node(tree))
    parts.append("")
    
    parts.append("    // Blob nodes")
    for blob in repo.blobs:
        parts.append(generate_blob_node(blob))
    parts.append("")
    
    if repo.tags:
        parts.append("    // Tag object nodes")
        for tag in repo.tags:
            parts.append(generate_tag_node(tag))
        parts.append("")
    
    # Reference nodes
    parts.append("    // Reference nodes")
    for ref in repo.refs:
        is_head_target = (ref.name == head_target_ref_name)
        parts.append(generate_ref_node(ref, is_head_target))
    
    # Non-existing reference node (e.g., unborn branch in empty repo)
    if head_target_ref_name and not head_target_exists:
        parts.append(generate_nonexistent_ref_node(head_target_ref_name))
    
    # HEAD node
    if repo.head:
        parts.append(generate_head_node(repo.head))
    parts.append("")
    
    # Add rank constraints to keep object types at same level
    rank_constraints = generate_rank_constraints(repo, head_target_ref_name, head_target_exists)
    parts.extend(rank_constraints)
    
    # Generate edges section
    parts.append("    // Commit edges")
    for commit in repo.commits:
        edges = generate_commit_edges(commit)
        parts.extend(edges)
    parts.append("")
    
    parts.append("    // Tree edges")
    for tree in repo.trees:
        edges = generate_tree_edges(tree)
        parts.extend(edges)
    parts.append("")
    
    if repo.tags:
        parts.append("    // Tag edges")
        for tag in repo.tags:
            edges = generate_tag_edges(tag)
            parts.extend(edges)
        parts.append("")
    
    parts.append("    // Reference edges")
    for ref in repo.refs:
        edges = generate_ref_edges(ref)
        parts.extend(edges)
    
    # Upstream tracking edges (local branch -> remote tracking branch)
    upstream_edges = generate_upstream_edges(repo.refs)
    if upstream_edges:
        parts.append("")
        parts.append("    // Upstream tracking edges")
        parts.extend(upstream_edges)
    
    # HEAD edges
    if repo.head:
        edges = generate_head_edges(repo.head, head_target_ref_name)
        parts.extend(edges)
    parts.append("")
    
    # Index table
    if include_index and repo.index_entries:
        parts.append(generate_index_table(repo.index_entries))
        parts.append("")
    
    # Footer
    parts.append(generate_footer())
    
    return "\n".join(parts)
