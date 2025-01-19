# tests.py
import pytest
import os
import shutil
import tempfile
from pathlib import Path

from tool import filesystem_tool

@pytest.fixture
def temp_dir():
    """
    Pytest fixture that creates a temporary directory for file tests,
    then cleans it up afterward.
    """
    old_cwd = os.getcwd()
    temp = tempfile.mkdtemp(prefix="tooltest_")
    os.chdir(temp)
    try:
        yield Path(temp)
    finally:
        os.chdir(old_cwd)
        shutil.rmtree(temp, ignore_errors=True)

def test_list_success(temp_dir):
    # Create subdirectories and files
    (temp_dir / "folderA").mkdir()
    (temp_dir / "folderB").mkdir()
    (temp_dir / "file1.txt").write_text("Hello")
    result = filesystem_tool.invoke({"action": "list", "path": str(temp_dir)})
    assert result["status"] == "success"
    listed = result["result"]
    assert sorted(listed) == ["file1.txt", "folderA", "folderB"]

def test_list_error_not_dir(temp_dir):
    file_path = temp_dir / "some_file"
    file_path.write_text("I'm a file, not a directory")
    result = filesystem_tool.invoke({"action": "list", "path": str(file_path)})
    assert result["status"] == "error"
    assert "not a directory" in result["result"].lower()

def test_list_error_missing_path():
    result = filesystem_tool.invoke({"action": "list"})
    assert result["status"] == "error"
    assert "missing 'path' argument" in result["result"].lower()

def test_search_success(temp_dir):
    (temp_dir / "doc1.pdf").write_text("PDF content")
    (temp_dir / "doc2.PDF").write_text("Another PDF content")
    (temp_dir / "readme.txt").write_text("Readme content")
    result = filesystem_tool.invoke({
        "action": "search",
        "pattern": "*.pdf",
        "search_root": str(temp_dir),
        "include_hidden": False
    })
    assert result["status"] == "success"
    assert len(result["result"]) == 1  # Case-sensitive by default

def test_search_error_missing_args():
    # Missing 'pattern' or 'search_root' => error
    result = filesystem_tool.invoke({"action": "search"})
    assert result["status"] == "error"
    assert "must provide 'pattern' and 'search_root'" in result["result"].lower()

def test_read_success(temp_dir):
    file_path = temp_dir / "readable.txt"
    file_path.write_text("Hello World")
    result = filesystem_tool.invoke({"action": "read", "path": str(file_path)})
    assert result["status"] == "success"
    assert result["result"] == "Hello World"

def test_read_error_not_found(temp_dir):
    result = filesystem_tool.invoke({"action": "read", "path": str(temp_dir / "nonexistent.txt")})
    assert result["status"] == "error"
    assert "does not exist" in result["result"].lower()

def test_read_error_missing_path():
    result = filesystem_tool.invoke({"action": "read"})
    assert result["status"] == "error"
    assert "missing 'path' argument" in result["result"].lower()

def test_write_overwrite(temp_dir):
    file_path = temp_dir / "write.txt"
    file_path.write_text("Original")
    result = filesystem_tool.invoke({
        "action": "write",
        "path": str(file_path),
        "content": "New content",
        "overwrite": True
    })
    assert result["status"] == "success"
    assert file_path.read_text() == "New content"

def test_write_append(temp_dir):
    file_path = temp_dir / "append.txt"
    file_path.write_text("Line1\n")
    result = filesystem_tool.invoke({
        "action": "write",
        "path": str(file_path),
        "content": "Line2\n",
        "overwrite": False
    })
    assert result["status"] == "success"
    assert file_path.read_text() == "Line1\nLine2\n"

def test_write_error_missing_args():
    # No path
    res_no_path = filesystem_tool.invoke({"action": "write", "content": "some data"})
    assert res_no_path["status"] == "error"
    assert "missing 'path' argument" in res_no_path["result"].lower()

