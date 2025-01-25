# ---- function_store/filesystem_tool/tool.py ----

import os
import shutil
import uuid
import fnmatch
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool

###############################################################################
# Helper Functions (private)
###############################################################################

def _check_is_directory(dir_path: Path) -> None:
    """Raise an error if 'dir_path' is not an existing directory."""
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory does not exist: {dir_path}")
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {dir_path}")

def _check_is_file(file_path: Path) -> None:
    """Raise an error if 'file_path' is not an existing file."""
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")
    if not file_path.is_file():
        raise IsADirectoryError(f"Path is a directory, not a file: {file_path}")

def _check_path_provided(path_value: Optional[str], action: str) -> None:
    """Raise a clear error if path was not provided but is required for the given action."""
    if not path_value:
        raise ValueError(f"Missing 'path' argument for action '{action}'.")

def _list_directory_contents(directory: Path) -> List[str]:
    """Return a list of file/directory names in the given directory."""
    return [item.name for item in directory.iterdir()]

def _search_files_by_pattern(root_dir: Path, pattern: str, include_hidden: bool) -> List[str]:
    """Recursively find files matching 'pattern' under 'root_dir'; optionally include hidden files."""
    matches = []
    for root, dirs, files in os.walk(root_dir):
        if not include_hidden:
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            files = [f for f in files if not f.startswith(".")]

        for name in files:
            if fnmatch.fnmatch(name, pattern):
                matches.append(str(Path(root) / name))
    return matches

def _read_file_contents(file_path: Path) -> str:
    """Return the entire text content of 'file_path'."""
    return file_path.read_text(encoding="utf-8")

