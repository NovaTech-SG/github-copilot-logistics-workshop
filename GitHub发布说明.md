# 发布一个 GitHub 仓库

发布目标名称：`github-copilot-logistics-workshop`。发布内容为四个案例代码和跟练文档，PPT 在仓库外单独保存。在此目录根部执行命令。
公开仓库地址：https://github.com/YanZhiwei/github-copilot-logistics-workshop

以下保留首次发布步骤，后续更新使用文末命令。

## 首次提交

```powershell
git status --short
git add .
git diff --cached --stat
git commit -m "Initial logistics Copilot workshop"
```

## GitHub 上尚未创建目标仓库

```powershell
gh auth status
gh repo create github-copilot-logistics-workshop --public --source . --remote origin --push
gh repo view --web
```

这会在当前 gh 登录账号下创建公开仓库并上传。发布到组织时使用 `组织名/github-copilot-logistics-workshop`。

## 已在 GitHub 创建了空仓库

不要再运行 repo create。将下面地址替换成目标仓库地址：

```powershell
git remote add origin https://github.com/YanZhiwei/github-copilot-logistics-workshop.git
git push -u origin main
```

如果远端已经有 README 或其他提交，先读取远端历史并处理合并，不要 force push。
上传后在 Actions 查看四个矩阵任务。远程 CI、本机页面和实际 MCP 分别验收。

当前目录内四个应用都是普通文件夹，没有嵌套 Git 仓库，也不需要 Git submodule。
原四个独立仓库及其提交保留在原交付目录中。

## 后续更新

```powershell
git status --short
git add .
git diff --cached --stat
git commit -m "Update workshop materials"
git push
```
