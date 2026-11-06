import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import yaml

from offerpilot import graph, tools


REPO_ROOT = Path(__file__).resolve().parent.parent


class SkillPackAssetTests(unittest.TestCase):
    def test_default_skill_aliases_file_exists_and_is_valid_json(self) -> None:
        aliases_path = REPO_ROOT / "skill-pack" / "data" / "skill_aliases.zh-en.json"

        aliases = json.loads(aliases_path.read_text(encoding="utf-8"))

        self.assertIn("ai agent", aliases)
        self.assertIn("agentic workflow", aliases["ai agent"])

    def test_profile_store_template_exists_and_is_valid_yaml(self) -> None:
        template_path = REPO_ROOT / "skill-pack" / "templates" / "profile_store.yaml"

        template = yaml.safe_load(template_path.read_text(encoding="utf-8"))

        self.assertIn("experience", template)
        self.assertIn("projects", template)
        self.assertIn("skills", template)


class SkillPackToolTests(unittest.TestCase):
    def test_run_pipeline_tool_reports_subprocess_failure(self) -> None:
        failed = SimpleNamespace(returncode=2, stdout="partial output", stderr="boom")

        with patch("offerpilot.tools.subprocess.run", return_value=failed):
            result = tools.run_pipeline.func()

        self.assertIn("错误：pipeline 运行失败", result)
        self.assertIn("exit code 2", result)
        self.assertIn("boom", result)

    def test_validate_tools_are_exposed_to_agent(self) -> None:
        tool_names = {tool.name for tool in tools.ALL_TOOLS}

        self.assertIn("validate_inputs", tool_names)
        self.assertIn("validate_outputs", tool_names)
        self.assertIn("validate_profile", tool_names)
        self.assertIn("validate_aliases", tool_names)

    def test_agent_system_prompt_and_tracker_statuses_are_synced_with_skill_pack(self) -> None:
        for expected in (
            "profile-build",
            "offer-eval",
            "14-18 条",
            "黄金公式",
            "offer_evaluating",
        ):
            self.assertIn(expected, graph.SYSTEM_PROMPT)

        for status in ("offer_evaluating", "accepted", "declined"):
            self.assertIn(status, tools.VALID_STATUSES)


if __name__ == "__main__":
    unittest.main()