def test_grep_success(temp_dir):
    file_path = temp_dir / "sample.log"
    file_path.write_text("Error: Something bad\nInfo: Nothing special\nError: Another problem")
    result = filesystem_tool.invoke({
        "action": "grep",
        "path": str(file_path),
        "search_text": "Error",
        "case_insensitive": False
    })
    assert result["status"] == "success"
    assert len(result["result"]) == 2

def test_grep_case_insensitive(temp_dir):
    file_path = temp_dir / "sample2.log"
    file_path.write_text("error in system\nERROR again\nsome other line")
    result = filesystem_tool.invoke({
        "action": "grep",
        "path": str(file_path),
        "search_text": "ERROR",
        "case_insensitive": True
    })
    assert result["status"] == "success"
    assert len(result["result"]) == 2

def test_grep_error_missing_args():
    # No path
    res = filesystem_tool.invoke({"action": "grep", "search_text": "stuff"})
    assert res["status"] == "error"
    assert "missing 'path' argument" in res["result"].lower()

def test_uuid_success():
    result = filesystem_tool.invoke({"action": "uuid"})
    assert result["status"] == "success"
    assert len(result["result"]) == 36  # UUID length

def test_resolve_success(temp_dir):
    sub_dir = temp_dir / "my_sub"
    sub_dir.mkdir()
    (sub_dir / "target.txt").write_text("some data")
    result = filesystem_tool.invoke({
        "action": "resolve",
        "path": "target.txt",
        "search_root": str(temp_dir),
        "return_first_only": True
    })
    assert result["status"] == "success"
    assert len(result["result"]) == 1
    assert result["result"][0].endswith("target.txt")

def test_resolve_no_results(temp_dir):
    result = filesystem_tool.invoke({
        "action": "resolve",
        "path": "not_found.txt",
        "search_root": str(temp_dir)
    })
    assert result["status"] == "error"
    assert "could not find" in result["result"].lower()

def test_mkdir_success(temp_dir):
    new_dir = temp_dir / "new_folder"
    result = filesystem_tool.invoke({
        "action": "mkdir",
        "path": str(new_dir),
        "exist_ok": True,
        "parents": True
    })
    assert result["status"] == "success"
    assert new_dir.is_dir()

def test_mkdir_missing_path():
    result = filesystem_tool.invoke({"action": "mkdir"})
    assert result["status"] == "error"
    assert "missing 'path' argument" in result["result"].lower()

def test_rmdir_success(temp_dir):
    empty_dir = temp_dir / "empty_dir"
    empty_dir.mkdir()
    result = filesystem_tool.invoke({"action": "rmdir", "path": str(empty_dir)})
    assert result["status"] == "success"
    assert not empty_dir.exists()

def test_rmdir_error_non_empty(temp_dir):
    non_empty_dir = temp_dir / "non_empty"
    non_empty_dir.mkdir()
    (non_empty_dir / "file.txt").write_text("can't remove me if I'm inside")
    result = filesystem_tool.invoke({"action": "rmdir", "path": str(non_empty_dir)})
    assert result["status"] == "error"
    assert "not empty" in result["result"].lower()

def test_remove_file_success(temp_dir):
    file_path = temp_dir / "removable.txt"
    file_path.write_text("Some content")
    result = filesystem_tool.invoke({"action": "remove_file", "path": str(file_path)})
    assert result["status"] == "success"
    assert not file_path.exists()

def test_remove_file_error_dir(temp_dir):
    dir_path = temp_dir / "dir"
    dir_path.mkdir()
    result = filesystem_tool.invoke({"action": "remove_file", "path": str(dir_path)})
    assert result["status"] == "error"
    assert "is a directory" in result["result"].lower()

def test_rename_success(temp_dir):
    original = temp_dir / "orig.txt"
    original.write_text("Renaming test")
    dest = temp_dir / "dest.txt"
    result = filesystem_tool.invoke({
        "action": "rename",
        "path": str(original),
        "dst": str(dest)
    })
    assert result["status"] == "success"
    assert not original.exists()
    assert dest.exists()

