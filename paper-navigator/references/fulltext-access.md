# 全文获取

完成文献发现后，如果用户需要合法获取全文、出版社 PDF 或建立经过验证的本地论文语料库，请使用本文件。

## 合法获取阶梯

1. 规范化 DOI 或稳定的论文网址，并核验核心元数据。
2. 优先从出版社、文献库、预印本平台或作者存档中获取合法的开放获取版本。
3. 对于出版社的非开放内容，使用用户已获授权的机构访问权限。
4. 如果已安装 `$instsci`，读取其当前版本的 `SKILL.md`，并将出版社全文获取任务交给它执行。不要在此复制或重构 InstSci 的实施规则。
5. 如果 InstSci 不可用，应如实报告能力缺失，并提供合法替代途径，例如机构图书馆、作者稿、文献库或文献传递服务。

## 与 InstSci 的任务交接

将 Paper Navigator 作为流程编排者，将 InstSci 作为全文获取执行者：

- 传递规范化后的 DOI 或 DOI 文件。
- 传递用户明确指定或已经配置的订阅机构；绝不能自行假定用户所属学校。
- 保持 InstSci 的可见浏览器可供使用，以便完成 SSO、双重验证（2FA）、验证码（CAPTCHA）、Cloudflare 检查及出版社验证。
- 由用户自行输入凭据和验证码。绝不索取、存储或重放这些信息。
- 遵循 InstSci 自身的证据标签和当前出版社工作流，不要重复编写可能随版本变化的命令。

## 验证质量门

将论文标记为 `PDF verified`（PDF 已验证）之前，必须满足：

- PDF 非空且具有有效的 PDF 文件签名；
- 从提取文本或可靠元数据中确认 DOI 或标题匹配；
- 通过目视检查确认文档能够正常渲染，且不是错误页面；
- 具有稳定的本地路径，并在可行时记录文件大小和 SHA-256；
- 明确区分自动化获取与人工浏览器恢复这两类过程。

不能仅凭 DOI 解析成功、HTTP 状态、Cookie、日志、出版社页面或已经打开的 PDF 查看器，推断全文获取成功。

## 获取报告

按以下格式记录每一项：

```text
出版社：
DOI：
获取路线：
路线状态：
执行器原始状态（如有）：
机构：
本地路径：
PDF核验状态：
核验证据：
下一步行动：
```

不要用一个“结果”字段混合获取路线和 PDF 质量。统一使用以下三个维度：

- **获取路线**：`OA-publisher`、`OA-repository`、`author-archive`、`institution-authorized`、`user-provided-local`、`document-delivery` 或 `not-found`。
- **路线状态**：`not-attempted`、`route-found`、`auth_required`、`acquired`、`blocked`、`unsupported` 或 `missing`。打开浏览器或 PDF 查看器只说明路线动作，不改变核验状态。
- **PDF核验状态**：`not-checked`、`verification-failed` 或 `PDF verified`。只有完整通过上方验证质量门才能使用 `PDF verified`。

调用 InstSci 或其他执行器时，原样保留它返回的 `HTTP preflight` 等当前证据标签到“执行器原始状态”，再映射到上述字段；不要覆盖或擅自改写执行器状态。禁止使用含义不清的 `browser verified` 作为 PDF 核验结论。

## 后续交接

PDF 验证通过后，按需转入：

- `paper-reading.md`：制作以原始来源为依据的阅读卡片；
- `citation-support.md`：提供主张级证据支持；
- `literature-discovery.md`：继续补足检索覆盖范围或完成筛选。
