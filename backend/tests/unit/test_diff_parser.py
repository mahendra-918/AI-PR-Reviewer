import pytest
from app.services.diff_parser import parse_diff, DiffHunk, DiffLine


def test_parse_diff_single_file_single_hunk():
    raw_diff = """diff --git a/main.py b/main.py
index e69de29..d95f3ad 100644
--- a/main.py
+++ b/main.py
@@ -1,3 +1,4 @@
 def hello():
-    return False
+    return True
+    pass
"""
    hunks = parse_diff(raw_diff)
    assert len(hunks) == 1
    
    hunk = hunks[0]
    assert hunk.file_path == "main.py"
    assert hunk.language == "py"
    assert hunk.old_start == 1
    assert hunk.new_start == 1
    
    assert len(hunk.lines) == 4
    
    assert hunk.lines[0].content == "def hello():"
    assert hunk.lines[0].change_type == "context"
    assert hunk.lines[0].line_number == 1
    
    assert hunk.lines[1].content == "    return False"
    assert hunk.lines[1].change_type == "removed"
    assert hunk.lines[1].line_number == 2
    
    assert hunk.lines[2].content == "    return True"
    assert hunk.lines[2].change_type == "added"
    assert hunk.lines[2].line_number == 2
    
    assert hunk.lines[3].content == "    pass"
    assert hunk.lines[3].change_type == "added"
    assert hunk.lines[3].line_number == 3


def test_parse_diff_multiple_files_and_hunks():
    raw_diff = """diff --git a/frontend/App.tsx b/frontend/App.tsx
index 1111111..2222222 100644
--- a/frontend/App.tsx
+++ b/frontend/App.tsx
@@ -10,2 +10,3 @@
 const App = () => {
-  return <div />;
+  return <span>Hello</span>;
+};
@@ -20,2 +21,2 @@
 export default App;
-console.log('test')
+console.log('done')
diff --git a/Makefile b/Makefile
index 333..444 100644
--- a/Makefile
+++ b/Makefile
@@ -1,1 +1,2 @@
-run:
+start:
+	python main.py
"""
    hunks = parse_diff(raw_diff)
    assert len(hunks) == 3
    
    # Check first file, first hunk
    h1 = hunks[0]
    assert h1.file_path == "frontend/App.tsx"
    assert h1.language == "tsx"
    assert h1.old_start == 10
    assert h1.new_start == 10
    assert h1.lines[0].change_type == "context"
    assert h1.lines[1].change_type == "removed"
    assert h1.lines[1].line_number == 11
    assert h1.lines[2].change_type == "added"
    assert h1.lines[2].line_number == 11
    assert h1.lines[3].change_type == "added"
    assert h1.lines[3].line_number == 12

    # Check first file, second hunk
    h2 = hunks[1]
    assert h2.file_path == "frontend/App.tsx"
    assert h2.language == "tsx"
    assert h2.old_start == 20
    assert h2.new_start == 21
    
    # Check second file
    h3 = hunks[2]
    assert h3.file_path == "Makefile"
    assert h3.language == "makefile"
    assert h3.lines[0].change_type == "removed"
    assert h3.lines[0].content == "run:"
    assert h3.lines[1].change_type == "added"
    assert h3.lines[1].content == "start:"
    assert h3.lines[2].change_type == "added"
    assert h3.lines[2].content == "\tpython main.py"


def test_parse_diff_deleted_file():
    raw_diff = """diff --git a/obsolete.js b/obsolete.js
deleted file mode 100644
index abc..000
--- a/obsolete.js
+++ /dev/null
@@ -1,2 +0,0 @@
-const x = 1;
-console.log(x);
"""
    hunks = parse_diff(raw_diff)
    assert len(hunks) == 1
    h = hunks[0]
    assert h.file_path == "obsolete.js"
    assert h.language == "js"
    assert len(h.lines) == 2
    assert all(l.change_type == "removed" for l in h.lines)


def test_parse_diff_new_file():
    raw_diff = """diff --git a/new_script.sh b/new_script.sh
new file mode 100755
index 000..abc
--- /dev/null
+++ b/new_script.sh
@@ -0,0 +1,2 @@
+#!/bin/bash
+echo "Hello world"
"""
    hunks = parse_diff(raw_diff)
    assert len(hunks) == 1
    h = hunks[0]
    assert h.file_path == "new_script.sh"
    assert h.language == "sh"
    assert len(h.lines) == 2
    assert all(l.change_type == "added" for l in h.lines)
