"""Behavioral tests against check_evidence.py shipped in a generated hub."""
import ast
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

GENERATOR = Path(__file__).resolve().parents[1] / 'skills/create-knowledge-hub/scripts/create_hub.py'

BRONZE = '''---
type: Source
title: Quarterly report
description: Report transcript.
status: draft
generated:
  by: human:editor
  at: 2026-09-23T12:00:00Z
---
# Quarterly report

Revenue was $42,000 in 2026. The director said
“the result beat expectations”.
'''

SILVER = '''---
type: Concept
title: Revenue
description: Revenue summary.
status: draft
generated:
  by: process:test
  at: 2026-09-23T12:00:00Z
sources:
  - id: report
    resource: ../00-bronze/source.md
    title: Quarterly report
---
# Revenue

Revenue was $42,000 in 2026.[^report] The director said
“the result beat expectations”.[^report]

[^report]: Quarterly report, paragraph 1.
'''


class CheckEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.hub = self.root / 'hub'
        result = subprocess.run(
            [sys.executable, '-B', str(GENERATOR), '--dest', str(self.hub),
             '--id', 'test', '--title', 'Test', '--kind', 'personal',
             '--owner', 'Tester', '--domain', 'Testing',
             '--hub-category', 'competency'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.script = self.hub / 'scripts/check_evidence.py'
        self.bronze = self.hub / 'knowledge/00-bronze/source.md'
        self.silver = self.hub / 'knowledge/10-silver/concept.md'

    def fixture(self, bronze=BRONZE, silver=SILVER):
        self.bronze.write_text(bronze, encoding='utf-8')
        self.silver.write_text(silver, encoding='utf-8')

    def run_script(self, *args):
        result = subprocess.run([sys.executable, '-B', str(self.script), *args],
                                 cwd=self.root, text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_grounded_claims_produce_no_suspects(self):
        self.fixture()
        stdout = self.run_script()
        self.assertIn('## Fidelity suspects', stdout)
        self.assertIn('0 fidelity suspect(s)', stdout)

    def test_value_absent_from_source_is_a_suspect(self):
        self.fixture(silver=SILVER.replace('42,000', '55,000'))
        stdout = self.run_script()
        self.assertIn('55,000', stdout)
        self.assertIn('1 fidelity suspect(s)', stdout)

    def test_fenced_code_values_are_ignored(self):
        silver = SILVER.replace(
            '[^report]: Quarterly report, paragraph 1.\n',
            '[^report]: Quarterly report, paragraph 1.\n\n```text\nexample: 999,999\n```\n',
        )
        self.fixture(silver=silver)
        stdout = self.run_script()
        self.assertNotIn('999,999', stdout)

    def test_status_block_explanation_is_not_checked(self):
        silver = SILVER.replace(
            '[^report]: Quarterly report, paragraph 1.\n',
            '[^report]: Quarterly report, paragraph 1.\n\n'
            '> **Status: Outdated** (2026-07-18)\n'
            '> Superseded by the 2026-07-18 report, the new value is $88,000.\n',
        )
        self.fixture(silver=silver)
        stdout = self.run_script()
        self.assertNotIn('2026-07-18', stdout)
        self.assertNotIn('88,000', stdout)

    def test_document_without_sources_is_reported_as_unverifiable(self):
        silver = SILVER.split('sources:')[0] + '---\n# Revenue\n\nNo footnotes.\n'
        self.fixture(silver=silver)
        stdout = self.run_script()
        self.assertIn('## Documents without possible verification', stdout)
        self.assertIn('no sources field', stdout)

    def test_unreferenced_bronze_file_is_listed(self):
        self.fixture()
        orphan = self.hub / 'knowledge/00-bronze/orphan.md'
        orphan.write_text(BRONZE.replace('Quarterly report', 'Note'), encoding='utf-8')
        stdout = self.run_script()
        self.assertIn('## Unreferenced bronze sources', stdout)
        self.assertIn('knowledge/00-bronze/orphan.md', stdout)

    def test_bronze_file_logged_as_no_material_is_not_listed(self):
        self.fixture()
        orphan = self.hub / 'knowledge/00-bronze/orphan.md'
        orphan.write_text(BRONZE.replace('Quarterly report', 'Note'), encoding='utf-8')
        (self.hub / 'knowledge/log.md').write_text(
            '# Log\n\n## 2026-09-23\n\n- No material: 00-bronze/orphan.md\n', encoding='utf-8')
        stdout = self.run_script()
        self.assertNotIn('knowledge/00-bronze/orphan.md', stdout)

    def test_ignores_arguments_and_still_succeeds(self):
        self.fixture()
        stdout = self.run_script('unexpected-argument')
        self.assertIn('# Evidence check', stdout)

    def test_python_310_syntax(self):
        ast.parse(self.script.read_text(), feature_version=(3, 10))


if __name__ == '__main__':
    unittest.main()
