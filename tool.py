import os
import uuid
import fnmatch
from pathlib import Path
from typing import List, Dict, Any, Optional

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
        # If ignoring hidden items, filter them out of iteration
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
    
    # 'append' mode if file exists and overwrite=False
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
    If 'return_first_only' is True, return a single-item list with the first found match.
    Otherwise, return all matches found as a list of absolute paths.
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


###############################################################################
# Primary Function
###############################################################################

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
    return_first_only: bool = True
) -> Dict[str, Any]:
    """
    This function provides a robust set of local filesystem operations, preventing common errors
    by carefully checking required arguments and clarifying usage details. You must specify an
    'action' from the set below, plus any needed arguments.

    Supported actions:
      1. "list"     => List items in a directory.
                      Required arguments:
                        - path (the directory to list)
                      Optional arguments:
                        - include_hidden (bool): If True, include hidden items (default: False).

      2. "search"   => Search for files by a filename pattern under a root directory.
                      Required arguments:
                        - pattern (e.g. '*.pdf')
                        - search_root (the directory to start searching from)
                      Optional arguments:
                        - include_hidden (bool): If True, include hidden directories/files (default: False).

      3. "read"     => Read the text content of a single file.
                      Required arguments:
                        - path (the file path to read).

      4. "write"    => Write or append text content to a file.
                      Required arguments:
                        - path (the file path)
                        - content (string to write)
                      Optional arguments:
                        - overwrite (bool): If True (default), overwrite. If False, append.

      5. "grep"     => Return lines containing 'search_text' from a file.
                      Required arguments:
                        - path (the file path)
                        - search_text (string to match)
                      Optional arguments:
                        - case_insensitive (bool): If True, ignore case (default: False).

      6. "uuid"     => Generate and return a new UUID.

      7. "resolve"  => Recursively search for an exact file or directory name under 'search_root'.
                      Required arguments:
                        - path (the name to look for, e.g. 'myfile.pdf')
                        - search_root (where to begin searching)
                      Optional arguments:
                        - return_first_only (bool): If True, return only the first match (default: True).

    Inputs:
      - action (str, required): One of "list", "search", "read", "write", "grep", "uuid", or "resolve".
      - path (str, sometimes required): The file/directory path or name, depending on action.
      - content (str, optional): Used for "write" action (the content to write or append).
      - pattern (str, optional): Used for "search" action (e.g. "*.pdf").
      - search_text (str, optional): Used for "grep" action.
      - search_root (str, optional): Used for "search" and "resolve" actions (the directory to search).
      - include_hidden (bool, optional): Used for "list" (if you also want hidden files) or "search" (defaults to False).
      - case_insensitive (bool, optional): Used for "grep" (default False).
      - overwrite (bool, optional): Used for "write" action; True => overwrite, False => append (default True).
      - return_first_only (bool, optional): Used for "resolve" action; if True, return only the first match (default True).

    Behavior:
      - Performs the requested filesystem operation.
      - Returns a JSON-like dict with "status" ("success" or "error") and "result" 
        (the requested data or an error description).

    Example Usage (non-Python-style for clarity):
      action: "list", path: "/home/user/docs", include_hidden: false
      => returns items in "/home/user/docs", excluding hidden files

      action: "search", pattern: "*.pdf", search_root: "/home/user", include_hidden: true
      => returns list of all PDF file paths under "/home/user", including hidden directories

      action: "read", path: "/home/user/docs/notes.txt"
      => returns the textual content of "notes.txt"

      action: "write", path: "/home/user/docs/newfile.txt", content: "Hello", overwrite: false
      => appends "Hello" if "newfile.txt" already exists; otherwise creates it

      action: "grep", path: "/var/log/syslog", search_text: "ERROR", case_insensitive: true
      => returns lines with "ERROR" or "error" or "Error" etc. from syslog

      action: "uuid"
      => returns a newly generated UUID

      action: "resolve", path: "report.pdf", search_root: "/home/user/archive", return_first_only: true
      => returns the first match found for "report.pdf" under "/home/user/archive"

    Output:
      A dictionary of the form:
        { "status": "success", "result": ... }   # on success
        { "status": "error",   "result": ... }   # on error

      The "result" field depends on the action:
       - "list", "search", "grep", "resolve": returns a list of strings (file paths or lines).
       - "read": returns a single string (the file contents).
       - "write": returns a string describing where the file was written/appended.
       - "uuid": returns a single string, the generated UUID.

    Notes on Robustness:
      - Mandatory arguments are validated. If any required argument is missing or invalid,
        you receive an "error" status with a descriptive message.
      - Listing a file path instead of a directory raises an error, avoiding confusion.
      - Overwriting vs. appending is controlled via 'overwrite'.
      - Searching or resolving a non-existent path yields an empty result or an error,
        rather than partial success that might mislead the agent.
      - The docstring is structured to help an LLM reason about usage more reliably.
    """
    try:
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
            if not root_dir.exists() or not root_dir.is_dir():
                raise NotADirectoryError(f"Search root is not a valid directory: {search_root}")
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
                raise ValueError("For 'resolve' action, provide 'path' (the lookup name) and 'search_root'.")
            root_dir = Path(search_root)
            if not root_dir.exists() or not root_dir.is_dir():
                raise NotADirectoryError(f"Search root is not a valid directory: {search_root}")
            results = _resolve_path(path, root_dir, return_first_only)
            if not results:
                return {"status": "error", "result": f"Could not find '{path}' under '{search_root}'."}
            return {"status": "success", "result": results}

        else:
            raise ValueError(f"Unknown action: '{action}'. Must be one of: "
                             "'list', 'search', 'read', 'write', 'grep', 'uuid', or 'resolve'.")

    except Exception as e:
        return {"status": "error", "result": str(e)}