def _write_file_contents(file_path: Path, content: str, overwrite: bool) -> str:
    """
    Write 'content' to 'file_path'. 
    - If overwrite=True, create or overwrite any existing file.
    - If overwrite=False, append to file if it exists; otherwise create it.
    Returns the absolute path as a string.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    mode = "w"
    if file_path.exists() and not overwrite:
        mode = "a"
    
    with file_path.open(mode, encoding="utf-8") as f:
        f.write(content)
    
    return str(file_path)

def _grep_in_file(file_path: Path, search_text: str, case_insensitive: bool) -> List[str]:
    """Return lines from 'file_path' containing 'search_text'; optionally ignore case."""
    matches = []
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            line_cmp = line.lower() if case_insensitive else line
            text_cmp = search_text.lower() if case_insensitive else search_text
            if text_cmp in line_cmp:
                matches.append(line.rstrip("\n"))
    return matches

def _generate_uuid() -> str:
    """Generate and return a new UUID (version 4) as a string."""
    return str(uuid.uuid4())

def _resolve_path(lookup_name: str, root_dir: Path, return_first_only: bool) -> List[str]:
    """
    Recursively search for 'lookup_name' (file or directory) under 'root_dir'.
    Return either the first match or all matches, depending on 'return_first_only'.
    """
    found_paths = []
    for root, dirs, files in os.walk(root_dir):
        for d in dirs:
            if d == lookup_name:
                found_paths.append(str(Path(root) / d))
                if return_first_only:
                    return found_paths
        for f in files:
            if f == lookup_name:
                found_paths.append(str(Path(root) / f))
                if return_first_only:
                    return found_paths
    return found_paths

def _mkdir(dir_path: Path, exist_ok: bool = True, parents: bool = True) -> str:
    """Create a directory, optionally including parent dirs. Returns the path as a string."""
    dir_path.mkdir(exist_ok=exist_ok, parents=parents)
    return str(dir_path)

def _rmdir(dir_path: Path) -> str:
    """
    Remove an empty directory.
    If directory is not empty, an error is raised unless you explicitly remove contents first.
    """
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {dir_path}")
    dir_path.rmdir()
    return f"Removed directory: {dir_path}"

def _remove_file(file_path: Path) -> str:
    """Remove a file if it exists."""
    _check_is_file(file_path)
    file_path.unlink()
    return f"Removed file: {file_path}"

def _rename(src: Path, dst: Path) -> str:
    """Rename or move a file/directory from 'src' to 'dst'."""
    src.rename(dst)
    return f"Renamed/moved from {src} to {dst}"

def _move(src: Path, dst: Path) -> str:
    """
    Move a file/directory from 'src' to 'dst'.
    If 'dst' is an existing directory, 'src' is placed under 'dst'. 
    Overwrites existing files if they have the same name in 'dst'.
    """
    if not src.exists():
        raise FileNotFoundError(f"Source path does not exist: {src}")
    shutil.move(str(src), str(dst))
    return f"Moved {src} to {dst}"

def _copy(src: Path, dst: Path, is_dir: bool) -> str:
    """
    Copy a file or directory from 'src' to 'dst'. 
    If is_dir=True, uses copytree (must not already exist at 'dst').
    If is_dir=False, uses copy2 (overwrites existing file at 'dst').
    """
    if not src.exists():
        raise FileNotFoundError(f"Source path does not exist: {src}")

    if is_dir:
        if dst.exists():
            raise FileExistsError(f"Destination directory '{dst}' already exists. Remove or rename it first.")
        shutil.copytree(str(src), str(dst))
        return f"Copied directory {src} to {dst}"
    else:
        shutil.copy2(str(src), str(dst))
        return f"Copied file {src} to {dst}"

def _walk_directory_tree(root_dir: Path, include_hidden: bool) -> Dict[str, Any]:
    """
    Recursively walk the directory tree starting at 'root_dir'.
    Returns a nested dict with 'name', 'type' (file/directory), and 'children' (for dirs).
    """
    if not root_dir.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root_dir}")
    
    def _walk(path: Path) -> Dict[str, Any]:
        node = {"name": path.name, "type": "directory", "children": []}
        for child in sorted(path.iterdir()):
            if not include_hidden and child.name.startswith("."):
                continue
            if child.is_dir():
                node["children"].append(_walk(child))
            else:
                node["children"].append({"name": child.name, "type": "file"})
        return node
    
    return _walk(root_dir)

def _path_info(path: Path) -> Dict[str, Any]:
    """
    Return metadata about 'path':
      {
        "exists": bool,
        "is_dir": bool,
        "is_file": bool,
        "absolute": str,
        "name": str,
        "stem": str,
        "suffix": str,
      }
    """
    info = {
        "exists": path.exists(),
        "is_dir": path.is_dir() if path.exists() else False,
        "is_file": path.is_file() if path.exists() else False,
        "absolute": str(path.resolve()),
        "name": path.name,
        "stem": path.stem,
        "suffix": path.suffix,
    }
    return info

def _get_pwd() -> str:
    """Return the current working directory."""
    return str(Path.cwd())

###############################################################################
# Primary Function
###############################################################################

@tool
def filesystem_tool(
    action: str,
    path: Optional[str] = None,
    content: Optional[str] = None,
    pattern: Optional[str] = None,
    search_text: Optional[str] = None,
    search_root: Optional[str] = None,
    include_hidden: bool = False,
    case_insensitive: bool = False,
    overwrite: bool = True,
    return_first_only: bool = True,
    src: Optional[str] = None,
    dst: Optional[str] = None,
    is_dir: bool = False,
    exist_ok: bool = True,
    parents: bool = True
) -> Dict[str, Any]:
    """
    A robust, multi-action filesystem tool for local file operations. 
    You must specify an 'action' from the list below, plus the necessary arguments.

    Default Path Behavior:
    - If no path is explicitly specified, the current directory ('./' or '.') is assumed
    - You can use relative paths (e.g., './docs', '../backup') or absolute paths
    - For safety, always confirm before operations that could affect parent directories

    Actions:
    1) "list" => List items in a directory.
       - Required: path (directory to list)
       - Optional: include_hidden (bool) to include hidden items
       Example:
         filesystem_tool(
            action='list',
            path='./docs',
            include_hidden=False
         )

    2) "search" => Search for files by pattern (e.g. '*.pdf') under a root directory.
       - Required: pattern, search_root
       - Optional: include_hidden (bool)
       Example:
         filesystem_tool(
            action='search',
            pattern='*.md',
            search_root='./src',
            include_hidden=True
         )

    3) "read" => Read text content from a file.
       - Required: path (the file path to read)
       Example:
         filesystem_tool(
            action='read',
            path='./docs/notes.txt'
         )

    4) "write" => Write (overwrite or append) text content to a file.
       - Required: path, content
       - Optional: overwrite (bool, default=True)
         If overwrite=True, existing file is overwritten.
         If overwrite=False, content is appended if file exists.
       Example:
         filesystem_tool(
            action='write',
            path='./docs/new.txt',
            content='Hello, World!',
            overwrite=False
         )

    5) "grep" => Return lines containing 'search_text' in a file.
       - Required: path, search_text
       - Optional: case_insensitive (bool)
       Example:
         filesystem_tool(
            action='grep',
            path='./logs/syslog',
            search_text='error',
            case_insensitive=True
         )

    6) "uuid" => Generate a new UUID (version 4).
       - No additional args needed.
       Example:
         filesystem_tool(action='uuid')

    7) "resolve" => Recursively find an exact file/directory name under a search root.
       - Required: path (lookup name), search_root
       - Optional: return_first_only (bool)
       Example:
         filesystem_tool(
            action='resolve',
            path='requirements.txt',
            search_root='.',
            return_first_only=True
         )

    8) "mkdir" => Create a directory.
       - Required: path
       - Optional: exist_ok (bool), parents (bool)
         exist_ok=True => no error if directory already exists
         parents=True => create parent dirs as needed
       Example:
         filesystem_tool(
            action='mkdir',
            path='./my_new_dir',
            exist_ok=True,
            parents=True
         )

    9) "rmdir" => Remove an empty directory.
       - Required: path (must be empty or an error is raised)
       Example:
         filesystem_tool(
            action='rmdir',
            path='./old_dir'
         )

    10) "remove_file" => Remove a single file.
        - Required: path
        Example:
          filesystem_tool(
            action='remove_file',
            path='./some_file.txt'
          )

    11) "rename" => Rename or move a file/directory from 'path' to 'dst'.
        - Required: path (source), dst (destination)
        Example:
          filesystem_tool(
            action='rename',
            path='./draft.doc',
            dst='./final.docx'
          )

    12) "move" => Move a file or directory from 'src' to 'dst'.
        - Required: src, dst
        Example:
          filesystem_tool(
            action='move',
            src='./downloads/old.zip',
            dst='./archive/old_backup.zip'
          )

    13) "copy" => Copy a file or directory from 'src' to 'dst'.
        - Required: src, dst
        - Optional: is_dir (bool) => True if 'src' is a directory
        Example:
          filesystem_tool(
            action='copy',
            src='./docs',
            dst='./backup/docs_copy',
            is_dir=True
          )

    14) "walk" => Return a nested dictionary describing the entire directory tree under 'path'.
        - Required: path (directory)
        - Optional: include_hidden (bool)
        Example:
          filesystem_tool(
            action='walk',
            path='.',
            include_hidden=False
          )

    15) "path_info" => Get metadata about a path (exists, is_file, is_dir, etc.).
        - Required: path
        Example:
          filesystem_tool(
            action='path_info',
            path='./docs/file.txt'
          )

    16) "pwd" => Print working directory (get current directory path).
        - No arguments needed
        Example:
          filesystem_tool(action='pwd')

    Return format for each action:
      {
        "status": "success" or "error",
        "result": <data or error message>
      }

    Usage Notes:
      - Always check the docstring or help text for what arguments are required.
      - If a required argument is missing or invalid, you'll get an "error" with a descriptive message.
      - Be highly highly concrete and concise in your answers, just deliver what's asked.

    Examples of multi-step usage:
      1) "list" a directory, then "move" a file based on the listing.
      2) "search" for all "*.pdf", then "copy" them into a "./PDFs" folder.
      3) "walk" the current directory to visualize structure, then "mkdir" subfolders 
         to reorganize files, and "rename" them consistently.

    Overall: This tool centralizes all filesystem operations in a single function with an 'action' parameter.
    """
    try:
        # --- ACTION HANDLER START ---
        if action == "list":
            _check_path_provided(path, "list")
            dir_path = Path(path)
            _check_is_directory(dir_path)
            items = _list_directory_contents(dir_path)
            if not include_hidden:
                items = [i for i in items if not i.startswith(".")]
            return {"status": "success", "result": items}

        elif action == "search":
            if not pattern or not search_root:
                raise ValueError("For 'search', you must provide 'pattern' and 'search_root'.")
            root_dir = Path(search_root)
            _check_is_directory(root_dir)
            found = _search_files_by_pattern(root_dir, pattern, include_hidden)
            return {"status": "success", "result": found}

        elif action == "read":
            _check_path_provided(path, "read")
            file_path = Path(path)
            _check_is_file(file_path)
            file_content = _read_file_contents(file_path)
            return {"status": "success", "result": file_content}

        elif action == "write":
            _check_path_provided(path, "write")
            if content is None:
                raise ValueError("For 'write' action, 'content' must be provided.")
            file_path = Path(path)
            final_path = _write_file_contents(file_path, content, overwrite)
            mode_label = "overwritten" if overwrite else "appended"
            return {"status": "success", "result": f"File {mode_label} at {final_path}"}

        elif action == "grep":
            _check_path_provided(path, "grep")
            if not search_text:
                raise ValueError("For 'grep' action, 'search_text' must be provided.")
            file_path = Path(path)
            _check_is_file(file_path)
            matches = _grep_in_file(file_path, search_text, case_insensitive)
            return {"status": "success", "result": matches}

        elif action == "uuid":
            new_id = _generate_uuid()
            return {"status": "success", "result": new_id}

        elif action == "resolve":
            if not path or not search_root:
                raise ValueError("For 'resolve' action, provide 'path' and 'search_root'.")
            root_dir = Path(search_root)
            _check_is_directory(root_dir)
            results = _resolve_path(path, root_dir, return_first_only)
            if not results:
                return {"status": "error", "result": f"Could not find '{path}' under '{search_root}'."}
            return {"status": "success", "result": results}

        elif action == "mkdir":
            _check_path_provided(path, "mkdir")
            dir_path = Path(path)
            final_dir = _mkdir(dir_path, exist_ok=exist_ok, parents=parents)
            return {"status": "success", "result": f"Directory created: {final_dir}"}

        elif action == "rmdir":
            _check_path_provided(path, "rmdir")
            dir_path = Path(path)
            msg = _rmdir(dir_path)
            return {"status": "success", "result": msg}

        elif action == "remove_file":
            _check_path_provided(path, "remove_file")
            file_path = Path(path)
            msg = _remove_file(file_path)
            return {"status": "success", "result": msg}

        elif action == "rename":
            _check_path_provided(path, "rename (source)")
            if not dst:
                raise ValueError("For 'rename' action, 'dst' must be provided.")
            src_path = Path(path)
            dst_path = Path(dst)
            msg = _rename(src_path, dst_path)
            return {"status": "success", "result": msg}

        elif action == "move":
            if not src or not dst:
                raise ValueError("For 'move' action, 'src' and 'dst' must be provided.")
            msg = _move(Path(src), Path(dst))
            return {"status": "success", "result": msg}

        elif action == "copy":
            if not src or not dst:
                raise ValueError("For 'copy' action, 'src' and 'dst' must be provided.")
            msg = _copy(Path(src), Path(dst), is_dir=is_dir)
            return {"status": "success", "result": msg}

        elif action == "walk":
            _check_path_provided(path, "walk")
            root_dir = Path(path)
            structure = _walk_directory_tree(root_dir, include_hidden)
            return {"status": "success", "result": structure}

        elif action == "path_info":
            _check_path_provided(path, "path_info")
            info = _path_info(Path(path))
            return {"status": "success", "result": info}

        elif action == "pwd":
            cwd = _get_pwd()
            return {"status": "success", "result": cwd}

        else:
            raise ValueError(
                f"Unknown action: '{action}'. Must be one of: "
                "'list', 'search', 'read', 'write', 'grep', 'uuid', 'resolve', "
                "'mkdir', 'rmdir', 'remove_file', 'rename', 'move', 'copy', 'walk', 'path_info', 'pwd'."
            )
        # --- ACTION HANDLER END ---

    except Exception as e:
        return {"status": "error", "result": str(e)}