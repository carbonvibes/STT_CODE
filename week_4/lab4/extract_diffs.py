"""Extract diffs per commit using pydriller and git diff with algorithms.

Minimal script for lab4. Use `--max-commits` to limit processing during testing.
"""
import argparse
import csv
import os
import subprocess
import tempfile
from typing import Optional

from pydriller import RepositoryMining


def run_git_diff(repo_path: str, old: str, new: str, file_path: str, algorithm: str,
                 ignore_whitespace: bool = True) -> str:
    """Run git diff for a single file between two refs using the specified algorithm."""
    cmd = ["git", "-C", repo_path, "diff", f"--diff-algorithm={algorithm}", old, new, "--", file_path]
    if ignore_whitespace:
        cmd.insert(3, "-w")
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
        count = 0
        for commit in RepositoryMining(repo_path).traverse_commits():
            if max_commits and count >= max_commits:
                break
            parent = commit.parents[0] if commit.parents else None
            for mod in commit.modifications:
                if mod.is_binary:
                    continue
                file_path = mod.new_path or mod.old_path
                if not file_path:
                    continue
                old = parent if parent else commit.hash + "^"
                myers = run_git_diff(repo_path, old, commit.hash, file_path, "myers")
                hist = run_git_diff(repo_path, old, commit.hash, file_path, "histogram")
                writer.writerow({
                    "parent_sha": parent or "",
                    "commit_sha": commit.hash,
                    "file_path": file_path,
                    "old_path": mod.old_path or "",
                    "new_path": mod.new_path or "",
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
