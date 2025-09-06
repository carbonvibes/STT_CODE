import sys
from pathlib import Path

# Ensure lab4 package dir is on sys.path so we can import local utils module
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import normalize_diff_lines, diffs_equal_sequence


def test_normalize_and_equality():
    a = """--- a/file.py
+++ b/file.py
@@ -1,3 +1,3 @@
-foo  
+foo

-bar
+bar
"""
    b = """--- a/file.py
+++ b/file.py
@@ -1,3 +1,3 @@
-foo
+foo

-bar
+bar
"""
    na = normalize_diff_lines(a)
    nb = normalize_diff_lines(b)
    assert na == nb
    assert diffs_equal_sequence(a, b)
