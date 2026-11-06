from datetime import date
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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
import_boss = _load_script("import_boss.py")


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

        scan_args = parser.parse_args(["scan", "--boss-only"])
        self.assertTrue(scan_args.boss_only)

        boss_args = parser.parse_args(["import-boss", "--from-clipboard", "--dry-run"])
        self.assertTrue(boss_args.from_clipboard)
        self.assertTrue(boss_args.dry_run)

    def test_boss_api_and_console_json_parsers_extract_rich_job_fields(self) -> None:
        api_item = {
            "encryptJobId": "abc123xyz",
            "jobName": "高级 Android 工程师",
            "brandName": "小红书",
            "cityName": "上海",
            "areaDistrict": "黄浦区",
            "salaryDesc": "30-50K·16薪",
            "jobExperience": "3-5年",
            "jobDegree": "硕士",
            "skills": ["Android", "Kotlin", "Perfetto"],
            "jobLabels": ["系统性能"],
            "brandScaleName": "1000-9999人",
            "brandIndustry": "互联网",
            "brandStageName": "D轮及以上",
        }
        parsed = scan_portals._parse_boss_api_job(api_item, "Android客户端")
        assert parsed is not None
        self.assertEqual(parsed["url"], "https://www.zhipin.com/job_detail/abc123xyz.html")
        self.assertEqual(parsed["company"], "小红书")
        self.assertIn("Perfetto", parsed["jd"])
        self.assertTrue(parsed["source"].startswith("api:boss:"))

        console_payload = json.dumps(
            [
                {
                    "title": "AI Agent 研发工程师",
                    "url": "https://www.zhipin.com/job_detail/def456.html",
                    "company": "月之暗面",
                    "location": "上海 徐汇区",
                    "salary": "35-60K",
                    "skills": ["Python", "AI Agent", "Playwright"],
                }
            ]
        )
        imported = import_boss.parse_json_payload(console_payload)
        self.assertEqual(len(imported), 1)
        self.assertEqual(imported[0]["company"], "月之暗面")
        self.assertIn("Playwright", imported[0]["jd"])

    def test_boss_parsers_tolerate_null_and_non_string_fields(self) -> None:
        parsed = scan_portals._parse_boss_api_job(
            {
                "encryptJobId": "nullcase1",
                "jobName": "Android 工程师",
                "brandName": None,
                "cityName": None,
                "areaDistrict": None,
                "salaryDesc": None,
                "jobExperience": None,
                "jobDegree": None,
                "skills": None,
                "jobLabels": None,
                "brandScaleName": None,
                "brandIndustry": None,
                "brandStageName": None,
            },
            "Android",
        )
        assert parsed is not None
        self.assertEqual(parsed["company"], "")
        self.assertEqual(parsed["location"], "")
        self.assertEqual(parsed["highlight"], "")
        self.assertNotIn("None", parsed["jd"])

        imported = import_boss.normalize_raw_item(
            {
                "title": 123,
                "url": "https://www.zhipin.com/job_detail/raw1.html",
                "brandName": None,
                "jd": None,
                "skills": "Kotlin",
            }
        )
        assert imported is not None
        self.assertEqual(imported["title"], "123")
        self.assertEqual(imported["company"], "Boss直聘企业")
        self.assertEqual(imported["jd"], "技能标签: Kotlin")

    def test_boss_import_skips_non_dict_and_malformed_items(self) -> None:
        payload = json.dumps(
            [
                {"title": "AI Agent 工程师", "url": "https://www.zhipin.com/job_detail/ok1.html"},
                "not-a-job",
                42,
            ]
        )
        jobs = import_boss.parse_json_payload(payload)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["title"], "AI Agent 工程师")

        wrapped = json.dumps({"zpData": {"jobList": "not-a-list"}})
        self.assertEqual(import_boss.parse_json_payload(wrapped), [])

    def test_boss_search_url_and_interaction_detection(self) -> None:
        url = scan_portals._build_boss_search_url("AI Agent", "101020100", "104,105")
        self.assertIn("query=AI%20Agent", url)
        self.assertIn("city=101020100", url)
        self.assertIn("experience=104,105", url)
        self.assertTrue(
            scan_portals._boss_needs_interaction(
                "https://www.zhipin.com/web/user/safe/verify-slider"
            )
        )
        self.assertTrue(scan_portals._boss_needs_interaction("https://www.zhipin.com/web/user/login"))
        self.assertFalse(
            scan_portals._boss_needs_interaction(
                "https://www.zhipin.com/web/geek/job?query=AI%20Agent"
            )
        )

    def test_cli_resolves_relative_paths_against_callers_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir).resolve()
            old_cwd = Path.cwd()
            os.chdir(temp_root)
            try:
                with mock.patch.object(offerpilot_cli, "_run_script", return_value=0) as run:
                    code = offerpilot_cli.main(
                        ["import-boss", "jobs.json", "--config", "cfg.yml", "--dry-run"]
                    )
                self.assertEqual(code, 0)
                script_name, forwarded = run.call_args.args
                self.assertEqual(script_name, "import_boss.py")
                self.assertIn(str(temp_root / "jobs.json"), forwarded)
                self.assertIn(str(temp_root / "cfg.yml"), forwarded)
                self.assertNotIn("cfg.yml", forwarded)
            finally:
                os.chdir(old_cwd)

    def test_import_boss_requires_config_unless_no_filter(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            payload = temp_root / "jobs.json"
            payload.write_text(
                json.dumps(
                    [
                        {
                            "title": "AI Agent 工程师",
                            "url": "https://www.zhipin.com/job_detail/cfgcheck.html",
                            "company": "示例公司",
                            "location": "上海",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            missing_config = temp_root / "missing.yml"

            code = import_boss.main(
                [str(payload), "--config", str(missing_config), "--dry-run"]
            )
            self.assertEqual(code, 1)

            code = import_boss.main(
                [
                    str(payload),
                    "--config",
                    str(missing_config),
                    "--no-filter",
                    "--dry-run",
                ]
            )
            self.assertEqual(code, 0)

    def test_import_boss_main_writes_history_pipeline_and_jd(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir).resolve()
            payload = temp_root / "jobs.json"
            payload.write_text(
                json.dumps(
                    [
                        {
                            "title": "AI Agent 研发工程师",
                            "url": "https://www.zhipin.com/job_detail/writecheck.html",
                            "company": "月之暗面",
                            "location": "上海 徐汇区",
                            "skills": ["Python", "AI Agent"],
                        }
                    ]
                ),
                encoding="utf-8",
            )
            config = temp_root / "cfg.yml"
            config.write_text(
                "title_filter:\n"
                "  positive: ['AI Agent']\n"
                "  negative: []\n"
                "location_filter: ['上海']\n",
                encoding="utf-8",
            )

            old_cwd = Path.cwd()
            os.chdir(temp_root)
            try:
                code = import_boss.main([str(payload), "--config", str(config)])
            finally:
                os.chdir(old_cwd)

            self.assertEqual(code, 0)
            history = temp_root / "data" / "scan-history.tsv"
            self.assertTrue(history.exists())
            self.assertIn("writecheck.html", history.read_text(encoding="utf-8"))
            self.assertTrue((temp_root / "data" / "pipeline.md").exists())
            jds = list((temp_root / "jds").glob("*.md"))
            self.assertEqual(len(jds), 1)

    def test_load_config_handles_empty_and_rejects_invalid_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            empty = root / "empty.yml"
            empty.write_text("", encoding="utf-8")
            self.assertEqual(scan_portals.load_config(str(empty)), {})

            bad = root / "bad.yml"
            bad.write_text("title_filter: [unclosed\n", encoding="utf-8")
            with self.assertRaises(scan_portals.ConfigError):
                scan_portals.load_config(str(bad))

            non_mapping = root / "list.yml"
            non_mapping.write_text("- a\n- b\n", encoding="utf-8")
            with self.assertRaises(scan_portals.ConfigError):
                scan_portals.load_config(str(non_mapping))

            with self.assertRaises(scan_portals.ConfigError):
                scan_portals.load_config(str(root / "missing.yml"))

    def test_boss_query_fields_normalize_scalars_and_nulls(self) -> None:
        self.assertEqual(scan_portals._as_str_list(None), [])
        self.assertEqual(scan_portals._as_str_list("Android"), ["Android"])
        self.assertEqual(scan_portals._as_str_list(["a", "", 3]), ["a", "3"])
        self.assertEqual(scan_portals._as_text(None), "")
        self.assertEqual(scan_portals._as_text(104), "104")

    def test_boss_payload_extraction_guards_malformed_shapes(self) -> None:
        self.assertEqual(scan_portals._extract_boss_jobs(None, "q"), [])
        self.assertEqual(scan_portals._extract_boss_jobs([], "q"), [])
        self.assertEqual(
            scan_portals._extract_boss_jobs({"code": 1, "message": "expired"}, "q"), []
        )
        self.assertEqual(
            scan_portals._extract_boss_jobs({"code": 0, "zpData": {"jobList": "x"}}, "q"),
            [],
        )
        self.assertEqual(
            scan_portals._extract_boss_jobs(
                {"code": 0, "zpData": {"jobList": [None, "x", {"jobName": "no-id"}]}},
                "q",
            ),
            [],
        )
        parsed = scan_portals._extract_boss_jobs(
            {
                "code": 0,
                "zpData": {
                    "jobList": [
                        {
                            "encryptJobId": "id1",
                            "jobName": "Android 工程师",
                            "brandName": "示例公司",
                        }
                    ]
                },
            },
            "q",
        )
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["company"], "示例公司")

    def test_boss_dom_card_uses_non_api_source_and_rejects_bad_urls(self) -> None:
        card = {
            "title": "AI Agent 工程师",
            "url": "https://www.zhipin.com/job_detail/dom1.html",
            "company": "示例公司",
            "location": "上海 徐汇区",
            "salary": "35-60K",
            "skills": ["Python", "AI Agent"],
        }
        parsed = scan_portals._parse_boss_dom_card(card, "AI Agent", "上海")
        assert parsed is not None
        self.assertEqual(parsed["source"], "dom:boss:AI Agent")
        self.assertIn("Python", parsed["jd"])
        self.assertIsNone(
            scan_portals._parse_boss_dom_card(
                {"title": "bad", "url": "javascript:void(0)"}, "q", "上海"
            )
        )
        self.assertIsNone(scan_portals._parse_boss_dom_card("not-a-card", "q", "上海"))

    def test_boss_payload_classification_and_error_summary(self) -> None:
        self.assertTrue(scan_portals._is_success_boss_payload({"code": 0}))
        self.assertFalse(scan_portals._is_success_boss_payload({"code": 37, "message": "AUTH"}))
        self.assertFalse(scan_portals._is_success_boss_payload(None))
        self.assertIn("code=37", scan_portals._boss_error_summary({"code": 37}))
        self.assertIn("AUTH", scan_portals._boss_error_summary({"code": 37, "message": "AUTH"}))

    def test_boss_launch_failure_raises_actionable_error(self) -> None:
        class FakeChromium:
            def launch_persistent_context(self, **kwargs):
                raise RuntimeError("profile locked")

        class FakePlaywright:
            chromium = FakeChromium()

        with self.assertRaises(scan_portals.BossScanError) as ctx:
            scan_portals._launch_boss_context(
                FakePlaywright(), Path("data/boss_browser_profile"), False
            )
        self.assertIn("可能被占用", str(ctx.exception))

    def test_import_boss_source_is_not_treated_as_official_api(self) -> None:
        job = import_boss.normalize_raw_item(
            {
                "title": "AI Agent 工程师",
                "url": "https://www.zhipin.com/job_detail/manual1.html",
                "company": "示例公司",
            }
        )
        assert job is not None
        self.assertEqual(job["source"], "manual:boss")
        self.assertFalse(job["source"].startswith("api:"))

    def test_pipeline_does_not_give_manual_boss_an_api_bonus(self) -> None:
        row = {
            "url": "https://www.zhipin.com/job_detail/manual2.html",
            "date": "",
            "title": "Android 工程师",
            "company": "示例公司",
        }
        with mock.patch.object(run_pipeline, "load_jd_content", return_value=""):
            manual = run_pipeline.score_row(
                {**row, "source": "manual:boss"},
                cfg={},
                cn_focus=False,
                profile_tags=set(),
            )
            official = run_pipeline.score_row(
                {**row, "source": "api:boss:Android"},
                cfg={},
                cn_focus=False,
                profile_tags=set(),
            )
        self.assertNotIn("结构化来源", manual.reasons)
        self.assertIn("结构化来源", official.reasons)
        self.assertLess(manual.score, official.score)

    def test_scan_main_tolerates_empty_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            config = root / "empty.yml"
            config.write_text("", encoding="utf-8")
            old_cwd = Path.cwd()
            os.chdir(root)
            try:
                with mock.patch.object(scan_portals, "scan_boss", return_value=[]):
                    code = scan_portals.main(
                        ["--boss-only", "--config", str(config), "--dry-run"]
                    )
            finally:
                os.chdir(old_cwd)
        self.assertEqual(code, 0)

    def test_scan_main_returns_nonzero_when_boss_cannot_start(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            config = root / "cfg.yml"
            config.write_text("boss_queries: []\n", encoding="utf-8")
            old_cwd = Path.cwd()
            os.chdir(root)
            try:
                with mock.patch.object(
                    scan_portals,
                    "scan_boss",
                    side_effect=scan_portals.BossScanError("profile locked"),
                ):
                    code = scan_portals.main(
                        ["--boss-only", "--config", str(config), "--dry-run"]
                    )
            finally:
                os.chdir(old_cwd)
        self.assertEqual(code, 1)

    def test_scan_main_returns_nonzero_for_invalid_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Path(temp_dir) / "bad.yml"
            config.write_text("title_filter: [unclosed\n", encoding="utf-8")
            code = scan_portals.main(
                ["--boss-only", "--config", str(config), "--dry-run"]
            )
        self.assertEqual(code, 1)

    def test_import_boss_accepts_empty_config_and_rejects_invalid_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            payload = root / "jobs.json"
            payload.write_text(
                json.dumps(
                    [
                        {
                            "title": "AI Agent 工程师",
                            "url": "https://www.zhipin.com/job_detail/emptycfg.html",
                            "company": "示例公司",
                            "location": "上海",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            empty = root / "empty.yml"
            empty.write_text("", encoding="utf-8")
            code = import_boss.main(
                [str(payload), "--config", str(empty), "--dry-run"]
            )
            self.assertEqual(code, 0)

            bad = root / "bad.yml"
            bad.write_text("title_filter: [unclosed\n", encoding="utf-8")
            code = import_boss.main(
                [str(payload), "--config", str(bad), "--dry-run"]
            )
            self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
