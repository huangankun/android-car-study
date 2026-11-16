#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_readme.py — README 全量校验（提交前必跑，机器检查代替人肉记忆）

检查 4 项：
  1. 根 README「当前进度（X/N）」与 ~/.hermes/data/todo/todo.json 的 learn 数组 done/total 一致
  2. 所有 README.md 里的相对链接无死链
  3. 所有含内容文件的目录都有 README.md（内容文件 = .md/.java/.aidl/.py/.sh/.txt/.html/.png/.json/.patch，不含 README 自身）
  4. notes/ 下每个 .md 都被 notes/README.md 提及（索引完整）

用法：
  python3 scripts/check_readme.py          # 只报告；exit 0=干净，1=有问题
  python3 scripts/check_readme.py --fix    # 自动修进度数字（其余需人工修）

约定：每次 git commit 前跑一遍；有 ❌ 不许提交。
"""
import os
import re
import sys
import json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODO = os.path.expanduser("~/.hermes/data/todo/todo.json")

ISSUES = []  # (level, msg)，level: error | warn


def error(msg):
    ISSUES.append(("error", msg))


def warn(msg):
    ISSUES.append(("warn", msg))


def check_progress():
    """检查 1：进度数字。"""
    try:
        data = json.load(open(TODO, encoding="utf-8"))
    except Exception as e:  # todo.json 读不到
        warn(f"读不到 todo.json：{e}")
        return None
    tasks = data.get("learn", [])
    total = len(tasks)
    done = sum(1 for t in tasks if t.get("status") == "done")

    readme = os.path.join(REPO, "README.md")
    txt = open(readme, encoding="utf-8").read()
    m = re.search(r"当前进度\s*（\s*(\d+)\s*/\s*(\d+)\s*）", txt)
    if not m:
        error('根 README 找不到「当前进度（X/N）」字样')
        return (done, total)
    r_done, r_total = int(m.group(1)), int(m.group(2))
    if r_total != total:
        error(f"根 README 进度总数 {r_total} ≠ todo.json 总数 {total}")
    if r_done != done:
        error(f"根 README 进度 done {r_done} ≠ todo.json done {done}")
    return (done, total)


def _find_readmes():
    out = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            if f == "README.md":
                out.append(os.path.join(root, f))
    return out


def check_deadlinks():
    """检查 2：README 相对链接死链。"""
    link_re = re.compile(r"\]\(([^)]+)\)")
    for rp in _find_readmes():
        d = os.path.dirname(rp)
        for m in link_re.finditer(open(rp, encoding="utf-8").read()):
            target = m.group(1).strip().strip("<>")
            if not target or target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target = target.split("#")[0]
            if not target:
                continue
            # 只处理相对路径（./ ../ 或纯文件名/相对子目录）
            if target.startswith(("~", "/")):
                continue
            full = os.path.normpath(os.path.join(d, target))
            if not os.path.exists(full):
                error(f"死链：{os.path.relpath(rp, REPO)} → {target}")


CONTENT_EXT = (".md", ".java", ".aidl", ".py", ".sh", ".txt",
               ".html", ".png", ".json", ".patch", ".ini", ".xml")


def check_dir_readme():
    """检查 3：边界目录要有 README。

    只查「边界目录」，不查实验证据叶子目录（experiments/*/ 由父级 experiments/README.md 索引）：
      a) REPO 直接子目录（notes/ experiments/ articles/ traces/ scripts/ ...）
      b) notes/ 的直接子目录（按周/主题拆分：dumpsys/ w1d3/ w2d3/ ...）
      c) 名为 src 的源码归档目录
    """
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d != ".git"]
        rel = os.path.relpath(root, REPO)
        if rel == ".":
            continue
        parts = rel.split(os.sep)
        parent = parts[0] if parts else ""
        base = parts[-1]
        require = (len(parts) == 1) or (parent == "notes" and len(parts) == 2) or (base == "src")
        if not require:
            continue
        content = [f for f in files
                   if f != "README.md" and f.lower().endswith(CONTENT_EXT)
                   and not f.startswith(".")]
        if content and "README.md" not in files:
            error(f"目录缺 README.md：{rel}/（含 {len(content)} 个内容文件）")


def check_notes_index():
    """检查 4：notes/ 每个 .md 都要被 notes/README.md 提及。"""
    notes = os.path.join(REPO, "notes")
    index = os.path.join(notes, "README.md")
    if not os.path.exists(index):
        warn("notes/README.md 不存在")
        return
    idx_txt = open(index, encoding="utf-8").read()
    for f in sorted(os.listdir(notes)):
        if f.endswith(".md") and f != "README.md":
            if f not in idx_txt:
                warn(f"notes/{f} 未被 notes/README.md 提及")
    # 子目录索引（notes/*/README.md 提及各自子目录里的 .md）
    for sub in sorted(os.listdir(notes)):
        subdir = os.path.join(notes, sub)
        if not os.path.isdir(subdir):
            continue
        subidx = os.path.join(subdir, "README.md")
        if not os.path.exists(subidx):
            continue
        s_txt = open(subidx, encoding="utf-8").read()
        for f in sorted(os.listdir(subdir)):
            if f.endswith(".md") and f != "README.md":
                if f not in s_txt:
                    warn(f"notes/{sub}/{f} 未被 notes/{sub}/README.md 提及")


def fix_progress(done, total):
    readme = os.path.join(REPO, "README.md")
    txt = open(readme, encoding="utf-8").read()
    new = re.sub(r"当前进度\s*（\s*\d+\s*/\s*\d+\s*）",
                 f"当前进度（{done}/{total}）", txt)
    if new != txt:
        open(readme, "w", encoding="utf-8").write(new)
        print(f"→ 已自动修正根 README 进度为 {done}/{total}")


def main():
    fix = "--fix" in sys.argv
    done_total = check_progress()
    check_deadlinks()
    check_dir_readme()
    check_notes_index()

    errors = [m for lvl, m in ISSUES if lvl == "error"]
    warns = [m for lvl, m in ISSUES if lvl == "warn"]

    if not ISSUES:
        print("✅ README 全量校验通过：进度一致 · 无死链 · 目录 README 齐全 · 笔记索引完整")
        return 0

    for m in errors:
        print("❌ " + m)
    for m in warns:
        print("⚠️  " + m)

    if fix and done_total:
        fix_progress(done_total[0], done_total[1])

    return 1


if __name__ == "__main__":
    sys.exit(main())