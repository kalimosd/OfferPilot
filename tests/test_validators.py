from datetime import date
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

from offerpilot import cli as offerpilot_cli


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
validate_inputs = _load_script("validate_inputs.py")
run_pipeline = _load_script("run_pipeline.py")
scan_portals = _load_script("scan_portals.py")
check_tracker = _load_script("check_tracker.py")


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
            "../../PROFILE_BUILDER.md",
            "../../JD_MATCHING.md",
            "../../RESUME_DIAGNOSIS.md",
            "../../DATASTORE.md",
            "../../EVALUATION.md",
            "../../OFFER_EVALUATION.md",
            "../../MOCK_INTERVIEW.md",
            "../../PRODUCT_RESEARCH.md",
            "../../TRACKER.md",
            "../../OUTREACH.md",
        ]
        required_triggers = [
            "/offerpilot 建素材库",
            "/offerpilot 结构化评估",
            "/offerpilot 模拟面试",
            "/offerpilot 面经复盘",
            "/offerpilot 行为面",
            "/offerpilot 产品研究",
            "/offerpilot 外联消息",
            "/offerpilot 简历诊断",
            "/offerpilot 求职信",
            "/offerpilot 申请追踪",
            "/offerpilot 批量评估",
            "/offerpilot 谈薪决策",
        ]

        for adapter in (ROOT / "skill-pack" / "adapters").glob("*/SKILL.md"):
            text = adapter.read_text(encoding="utf-8")
            for required in required_docs + required_triggers:
                self.assertIn(required, text, msg=f"{required} missing from {adapter}")

    def test_validate_inputs_accepts_yaml_profile_store(self) -> None:
        self.assertIn(".yaml", validate_inputs.SUPPORTED_EXTENSIONS)
        self.assertIn(".yml", validate_inputs.SUPPORTED_EXTENSIONS)

    def test_pipeline_skill_matching_avoids_substring_false_positives(self) -> None:
        row = {
            "url": "https://example.com/job/1",
            "date": "2026-08-01",
            "source": "greenhouse:test",
            "title": "Android & JavaScript Engineer",
            "company": "TestCorp",
        }
        # 'r' should not match 'android'/'engineer', 'java' should not match 'javascript'
        candidate = run_pipeline.score_row(
            row, cfg={}, cn_focus=False, profile_tags={"r", "java", "c++"}
        )
        self.assertEqual(candidate.skill_hits, 0)

        # Positive boundary check: 'r', 'java', 'c++', and Chinese tags should match properly
        row_positive = {
            "url": "https://example.com/job/2",
            "date": "2026-08-01",
            "source": "greenhouse:test",
            "title": "Senior R / Java / C++ 性能优化 Engineer",
            "company": "TestCorp",
        }
        candidate_pos = run_pipeline.score_row(
            row_positive, cfg={}, cn_focus=False, profile_tags={"r", "java", "c++", "性能优化"}
        )
        self.assertEqual(candidate_pos.skill_hits, 4)

    def test_scan_didi_uses_urllib_without_curl_subprocess(self) -> None:
        import inspect
        source = inspect.getsource(scan_portals.scan_didi)
        self.assertNotIn("subprocess", source)
        self.assertNotIn('"curl"', source)

    def test_validate_outputs_accepts_offer_debrief_and_outreach_filenames(self) -> None:
        for rel_path in (
            "outputs/resumes/候选人A_小米_Offer评估_v1.md",
            "outputs/interview/候选人A_小米_客户端_面经复盘_v1.md",
            "outputs/misc/候选人A_小米_打招呼.md",
        ):
            warnings: list[str] = []
            validate_outputs._check_filename(Path(rel_path), warnings)
            self.assertEqual(warnings, [], msg=f"Unexpected warnings for {rel_path}: {warnings}")

    def test_check_tracker_identifies_overdue_followups_and_skips_malformed_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker_file = Path(temp_dir) / "tracker.tsv"
            tracker_file.write_text(
                "url\tcompany\ttitle\tstatus\tapplied_date\tlast_update\tnotes\n"
                "https://a.com\tCompanyA\tAndroid Eng\tapplied\t2026-08-01\t2026-08-01\t\n"
                "https://b.com\tCompanyB\tAI Eng\tinterviewing\t2026-08-01\t2026-08-04\t\n"
                "https://c.com\tCompanyC\tSystem Eng\toffer_evaluating\t2026-08-01\t2026-08-06\t\n"
                "https://d.com\tCompanyD\tBackend Eng\tapplied\t2026-08-08\t2026-08-08\tFresh\n"
                "malformed_row_with_too_few_columns\n",
                encoding="utf-8",
            )
            counts, followups, skipped = check_tracker.analyze_tracker(
                tracker_file, today=date(2026, 8, 10)
            )

        self.assertEqual(skipped, 1)
        self.assertEqual(counts["applied"], 2)
        self.assertEqual(counts["interviewing"], 1)
        self.assertEqual(counts["offer_evaluating"], 1)
        self.assertEqual(
            [f.company for f in followups],
            ["CompanyA", "CompanyB", "CompanyC"],
        )

    def test_cli_parser_aligns_defaults_and_exposes_pipeline_and_tracker_flags(self) -> None:
        parser = offerpilot_cli._build_parser()
        pdf_args = parser.parse_args(["pdf", "in.md", "out.pdf"])
        self.assertEqual(pdf_args.style, "standard_cn")

        pipe_args = parser.parse_args(
            ["pipeline", "--profile", "custom.yaml", "--max-per-company", "2"]
        )
        self.assertEqual(pipe_args.profile, "custom.yaml")
        self.assertEqual(pipe_args.max_per_company, 2)

        tracker_args = parser.parse_args(["tracker", "--init", "--today", "2026-08-10"])
        self.assertTrue(tracker_args.init)
        self.assertEqual(tracker_args.today, "2026-08-10")


if __name__ == "__main__":
    unittest.main()
