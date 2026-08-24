# Markdown 转 HTML（商务简约风）

## 脚本位置

- `Convert-MarkdownToHtml.ps1`

## 默认行为

- 默认输入：`03Test/01test-case.md`
- 默认输出：与输入同目录同名 `.html`
- 默认样式：`02Development_Zone/styles/business.css`

## 监控模式

如果你要让 `04AI_Output/` 文件夹里的 Markdown 文档自动转换成 HTML，可以启动脚本的监控模式：

```powershell
python3 .github/hooks/scripts/md_to_html.py --watch
```

后台自动化由 `.github/hooks/scripts/md_to_html.py --watch` 提供，会持续扫描 `04AI_Output/` 下新增或修改的 `.md` 文件并生成同名 `.html`。

## 运行示例

```powershell
pwsh -File ./02Development_Zone/Convert-MarkdownToHtml.ps1
```

```powershell
pwsh -File ./02Development_Zone/Convert-MarkdownToHtml.ps1 -InputFile ./03Test/01test-case.md -OutputFile ./03Test/01test-case.html -Title "数据库开发场景"
```

## 依赖

- `pandoc`

macOS 安装：

```powershell
brew install pandoc
```
