# GitHub 仓库维护与发布

公开仓库：[NovaTech-SG/github-copilot-logistics-workshop](https://github.com/NovaTech-SG/github-copilot-logistics-workshop)

本仓库包含四个案例代码和跟练文档，PPT 在仓库外单独保存。
四个应用是普通子目录，每个应用独立管理依赖、规格与练习数据。

## 克隆仓库

```powershell
git clone https://github.com/NovaTech-SG/github-copilot-logistics-workshop.git
cd github-copilot-logistics-workshop
```

准备环境和运行案例时，进入选定应用目录，按其 README 执行。

## 更新已有本地副本的 remote

如果本地副本使用转移前的地址，在仓库根目录执行：

```powershell
git remote set-url origin https://github.com/NovaTech-SG/github-copilot-logistics-workshop.git
git remote -v
git fetch origin
```

## 提交后续更新

在有仓库写权限的账号下操作；先检查自己的改动范围，再暂存和提交。

```powershell
git status --short
git diff
git add .
git diff --cached --stat
git diff --cached --check
git commit -m "Update workshop materials"
git push
```

也可按团队约定推送功能分支并创建 PR。不要强制覆盖远端历史。

## 检查仓库与 CI

```powershell
gh repo view NovaTech-SG/github-copilot-logistics-workshop --json nameWithOwner,url,visibility
gh run list --repo NovaTech-SG/github-copilot-logistics-workshop --limit 5
```

根目录 Workshop CI 分四个矩阵任务运行离线检查，不使用 Databricks 凭据，也不部署服务器。
远程 CI、本机页面和实际 MCP 查询需要分别验收。实际 Token、本地数据库、虚拟环境和 PPT 均不提交。
