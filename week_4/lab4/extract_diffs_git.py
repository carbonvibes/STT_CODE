"""Alternative extractor using installed pydriller API (Repository).

Some environments expose a different API; this script adapts to that.
"""
import argparse
import csv
import os
import subprocess
import tempfile
from typing import Optional

from pydriller.repository import Repository


def run_git_diff(repo_path: str, old: str, new: str, file_path: str, algorithm: str,
                 ignore_whitespace: bool = True) -> str:
    # place -w right after 'diff' when requested
    cmd = ["git", "-C", repo_path, "diff"]
    if ignore_whitespace:
        cmd += ["-w"]
    cmd += [f"--diff-algorithm={algorithm}", old, new, "--", file_path]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        return out.decode(errors='replace')
    except subprocess.CalledProcessError:
        return ""


def ensure_local_repo(repo: str) -> str:
    if os.path.isdir(repo):
        return repo
    tmp = tempfile.mkdtemp(prefix="repo_clone_")
    subprocess.check_call(["git", "clone", repo, tmp])
    return tmp


def extract(repo: str, out_csv: str, max_commits: Optional[int] = None):
    repo_path = ensure_local_repo(repo)
    fieldnames = ["parent_sha", "commit_sha", "file_path", "old_path", "new_path", "commit_message", "diff_myers", "diff_hist"]
    with open(out_csv, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        r = Repository(repo_path)
        count = 0
        for commit in r.traverse_commits():
            if max_commits and count >= max_commits:
                break
            parents = list(commit.parents)
            parent = parents[0] if parents else None
            # Use modified_files for this pydriller version
            mlist = getattr(commit, 'modified_files', None)
            if mlist is None:
                fval = getattr(commit, 'files', None)
                # only use files if it's an iterable of file objects, not an int count
                if isinstance(fval, list):
                    mlist = fval
                else:
                    mlist = []
            for mod in mlist:
                # modified_files elements expose: new_path, old_path, is_binary (maybe), or path
                is_binary = getattr(mod, 'is_binary', False)
                if is_binary:
                    continue
                file_path = getattr(mod, 'new_path', None) or getattr(mod, 'old_path', None) or getattr(mod, 'path', None)
                if not file_path:
                    continue
                old = parent if parent else commit.hash + "^"
                myers = run_git_diff(repo_path, old, commit.hash, file_path, "myers")
                hist = run_git_diff(repo_path, old, commit.hash, file_path, "histogram")
                writer.writerow({
                    "parent_sha": parent or "",
                    "commit_sha": commit.hash,
                    "file_path": file_path,
                    "old_path": getattr(mod, 'old_path', '') or "",
                    "new_path": getattr(mod, 'new_path', '') or "",
                    "commit_message": commit.msg.replace('\n', ' '),
                    "diff_myers": myers,
                    "diff_hist": hist,
                })
            count += 1


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--repo', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--max-commits', type=int)
    args = p.parse_args()
    extract(args.repo, args.out, args.max_commits)
