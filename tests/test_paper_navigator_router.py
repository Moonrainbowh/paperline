"""Static contract tests for the lightweight paper-navigator router."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "paper-navigator" / "references" / "router-rules.md"
ROUTER_SKILL = ROOT / "paper-navigator" / "SKILL.md"
LITERATURE_SKILL = ROOT / "literature-research" / "SKILL.md"
JOURNAL_SKILL = ROOT / "journal-navigator" / "SKILL.md"

SKILLS = {
    "literature-research",
    "introduction-writer",
    "methods-writer",
    "results-writer",
    "discussion-writer",
    "abstract-conclusion-writer",
    "manuscript-reviewer",
    "rebuttal-writer",
    "journal-navigator",
}


class PaperNavigatorRouterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = ROUTER.read_text(encoding="utf-8")
        cls.skill_text = ROUTER_SKILL.read_text(encoding="utf-8")
        cls.literature_text = LITERATURE_SKILL.read_text(encoding="utf-8")
        cls.journal_text = JOURNAL_SKILL.read_text(encoding="utf-8")

    def test_all_single_task_routes_are_declared(self):
        cases = {
            "找文献": "literature-research",
            "写引言": "introduction-writer",
            "写方法": "methods-writer",
            "写结果": "results-writer",
            "解释结果": "discussion-writer",
            "写标题、关键词、摘要或结论": "abstract-conclusion-writer",
            "检查全文": "manuscript-reviewer",
            "回复审稿人": "rebuttal-writer",
            "选刊": "journal-navigator",
        }
        for request, skill in cases.items():
            with self.subTest(request=request):
                self.assertIn(request, self.rules)
                self.assertIn(f"`{skill}`", self.rules)

    def test_mixed_task_order_is_declared(self):
        chains = (
            ("找文献，然后写引言", "literature-research", "introduction-writer"),
            ("根据结果写结果和讨论", "results-writer", "discussion-writer"),
            ("检查全文，然后重写摘要", "manuscript-reviewer", "abstract-conclusion-writer"),
            ("有材料和想法，先写初稿再选刊", "manuscript-reviewer", "journal-navigator"),
        )
        for label, first, second in chains:
            with self.subTest(label=label):
                self.assertIn(label, self.rules)
                self.assertIn(f"`{first}` → `{second}`", self.rules)

    def test_router_handles_explicit_skill_and_ambiguous_requests(self):
        self.assertIn("明确写出 `$methods-writer`", self.rules)
        self.assertIn("不能直接按关键词决定", self.rules)
        self.assertIn("章节名、标题或文件名", self.rules)
        self.assertIn("最小必要问题", self.skill_text)

    def test_router_does_not_claim_to_be_a_workflow_state_machine(self):
        self.assertIn("不维护 S0–S7 状态", self.rules)
        self.assertIn("不创建 SHA", self.rules)
        self.assertIn("创建状态机", self.skill_text)

    def test_journal_routing_reuses_one_literature_pool(self):
        self.assertIn("默认采用混合路径", self.rules)
        self.assertIn("literature-evidence.md", self.rules)
        self.assertIn("不重新做一轮相同检索", self.rules)
        self.assertIn("目标期刊 × 研究方向 × Article Type", self.rules)
        self.assertIn("guide 不替代科学文献证据", self.rules)
        self.assertIn("同时供章节写作和 `journal-navigator` 使用", self.literature_text)
        self.assertIn("不从零重复同一轮检索", self.journal_text)
        self.assertIn("交由 `literature-research` 增量补齐", self.journal_text)

    def test_all_specialist_skills_have_skill_metadata(self):
        for skill in SKILLS:
            with self.subTest(skill=skill):
                skill_dir = ROOT / skill
                self.assertTrue((skill_dir / "SKILL.md").is_file())
                self.assertTrue((skill_dir / "agents" / "openai.yaml").is_file())


if __name__ == "__main__":
    unittest.main()