def test_rename_missing_args():
    # Missing path
    res = filesystem_tool.invoke({"action": "rename", "dst": "/new/path.txt"})
    assert res["status"] == "error"
    assert "missing 'path' argument" in res["result"].lower()

def test_move_success(temp_dir):
    src_dir = temp_dir / "src"
    src_dir.mkdir()
    file_path = src_dir / "file.txt"
    file_path.write_text("Test move")
    dst_dir = temp_dir / "dst"
    dst_dir.mkdir()
    result = filesystem_tool.invoke({
        "action": "move",
        "src": str(src_dir),
        "dst": str(dst_dir / "src_moved")
    })
    assert result["status"] == "success"
    assert not src_dir.exists()
    assert (dst_dir / "src_moved").exists()

def test_move_missing_args():
    # no src
    res = filesystem_tool.invoke({"action": "move", "dst": "/some/dest"})
    assert res["status"] == "error"
    assert "'src' and 'dst' must be provided" in res["result"].lower()

def test_copy_file(temp_dir):
    file_path = temp_dir / "original.txt"
    file_path.write_text("Copy me")
    new_path = temp_dir / "copy.txt"
    result = filesystem_tool.invoke({
        "action": "copy",
        "src": str(file_path),
        "dst": str(new_path),
        "is_dir": False
    })
    assert result["status"] == "success"
    assert file_path.exists()
    assert new_path.exists()
    assert new_path.read_text() == "Copy me"

def test_copy_dir(temp_dir):
    src_folder = temp_dir / "folder_src"
    src_folder.mkdir()
    (src_folder / "data.txt").write_text("Data in folder")
    dst_folder = temp_dir / "folder_dst"
    result = filesystem_tool.invoke({
        "action": "copy",
        "src": str(src_folder),
        "dst": str(dst_folder),
        "is_dir": True
    })
    assert result["status"] == "success"
    assert src_folder.exists()
    assert dst_folder.exists()
    assert (dst_folder / "data.txt").exists()

def test_copy_missing_args():
    # no src
    res = filesystem_tool.invoke({"action": "copy", "dst": "/some/dest", "is_dir": False})
    assert res["status"] == "error"
    assert "'src' and 'dst' must be provided" in res["result"].lower()

def test_walk_success(temp_dir):
    sub = temp_dir / "sub"
    sub.mkdir()
    (sub / "file.txt").write_text("test")
    result = filesystem_tool.invoke({"action": "walk", "path": str(temp_dir), "include_hidden": False})
    assert result["status"] == "success"
    tree = result["result"]
    assert isinstance(tree, dict)
    assert tree["type"] == "directory"
    assert len(tree["children"]) == 1
    sub_dir = tree["children"][0]
    assert sub_dir["name"] == "sub"
    assert sub_dir["type"] == "directory"

def test_walk_error_not_dir(temp_dir):
    file_path = temp_dir / "not_a_dir.txt"
    file_path.write_text("Hello")
    result = filesystem_tool.invoke({"action": "walk", "path": str(file_path)})
    assert result["status"] == "error"
    assert "not a directory" in result["result"].lower()

def test_walk_error_missing_path():
    result = filesystem_tool.invoke({"action": "walk"})
    assert result["status"] == "error"
    assert "missing 'path' argument" in result["result"].lower()

def test_path_info_success(temp_dir):
    file_path = temp_dir / "info.txt"
    file_path.write_text("some data")
    result = filesystem_tool.invoke({"action": "path_info", "path": str(file_path)})
    assert result["status"] == "success"
    info = result["result"]
    assert info["exists"] is True
    assert info["is_file"] is True
    assert info["is_dir"] is False
    assert info["name"] == "info.txt"
    assert info["suffix"] == ".txt"

def test_path_info_missing_path():
    result = filesystem_tool.invoke({"action": "path_info"})
    assert result["status"] == "error"
    assert "missing 'path' argument" in result["result"].lower()

def test_invalid_action():
    # Provide an unknown action
    result = filesystem_tool.invoke({"action": "invalid_action_name"})
    assert result["status"] == "error"
    assert "unknown action" in result["result"].lower()