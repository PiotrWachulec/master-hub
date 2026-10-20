"""Behavioral tests against check_evidence.py shipped in a generated hub."""
import ast
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

GENERATOR = Path(__file__).resolve().parents[1] / 'skills/create-knowledge-hub/scripts/create_hub.py'

BRONZE = '''---
type: Źródło
title: Raport kwartalny
description: Transkrypcja raportu.
status: draft
generated:
  by: human:editor
  at: 2026-09-23T12:00:00Z
---
# Raport kwartalny

Przychód wyniósł 42,000 zł w roku 2026. Dyrektor powiedział
„wynik przeszedł oczekiwania”.
'''

SILVER = '''---
type: Koncept
title: Przychód
description: Podsumowanie przychodu.
status: draft
generated:
  by: process:test
  at: 2026-09-23T12:00:00Z
sources:
  - id: raport
    resource: ../00-bronze/source.md
    title: Raport kwartalny
---
# Przychód

Przychód wyniósł 42,000 zł w roku 2026.[^raport] Dyrektor powiedział
„wynik przeszedł oczekiwania”.[^raport]

[^raport]: Raport kwartalny, akapit 1.
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
             '--owner', 'Tester', '--domain', 'Testing'], capture_output=True, text=True)
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
        self.assertIn('## Podejrzenia braku pokrycia (fidelity suspects)', stdout)
        self.assertIn('0 podejrzeń braku pokrycia', stdout)

    def test_value_absent_from_source_is_a_suspect(self):
        self.fixture(silver=SILVER.replace('42,000', '55,000'))
        stdout = self.run_script()
        self.assertIn('55,000', stdout)
        self.assertIn('1 podejrzeń braku pokrycia', stdout)

    def test_fenced_code_values_are_ignored(self):
        silver = SILVER.replace(
            '[^raport]: Raport kwartalny, akapit 1.\n',
            '[^raport]: Raport kwartalny, akapit 1.\n\n```text\nprzykład: 999,999\n```\n',
        )
        self.fixture(silver=silver)
        stdout = self.run_script()
        self.assertNotIn('999,999', stdout)

    def test_status_block_explanation_is_not_checked(self):
        silver = SILVER.replace(
            '[^raport]: Raport kwartalny, akapit 1.\n',
            '[^raport]: Raport kwartalny, akapit 1.\n\n'
            '> **Status: Outdated** (2026-07-18)\n'
            '> Zastąpione raportem z 2026-07-18, nowa wartość to 88,000 zł.\n',
        )
        self.fixture(silver=silver)
        stdout = self.run_script()
        self.assertNotIn('2026-07-18', stdout)
        self.assertNotIn('88,000', stdout)

    def test_document_without_sources_is_reported_as_unverifiable(self):
        silver = SILVER.split('sources:')[0] + '---\n# Przychód\n\nBrak przypisów.\n'
        self.fixture(silver=silver)
        stdout = self.run_script()
        self.assertIn('## Dokumenty bez możliwej weryfikacji', stdout)
        self.assertIn('no sources field', stdout)

    def test_unreferenced_bronze_file_is_listed(self):
        self.fixture()
        orphan = self.hub / 'knowledge/00-bronze/orphan.md'
        orphan.write_text(BRONZE.replace('Raport kwartalny', 'Notatka'), encoding='utf-8')
        stdout = self.run_script()
        self.assertIn('## Nieodwołane źródła bronze', stdout)
        self.assertIn('knowledge/00-bronze/orphan.md', stdout)

    def test_bronze_file_logged_as_no_material_is_not_listed(self):
        self.fixture()
        orphan = self.hub / 'knowledge/00-bronze/orphan.md'
        orphan.write_text(BRONZE.replace('Raport kwartalny', 'Notatka'), encoding='utf-8')
        (self.hub / 'knowledge/log.md').write_text(
            '# Log\n\n## 2026-09-23\n\n- Bez materiału: 00-bronze/orphan.md\n', encoding='utf-8')
        stdout = self.run_script()
        self.assertNotIn('knowledge/00-bronze/orphan.md', stdout)

    def test_ignores_arguments_and_still_succeeds(self):
        self.fixture()
        stdout = self.run_script('unexpected-argument')
        self.assertIn('# Kontrola uziemienia faktów', stdout)

    def test_python_310_syntax(self):
        ast.parse(self.script.read_text(), feature_version=(3, 10))


if __name__ == '__main__':
    unittest.main()
