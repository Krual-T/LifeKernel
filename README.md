# LifeKernel

## 开源与隐私

本项目包含私有记录（`workspace/records`）。为同时保留私有记录历史并开源代码，采用**双远端**：

- `origin`：私有仓库（包含完整 `workspace/records`）
- `public`：开源仓库（**必须剔除** `workspace/records`）

自动提交仅推送 `origin`。除非明确指令“发布开源/同步 public”，否则禁止推送 `public`。

## 一次性配置（仅第一次需要）

1) 添加 public 远端

```powershell
git remote add public https://github.com/<you>/LifeKernel.git
```

2) 安装 filter-repo（用于生成不含 records 的发布分支）

```powershell
uv add git-filter-repo
```

## 发布开源（每次需要公开时执行）

以下流程会生成一个不含 `workspace/records` 的发布分支并推送到 `public`。

```powershell
# 1) 确保本地是最新的私有主分支
git checkout main
git pull origin main

# 2) 创建/更新发布分支（从私有主分支复制）
git branch -f public-main main

# 3) 在发布分支中移除 records（改写历史）
git checkout public-main
git filter-repo --path workspace/records --invert-paths --force

# 4) 推送到 public
git push public public-main:main --force

# 5) 切回私有主分支继续工作
git checkout main
```

说明：
- `public-main` 是发布用分支，**只用于推送 public**。
- 该流程会重写发布分支历史，不影响私有 `main`。

## 注意事项

- 开源仓库中不会包含任何真实 `workspace/records` 数据。
- 私有记录仍在 `origin` 保持完整历史与变更。
