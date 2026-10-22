"""Behavioral tests against the validator shipped in an independently generated hub."""
import json
import ast
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

GENERATOR = Path(__file__).resolve().parents[1] / 'skills/create-knowledge-hub/scripts/create_hub.py'

DOCUMENT = '''---
type: Concept
title: Test knowledge
description: Example for checking the structure.
status: draft
doc_key: 11111111-1111-4111-8111-111111111111
generated:
  by: process:test
  at: 2026-09-23T12:00:00Z
sources:
  - id: input
    resource: ../00-bronze/source.txt
    title: Source material
---
# Concept

Claim.[^input]

[^input]: Material excerpt.

[Source](../00-bronze/source.txt)
'''

EXTERNAL_REF_BLOCK = (
    'external_refs:\n'
    '  - id: ext-ref\n'
    '    hub: 33333333-3333-4333-8333-333333333333\n'
    '    doc: 44444444-4444-4444-8444-444444444444\n'
    '    classification: Internal\n'
    '    operation: cite\n'
    '    note: "Cited from a competency hub."\n'
)

DOCUMENT_WITH_EXTERNAL_REF = (
    DOCUMENT.replace('    title: Source material\n---\n',
                     '    title: Source material\n' + EXTERNAL_REF_BLOCK + '---\n')
            .replace('[Source](../00-bronze/source.txt)\n',
                     '[Source](../00-bronze/source.txt)\n\n'
                     'External claim.[^ext-ref]\n\n[^ext-ref]: External detail.\n')
)


class ValidateHubTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.hub = self.root / 'hub with spaces'
        result = subprocess.run(
            [sys.executable, '-B', str(GENERATOR), '--dest', str(self.hub),
             '--id', 'test', '--title', 'Test', '--kind', 'personal',
             '--owner', 'Tester', '--domain', 'Testing',
             '--hub-category', 'competency'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.script = self.hub / 'scripts/validate_hub.py'
        self.doc = self.hub / 'knowledge/10-silver/concept.md'

    def fixture(self, text=DOCUMENT, path=None):
        (self.hub / 'knowledge/00-bronze/source.txt').write_text('Source text\n', encoding='utf-8')
        (path or self.doc).write_text(text, encoding='utf-8')

    def validate(self, good=True, contains=None):
        result = subprocess.run([sys.executable, '-B', str(self.script)],
                                cwd=self.root, text=True, capture_output=True, timeout=10)
        try:
            report = json.loads(result.stdout)
        except ValueError:
            self.fail(f'No JSON report: {result.stdout}\n{result.stderr}')
        self.assertEqual(set(report), {'violations', 'errors', 'warnings'})
        self.assertEqual(report['violations'], len(report['errors']))
        self.assertEqual(result.returncode, 0 if good else 1, result.stderr)
        self.assertEqual(report['violations'] == 0, good, report)
        for item in report['errors'] + report['warnings']:
            self.assertEqual(set(item), {'file', 'line', 'message'})
            self.assertGreaterEqual(item['line'], 1)
            self.assertIn(f"{item['file']}:{item['line']}:", result.stderr)
        if contains:
            self.assertIn(contains, result.stderr)
        return report

    def config(self, transform):
        path = self.hub / 'hub.json'
        data = json.loads(path.read_text())
        transform(data)
        path.write_text(json.dumps(data), encoding='utf-8')

    def test_empty_generated_hub_is_valid_and_portable(self):
        report = self.validate()
        self.assertEqual(report, {'violations': 0, 'errors': [], 'warnings': []})
        self.assertEqual(json.loads((self.hub / 'hub.json').read_text())['quality'], {
            'validator': 'scripts/validate_hub.py', 'metric': 'violations',
            'threshold': 0, 'max_fix_iterations': 5,
            'evidence_script': 'scripts/check_evidence.py'})

    def test_valid_document_and_log(self):
        self.fixture()
        (self.hub / 'knowledge/log.md').write_text(
            '# Log\n\n## 2026-09-23\n\nAdded a concept.\n\n## 2026-09-22\n\nOlder entry.\n')
        self.validate()

    def test_remote_copy_policy_is_required_and_strict(self):
        config_path = self.hub / 'hub.json'
        original = config_path.read_text(encoding='utf-8')
        changes = [lambda c: c.pop('policy'),
                   lambda c: c['policy'].pop('remote_copy')]
        for value in (None, [], True, 'required_after_validated_task'):
            changes.append(lambda c, value=value: c.update(policy=value))
        for value in (None, '', 'disabled', 'optional', True, [], {},
                      ['required_after_validated_task']):
            changes.append(lambda c, value=value: c['policy'].update(remote_copy=value))
        for number, change in enumerate(changes):
            with self.subTest(case=number):
                config_path.write_text(original, encoding='utf-8')
                self.config(change)
                report = self.validate(False, 'policy.remote_copy')
                self.assertEqual(report['violations'], 1)
                self.assertEqual(report['errors'][0]['file'], 'hub.json')
        config_path.write_text(original, encoding='utf-8')
        self.validate()

    def test_content_review_policy_is_required_and_strict(self):
        config_path = self.hub / 'hub.json'
        original = config_path.read_text(encoding='utf-8')
        changes = [lambda c: c['policy'].pop('content_review')]
        for value in (None, '', 'disabled', 'optional', True, [], {},
                      ['direct'], 'Direct', 'required-pr'):
            changes.append(lambda c, value=value: c['policy'].update(content_review=value))
        for number, change in enumerate(changes):
            with self.subTest(case=number):
                config_path.write_text(original, encoding='utf-8')
                self.config(change)
                report = self.validate(False, 'policy.content_review')
                self.assertEqual(report['violations'], 1)
                self.assertEqual(report['errors'][0]['file'], 'hub.json')
        for value in ('direct', 'required_pr'):
            config_path.write_text(original, encoding='utf-8')
            self.config(lambda c, value=value: c['policy'].update(content_review=value))
            self.validate()
        config_path.write_text(original, encoding='utf-8')
        self.validate()

    def test_hub_key_must_be_a_uuid(self):
        for value in (None, '', 'not-a-uuid', 123, [], {},
                      '11111111-1111-4111-8111-11111111111'):
            with self.subTest(value=value):
                self.config(lambda c, value=value: c.update(hub_key=value))
                report = self.validate(False, 'hub_key must be a UUID')
                self.assertEqual(report['violations'], 1)
        self.config(lambda c: c.pop('hub_key'))
        self.validate(False, 'hub_key must be a UUID')
        self.config(lambda c: c.update(hub_key='11111111-1111-4111-8111-111111111111'))
        self.validate()

    def test_hub_category_is_required_and_strict(self):
        for value in (None, '', 'client', 'Competency', 123, [], {}):
            with self.subTest(value=value):
                self.config(lambda c, value=value: c.update(hub_category=value))
                report = self.validate(False, 'hub_category must be')
                self.assertEqual(report['violations'], 1)
        self.config(lambda c: c.pop('hub_category'))
        self.validate(False, 'hub_category must be')
        for value in ('competency', 'initiative'):
            self.config(lambda c, value=value: c.update(hub_category=value))
            self.validate()

    def test_default_classification_is_required_and_strict(self):
        for value in (None, '', 'secret', 'Top Secret', 123, [], {}):
            with self.subTest(value=value):
                self.config(lambda c, value=value: c.update(default_classification=value))
                report = self.validate(False, 'default_classification must be')
                self.assertEqual(report['violations'], 1)
        self.config(lambda c: c.pop('default_classification'))
        self.validate(False, 'default_classification must be')
        for value in ('Public', 'Internal', 'Confidential', 'Secret'):
            self.config(lambda c, value=value: c.update(default_classification=value))
            self.validate()

    def test_profile_version_requires_explicit_upgrade(self):
        for version in ('0.3.0', '0.2.2', '0.2.1', '0.2.0', '0.1.1', '0.4.0', None, 0.4):
            with self.subTest(version=version):
                self.config(lambda c: c.update(profile_version=version))
                self.validate(False, 'implements profile 0.5.0')
        self.config(lambda c: c.pop('profile_version'))
        self.validate(False, 'implements profile 0.5.0')

    def test_invalid_remote_copy_policy_does_not_skip_documents(self):
        self.config(lambda c: c['policy'].pop('remote_copy'))
        self.fixture('# Missing metadata\n')
        report = self.validate(False, 'policy.remote_copy')
        self.assertTrue(any(e['file'] == 'knowledge/10-silver/concept.md'
                            and e['message'] == 'Missing frontmatter'
                            for e in report['errors']))

    def test_nested_index_and_log_require_metadata(self):
        for layer in ('00-bronze', '10-silver', '20-gold', '90-decisions', 'custom'):
            for name in ('index.md', 'log.md'):
                with self.subTest(layer=layer, name=name):
                    path = self.hub / 'knowledge' / layer / 'product' / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text('# Document without metadata\n', encoding='utf-8')
                    report = self.validate(False, 'Missing frontmatter')
                    self.assertTrue(all(e['file'] == path.relative_to(self.hub).as_posix()
                                        for e in report['errors']))
                    path.unlink()

    def test_non_scaffold_index_and_layer_log_are_not_exempt(self):
        for relative in ('custom/index.md', '00-bronze/log.md', '10-silver/log.md',
                         '20-gold/log.md', '90-decisions/log.md'):
            with self.subTest(relative=relative):
                path = self.hub / 'knowledge' / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('# Log\n\n## 2026-09-23\n\nContent.\n', encoding='utf-8')
                self.validate(False, 'Missing frontmatter')
                path.unlink()

    def test_nested_index_and_log_require_sources_in_silver_and_gold(self):
        text = DOCUMENT.split('sources:')[0] + '---\n# Product\n'
        for layer in ('10-silver', '20-gold'):
            for name in ('index.md', 'log.md'):
                with self.subTest(layer=layer, name=name):
                    path = self.hub / 'knowledge' / layer / 'product' / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    self.fixture(text, path)
                    report = self.validate(False, 'requires nonempty sources')
                    self.assertEqual(report['violations'], 1)
                    path.unlink()

    def test_valid_nested_index_and_log_keep_source_and_link_checks(self):
        text = DOCUMENT.replace('../00-bronze/', '../../00-bronze/')
        for layer in ('10-silver', '20-gold'):
            for name in ('index.md', 'log.md'):
                with self.subTest(layer=layer, name=name):
                    path = self.hub / 'knowledge' / layer / 'product' / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    self.fixture(text, path)
                    self.validate()
                    self.fixture(text.replace('resource: ../../00-bronze/source.txt',
                                              'resource: ../../00-bronze/missing.txt'), path)
                    self.validate(False, 'does not exist')
                    self.fixture(text + '\n[Missing](missing.md)\n', path)
                    self.validate(False, 'does not exist')
                    self.fixture(text.replace('[^input]: Material excerpt.', ''), path)
                    self.validate(False, 'Missing footnote definition')
                    path.unlink()

    def test_navigation_indexes_still_check_links_and_declared_sources(self):
        for relative in ('index.md', '00-bronze/index.md', '10-silver/index.md',
                         '20-gold/index.md', '90-decisions/index.md'):
            with self.subTest(relative=relative):
                path = self.hub / 'knowledge' / relative
                original = path.read_text(encoding='utf-8')
                path.write_text(original + '\n[Missing](missing.md)\n', encoding='utf-8')
                self.validate(False, 'does not exist')
                path.write_text('---\nokf_version: "0.2"\nsources:\n'
                                '  - id: missing\n    resource: missing.txt\n---\n'
                                'Description.[^missing]\n\n[^missing]: Source.\n', encoding='utf-8')
                self.validate(False, 'does not exist')
                path.write_text(original, encoding='utf-8')
        self.validate()

    def test_generated_hub_needs_no_imports_directory(self):
        self.assertFalse((self.hub / 'knowledge/imports').exists())
        self.validate()

    def test_plain_text_cross_hub_context_is_not_a_structural_reference(self):
        self.fixture(DOCUMENT + '\nAdditional context: sales hub, '
                     'SPIN document, read 2026-09-23.\n')
        self.validate()

    def test_validator_does_not_write_even_on_failure(self):
        self.fixture(DOCUMENT.replace('status: draft', 'status: bad'))
        before = {p.relative_to(self.hub): p.read_bytes() for p in self.hub.rglob('*') if p.is_file()}
        self.validate(False)
        after = {p.relative_to(self.hub): p.read_bytes() for p in self.hub.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_missing_frontmatter(self):
        self.fixture('# Missing\n')
        self.validate(False, 'Missing frontmatter')

    def test_missing_required_fields(self):
        for line in ('type: Concept\n', 'title: Test knowledge\n',
                     'description: Example for checking the structure.\n', 'status: draft\n',
                     'generated:\n  by: process:test\n  at: 2026-09-23T12:00:00Z\n'):
            with self.subTest(line=line):
                self.fixture(DOCUMENT.replace(line, ''))
                self.validate(False)

    def test_wrong_field_types_and_empty_values(self):
        for old, new in [('title: Test knowledge', 'title: []'),
                         ('description: Example for checking the structure.', 'description: ""'),
                         ('type: Concept', 'type: {}'),
                         ('status: draft', 'status: ["draft"]'),
                         ('  by: process:test', '  by: ""')]:
            with self.subTest(new=new):
                self.fixture(DOCUMENT.replace(old, new))
                self.validate(False)

    def test_unknown_status_and_type(self):
        for old, new, error in [('status: draft', 'status: ready', 'Invalid status'),
                                ('type: Concept', 'type: Unknown', 'concept_types')]:
            with self.subTest(new=new):
                self.fixture(DOCUMENT.replace(old, new))
                self.validate(False, error)

    def test_sources_required_in_silver_and_gold(self):
        for layer in ('10-silver', '20-gold'):
            path = self.hub / f'knowledge/{layer}/missing.md'
            with self.subTest(layer=layer):
                self.fixture(DOCUMENT.replace('sources:\n  - id: input\n    resource: ../00-bronze/source.txt\n    title: Source material', 'sources: []'), path)
                self.validate(False, 'requires nonempty sources')
            path.unlink()

    def test_bronze_requires_metadata_but_not_sources(self):
        text = DOCUMENT.split('sources:')[0] + '---\n# Source\n'
        self.fixture(text, self.hub / 'knowledge/00-bronze/source.md')
        self.validate()

    def test_doc_key_is_required_on_silver_and_gold(self):
        self.fixture(DOCUMENT.replace('doc_key: 11111111-1111-4111-8111-111111111111\n', ''))
        self.validate(False, 'requires a nonempty doc_key')

    def test_doc_key_must_be_a_uuid(self):
        self.fixture(DOCUMENT.replace('doc_key: 11111111-1111-4111-8111-111111111111',
                                      'doc_key: not-a-uuid'))
        self.validate(False, 'doc_key must be a UUID')

    def test_duplicate_doc_key_across_documents(self):
        self.fixture()
        (self.hub / 'knowledge/00-bronze/extra.txt').write_text('Additional.\n', encoding='utf-8')
        second = (DOCUMENT.replace('id: input', 'id: extra')
                  .replace('resource: ../00-bronze/source.txt', 'resource: ../00-bronze/extra.txt')
                  .replace('[^input]', '[^extra]'))
        (self.hub / 'knowledge/20-gold/second.md').write_text(second, encoding='utf-8')
        report = self.validate(False, 'Duplicate doc_key')
        self.assertEqual(report['violations'], 1)

    def test_bronze_and_decisions_do_not_require_doc_key(self):
        text = (DOCUMENT.split('sources:')[0] + '---\n# Note\n').replace(
            'doc_key: 11111111-1111-4111-8111-111111111111\n', '')
        for target in ('knowledge/00-bronze/source.md', 'knowledge/90-decisions/decision.md'):
            with self.subTest(target=target):
                self.fixture(text, self.hub / target)
                self.validate()
                (self.hub / target).unlink()

    def test_document_classification_is_optional_and_strict(self):
        self.fixture()
        self.validate()
        self.fixture(DOCUMENT.replace('status: draft', 'status: draft\nclassification: Public'))
        self.validate()
        self.fixture(DOCUMENT.replace('status: draft', 'status: draft\nclassification: secret'))
        self.validate(False, 'classification must be Public, Internal, Confidential, or Secret')

    def test_well_formed_external_ref_resolves_as_footnote(self):
        self.fixture(DOCUMENT_WITH_EXTERNAL_REF)
        self.validate()

    def test_external_ref_missing_note_is_violation(self):
        self.fixture(DOCUMENT_WITH_EXTERNAL_REF.replace(
            '    note: "Cited from a competency hub."\n', ''))
        self.validate(False, 'external_refs[].note is required')

    def test_external_ref_malformed_hub_or_doc_is_violation(self):
        for old, new in [
            ('    hub: 33333333-3333-4333-8333-333333333333\n', '    hub: not-a-uuid\n'),
            ('    doc: 44444444-4444-4444-8444-444444444444\n', '    doc: not-a-uuid\n')]:
            with self.subTest(new=new):
                self.fixture(DOCUMENT_WITH_EXTERNAL_REF.replace(old, new))
                self.validate(False, 'external_refs[].' + ('hub' if 'hub' in new else 'doc')
                              + ' must be a UUID')

    def test_external_ref_missing_or_invalid_operation_is_violation(self):
        for old, new in [('    operation: cite\n', ''),
                         ('    operation: cite\n', '    operation: sync\n')]:
            with self.subTest(new=new):
                self.fixture(DOCUMENT_WITH_EXTERNAL_REF.replace(old, new))
                self.validate(False, 'external_refs[].operation must be "cite" or "derive"')

    def test_external_ref_secret_classification_is_hard_block(self):
        self.fixture(DOCUMENT_WITH_EXTERNAL_REF.replace(
            '    classification: Internal\n', '    classification: Secret\n'))
        report = self.validate(False, 'external_refs[].classification must not be "Secret"')
        self.assertEqual(report['violations'], 1)

    def test_external_ref_duplicate_id_against_sources_id(self):
        self.fixture(DOCUMENT_WITH_EXTERNAL_REF.replace('id: ext-ref', 'id: input').replace(
            'External claim.[^ext-ref]\n\n[^ext-ref]: External detail.\n', ''))
        self.validate(False, 'Duplicate external_refs[].id: input')

    def test_unused_external_ref_id_uses_distinct_message(self):
        text = DOCUMENT_WITH_EXTERNAL_REF.replace(
            'External claim.[^ext-ref]\n\n[^ext-ref]: External detail.\n', '')
        self.fixture(text)
        report = self.validate(True, 'Unused external_refs[].id: ext-ref')
        self.assertEqual(len(report['warnings']), 1)

    def test_footnote_with_unknown_id_names_both_origins(self):
        self.fixture(DOCUMENT_WITH_EXTERNAL_REF + '\nOther.[^other]\n\n[^other]: Explanation.\n')
        self.validate(False, 'Footnote has no sources[].id or external_refs[].id: other')

    def test_derive_without_decision_entry_is_violation(self):
        self.fixture(DOCUMENT_WITH_EXTERNAL_REF.replace(
            '    operation: cite\n', '    operation: derive\n'
        ).replace('    classification: Internal\n', '    classification: Confidential\n'))
        report = self.validate(False, '90-decisions entry')
        self.assertEqual(report['violations'], 1)

    def test_derive_decision_entry_without_doc_key_mention_still_violation(self):
        self.fixture(DOCUMENT_WITH_EXTERNAL_REF.replace(
            '    operation: cite\n', '    operation: derive\n'
        ).replace('    classification: Internal\n', '    classification: Confidential\n'))
        decision = (DOCUMENT.split('sources:')[0] + '---\n# Decision\n\nApproved generalization.\n'
                   ).replace('doc_key: 11111111-1111-4111-8111-111111111111\n', '')
        decision_path = self.hub / 'knowledge/90-decisions/decision.md'
        decision_path.parent.mkdir(parents=True, exist_ok=True)
        decision_path.write_text(decision, encoding='utf-8')
        self.validate(False, '90-decisions entry')

    def test_derive_decision_entry_mentioning_doc_key_is_clean(self):
        self.fixture(DOCUMENT_WITH_EXTERNAL_REF.replace(
            '    operation: cite\n', '    operation: derive\n'
        ).replace('    classification: Internal\n', '    classification: Confidential\n'))
        decision = (DOCUMENT.split('sources:')[0] + '---\n# Decision\n\n'
                   'Approved generalization referencing doc_key '
                   '11111111-1111-4111-8111-111111111111.\n'
                   ).replace('doc_key: 11111111-1111-4111-8111-111111111111\n', '')
        decision_path = self.hub / 'knowledge/90-decisions/decision.md'
        decision_path.parent.mkdir(parents=True, exist_ok=True)
        decision_path.write_text(decision, encoding='utf-8')
        self.validate()

    def test_sources_shapes_ids_and_file_targets(self):
        for old, new, error in [
            ('sources:\n  - id: input\n    resource: ../00-bronze/source.txt\n    title: Source material',
             'sources: {}', 'sources must be a list'),
            ('sources:\n  - id: input\n    resource: ../00-bronze/source.txt\n    title: Source material',
             'sources: ["input"]', 'Each source must be a mapping'),
            ('  - id: input', '  - id: "bad id"', 'Source id'),
            ('    resource: ../00-bronze/source.txt', '    resource: ../00-bronze/missing.txt', 'does not exist'),
            ('    resource: ../00-bronze/source.txt', '    resource: ../00-bronze', 'does not exist'),
            ('    resource: ../00-bronze/source.txt', '    resource: https://example.org/source', 'local file')]:
            with self.subTest(new=new):
                self.fixture(DOCUMENT.replace(old, new))
                self.validate(False, error)

    def test_duplicate_source_id(self):
        self.fixture(DOCUMENT.replace('    title: Source material',
                     '    title: Source material\n  - id: input\n    resource: ../00-bronze/source.txt'))
        self.validate(False, 'Duplicate sources[].id')

    def test_footnotes_require_definition_and_source(self):
        self.fixture(DOCUMENT.replace('[^input]: Material excerpt.', ''))
        self.validate(False, 'Missing footnote definition')
        self.fixture(DOCUMENT + '\nOther.[^other]\n\n[^other]: Explanation.\n')
        self.validate(False, 'Footnote has no sources[].id')

    def test_duplicate_footnote_definition(self):
        self.fixture(DOCUMENT + '\n[^input]: Repeat.\n')
        self.validate(False, 'Duplicate footnote definition')

    def test_unused_source_is_warning_not_violation(self):
        self.fixture(DOCUMENT.replace('Claim.[^input]', 'Claim.'))
        result = self.validate(True, 'Unused sources[].id')
        self.assertEqual(len(result['warnings']), 1)

    def test_unreferenced_bronze_file_is_warning_not_violation(self):
        self.fixture()
        (self.hub / 'knowledge/00-bronze/orphan.txt').write_text('Unused.\n', encoding='utf-8')
        report = self.validate(True, 'not referenced by any sources')
        self.assertEqual(len(report['warnings']), 1)
        self.assertEqual(report['warnings'][0]['file'], 'knowledge/00-bronze/orphan.txt')

    def test_bronze_file_referenced_from_any_document_is_not_orphaned(self):
        self.fixture()
        (self.hub / 'knowledge/00-bronze/extra.txt').write_text('Additional.\n', encoding='utf-8')
        second = (DOCUMENT.replace('id: input', 'id: extra')
                  .replace('resource: ../00-bronze/source.txt', 'resource: ../00-bronze/extra.txt')
                  .replace('[^input]', '[^extra]')
                  .replace('11111111-1111-4111-8111-111111111111',
                           '22222222-2222-4222-8222-222222222222'))
        (self.hub / 'knowledge/10-silver/second.md').write_text(second, encoding='utf-8')
        report = self.validate()
        self.assertEqual(report['warnings'], [])

    def test_bronze_file_logged_as_no_material_is_not_orphaned(self):
        self.fixture()
        (self.hub / 'knowledge/00-bronze/orphan.txt').write_text('Unused.\n', encoding='utf-8')
        (self.hub / 'knowledge/log.md').write_text(
            '# Log\n\n## 2026-09-23\n\n- No material: 00-bronze/orphan.txt\n', encoding='utf-8')
        report = self.validate()
        self.assertEqual(report['warnings'], [])

    def test_inline_image_reference_and_nested_links(self):
        for link in ('[x](missing.md)', '![x](missing.png)', '[x][bad]\n\n[bad]: missing.md',
                     '[x][]\n\n[x]: missing.md', '[x]\n\n[x]: missing.md',
                     '[outer [inner]](missing.md)', '[x](missing(one).md)',
                     '[x](<missing file.md> "Title")', '[x](missing.md "Title")'):
            with self.subTest(link=link):
                self.fixture(DOCUMENT + '\n' + link + '\n')
                self.validate(False, 'does not exist')

    def test_missing_reference_definition_and_malformed_links(self):
        for link in ('[x][absent]', '[x](', '[x]()', '[x](foo bar baz)', '[x]['):
            with self.subTest(link=link):
                self.fixture(DOCUMENT + '\n' + link + '\n')
                self.validate(False)

    def test_valid_link_formats_code_and_external_urls(self):
        (self.hub / 'knowledge/00-bronze/file (one).txt').write_text('text')
        self.fixture(DOCUMENT + '''
[x](<../00-bronze/file (one).txt> "title")
[x](../00-bronze/file%20%28one%29.txt#anchor)
[x](../00-bronze/source.txt?view=1#anchor)
[x][source]
[source][]
[source]
[source]: ../00-bronze/source.txt "title"
[external](https://example.org/does-not-need-network)
[mail](mailto:someone@example.org)
[anchor](#unknown-heading)
`[literal](missing.md)`
```md
[literal](missing.md) [^absent]
```
~~~md
[[example]]
~~~
''')
        self.validate()

    def test_unsupported_link_formats_and_unclosed_fence(self):
        for text in ('[[missing]]', '<a href="missing.md">x</a>', '<img src="missing.png">', '```\n'):
            with self.subTest(text=text):
                self.fixture(DOCUMENT + '\n' + text)
                self.validate(False)

    def test_index_version_and_missing_scaffold(self):
        index = self.hub / 'knowledge/index.md'
        original = index.read_text()
        index.write_text(original.replace('"0.2"', '"0.3"'))
        self.validate(False, 'okf_version')
        index.unlink()
        self.validate(False, 'Required scaffold file')

    def test_timestamp_requires_real_datetime_and_timezone(self):
        for stamp in ('2026-09-23T12:00:00', '2026-02-30T12:00:00Z', '2026-09-23',
                      'not-a-date', '[]', '2026-09-23T12:00:00+25:00'):
            with self.subTest(stamp=stamp):
                self.fixture(DOCUMENT.replace('2026-09-23T12:00:00Z', stamp))
                self.validate(False, 'ISO 8601')
        self.fixture(DOCUMENT.replace('2026-09-23T12:00:00Z', '2026-09-23T14:00:00+02:00'))
        self.validate()

    def test_log_frontmatter_dates_order_and_unheaded_entries(self):
        log = self.hub / 'knowledge/log.md'
        for text in ('---\ntitle: Log\n---\n', '# Log\nUndated entry\n',
                     '# Log\n## 2026-02-30\n', '# Log\n## 2026-9-23\n',
                     '# Log\n## 2026-09-22\nA\n## 2026-09-23\nB\n',
                     '# Log\n## 2026-09-23\nA\n## 2026-09-23\nB\n'):
            with self.subTest(text=text):
                log.write_text(text)
                self.validate(False)

    def test_unknown_yaml_never_silently_passes(self):
        for extra in ('extra: &anchor thing', 'extra: *anchor', 'extra: !!str text',
                      'extra: |\n  multiline', 'extra: >\n  multiline',
                      'extra: [bare, values]', 'extra: {key: value}', '# comment',
                      'extra: text # comment', 'extra: yes', 'extra: 42',
                      'extra: 0x20', 'extra: .nan', 'extra: 1_000', 'extra: [NaN]', 'extra: [1e999]',
                      'extra:\n   bad: indent', 'extra:\n\tbad: tab',
                      'extra: "multiline\n  string"', '<<: *anchor',
                      'title: Duplicate', 'extra: {"x": "one", "x": "two"}',
                      'extra:\n  x: one\n  x: two'):
            with self.subTest(extra=extra):
                self.fixture(DOCUMENT.replace('type: Concept', 'type: Concept\n' + extra))
                self.validate(False, 'Frontmatter:')

    def test_unclosed_frontmatter(self):
        self.fixture('---\ntype: Concept\n')
        self.validate(False, 'Unclosed frontmatter')

    def test_supported_nested_and_inline_frontmatter(self):
        self.fixture(DOCUMENT.replace('generated:\n  by: process:test\n  at: 2026-09-23T12:00:00Z',
                     'generated: {"by": "process:test", "at": "2026-09-23T12:00:00Z"}')
                     .replace('title: Test knowledge', "title: 'Author''s note'")
                     .replace('status: draft', 'status: draft\ntags: ["one", "two"]\nextra:\n  labels:\n    - first\n    - second'))
        self.validate()

    def test_bad_config_and_quality_cannot_disable_scanning(self):
        path = self.hub / 'hub.json'
        original = path.read_text()
        for change in (lambda c: c['quality'].update(threshold=100),
                       lambda c: c['quality'].update(threshold=False),
                       lambda c: c['quality'].update(max_fix_iterations=0),
                       lambda c: c['quality'].update(validator='skip.py'),
                       lambda c: c['quality'].pop('evidence_script'),
                       lambda c: c['quality'].update(evidence_script='skip.py'),
                       lambda c: c.update(bundle_root='empty'),
                       lambda c: c.update(concept_types=[]),
                       lambda c: c.update(concept_types=['Concept', 'Concept'])):
            path.write_text(original)
            self.config(change)
            self.validate(False)
        for text in ('{', '[]', '{"concept_types": [], "concept_types": ["Concept"]}'):
            path.write_text(text)
            self.validate(False)

    def test_paths_cannot_escape_hub_or_use_symlinks(self):
        outside = self.root / 'outside.txt'
        outside.write_text('outside')
        for target in ('../../../outside.txt', str(outside), '../../../%6futside.txt'):
            with self.subTest(target=target):
                self.fixture(DOCUMENT.replace('../00-bronze/source.txt', target))
                self.validate(False)
        self.fixture()
        link = self.hub / 'knowledge/10-silver/link.md'
        link.symlink_to(outside)
        self.validate(False, 'Symlinks')
        link.unlink()
        directory = self.hub / 'knowledge/external'
        directory.symlink_to(self.root, target_is_directory=True)
        self.validate(False, 'Symlinks')

    def test_invalid_utf8_is_reported_as_json(self):
        self.doc.write_bytes(b'\xff\xfe')
        self.validate(False, 'UTF-8')

    def test_error_line_is_in_original_document(self):
        self.fixture(DOCUMENT + '\n[x](missing.md)\n')
        report = self.validate(False)
        error = next(e for e in report['errors'] if 'does not exist' in e['message'])
        self.assertEqual(error['file'], 'knowledge/10-silver/concept.md')
        self.assertEqual(error['line'], len(DOCUMENT.splitlines()) + 2)

    def test_moved_hub_still_validates_without_generator(self):
        self.fixture()
        moved = self.root / 'moved hub'
        self.hub.rename(moved)
        self.hub = moved
        self.script = moved / 'scripts/validate_hub.py'
        self.validate()

    def test_reference_checks_do_not_disappear_in_escaped_code_or_separate_paragraphs(self):
        for text in ('\\` [x](missing.md) `', '`text\n\n[x](missing.md)\n\n`'):
            with self.subTest(text=text):
                self.fixture(DOCUMENT + '\n' + text)
                self.validate(False, 'does not exist')

    def test_config_missing_or_symlinked(self):
        path = self.hub / 'hub.json'
        contents = path.read_text()
        path.unlink()
        self.validate(False)
        external = self.root / 'config.json'
        external.write_text(contents)
        path.symlink_to(external)
        self.validate(False, 'symlink')

    def test_missing_entire_knowledge_tree_is_not_green(self):
        (self.hub / 'knowledge').rename(self.root / 'saved-knowledge')
        self.validate(False, 'Required scaffold file')

    def test_nonregular_markdown_does_not_block(self):
        import os
        if not hasattr(os, 'mkfifo'):
            self.skipTest('FIFO not supported on this platform')
        os.mkfifo(self.doc)
        self.validate(False, 'regular files')

    def test_nonregular_config_does_not_block(self):
        import os
        if not hasattr(os, 'mkfifo'):
            self.skipTest('FIFO not supported on this platform')
        path = self.hub / 'hub.json'
        path.unlink()
        os.mkfifo(path)
        self.validate(False, 'regular file')

    def test_python_310_syntax(self):
        # Grammar compatibility, not a substitute for runtime tests on Python 3.10.
        ast.parse(self.script.read_text(), feature_version=(3, 10))


if __name__ == '__main__':
    unittest.main()
