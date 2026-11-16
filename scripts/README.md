# scripts/

仓库维护脚本。

| 脚本 | 用途 |
|---|---|
| `check_readme.py` | README 全量校验：进度数字 / 死链 / 边界目录 README 存在性 / 笔记索引完整。**每次 `git commit` 前跑一遍** |

用法：
```bash
python3 scripts/check_readme.py          # 只报告；exit 0 = 干净
python3 scripts/check_readme.py --fix    # 自动修进度数字
```

> 约定：有 ❌ 不许提交。这个脚本用「机器检查」代替「人肉记住 README 要和实际内容保持一致」。