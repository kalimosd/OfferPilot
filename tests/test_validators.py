import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def _load_script(name: str):
    module_path = ROOT / "skill-pack" / "scripts" / name
    module_name = name.replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validate_outputs = _load_script("validate_outputs.py")
validate_aliases = _load_script("validate_aliases.py")
validate_profile_store = _load_script("validate_profile_store.py")


class ValidatorTests(unittest.TestCase):
    def test_validate_outputs_rejects_direct_outputs_root_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "outputs" / "resume.md"
            output.parent.mkdir()
            output.write_text("# Candidate\n", encoding="utf-8")

            errors: list[str] = []
            warnings: list[str] = []
            validate_outputs._check_output_location(output, errors, warnings)

        self.assertIn("saved directly under outputs", errors[0])

    def test_validate_outputs_detects_unresolved_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "outputs" / "resumes" / "候选人A_算法工程师_v1.md"
            output.parent.mkdir(parents=True)
            output.write_text("# 候选人A\n<email>\n", encoding="utf-8")

            errors: list[str] = []
            warnings: list[str] = []
            validate_outputs._check_content(output, errors, warnings)

        self.assertIn("unresolved placeholder", errors[0])

    def test_validate_outputs_warns_for_missing_resume_pdf_pair(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "outputs" / "resumes" / "候选人A_算法工程师_v1.md"
            output.parent.mkdir(parents=True)
            output.write_text("# 候选人A\n", encoding="utf-8")

            warnings: list[str] = []
            validate_outputs._check_markdown_pdf_pairs([output], warnings)

        self.assertIn("without matching PDF", warnings[0])

    def test_validate_aliases_accepts_basic_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            alias_file = Path(temp_dir) / "aliases.json"
            alias_file.write_text(
                json.dumps({"system design": ["系统设计"], "python": ["python3"]}),
                encoding="utf-8",
            )

            errors: list[str] = []
            warnings: list[str] = []
            aliases = json.loads(alias_file.read_text(encoding="utf-8"))
            for key, values in aliases.items():
                self.assertIsInstance(key, str)
                self.assertIsInstance(values, list)
                validate_aliases._record_term(key, key, {}, warnings)

        self.assertEqual(errors, [])

    def test_validate_profile_store_accepts_valid_minimal_profile(self) -> None:
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML is not installed")

        store = {
            "meta": {"name": "候选人A", "birth_year": 1999},
            "experience": [
                {
                    "company": "某公司",
                    "role": "开发工程师",
                    "start": "2024-01",
                    "end": "present",
                    "bullets": [
                        {
                            "text": "设计并实现核心服务",
                            "tags": ["system design", "python"],
                            "impact": "qualitative",
                        }
                    ],
                }
            ],
            "skills": [{"name": "Python", "level": "proficient", "years": 3}],
        }
        aliases = {"system design": ["系统设计"], "python": ["python3"]}
        errors: list[str] = []
        warnings: list[str] = []

        validate_profile_store._validate_store(
            store,
            canonical_tags=set(aliases),
            alias_to_key={"系统设计": "system design", "python3": "python"},
            errors=errors,
            warnings=warnings,
        )

        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_adapters_share_task_documents_and_triggers(self) -> None:
        required_docs = [
            "../../JD_MATCHING.md",
            "../../DATASTORE.md",
            "../../EVALUATION.md",
            "../../MOCK_INTERVIEW.md",
            "../../PRODUCT_RESEARCH.md",
            "../../TRACKER.md",
            "../../OUTREACH.md",
        ]
        required_triggers = [
            "/offerpilot 结构化评估",
            "/offerpilot 模拟面试",
            "/offerpilot 产品研究",
            "/offerpilot 外联消息",
        ]

        for adapter in (ROOT / "skill-pack" / "adapters").glob("*/SKILL.md"):
            text = adapter.read_text(encoding="utf-8")
            for required in required_docs + required_triggers:
                self.assertIn(required, text, msg=f"{required} missing from {adapter}")


if __name__ == "__main__":
    unittest.main()
