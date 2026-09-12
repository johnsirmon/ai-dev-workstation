import contextlib
import copy
import importlib.util
import io
import json
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'mcp_validator', ROOT / 'scripts' / 'validate-mcp-config.py'
)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ValidateMcpConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = json.loads((ROOT / '.vscode' / 'mcp.json').read_text(encoding='utf-8'))
        self.tracking = json.loads(
            (ROOT / 'config' / 'tools-tracking.json').read_text(encoding='utf-8')
        )
        self.package = json.loads((ROOT / 'package.json').read_text(encoding='utf-8'))
        self.package_lock = json.loads(
            (ROOT / 'package-lock.json').read_text(encoding='utf-8')
        )

    def run_validation(self, check_registry: bool = False) -> tuple[int, str]:
        output = io.StringIO()
        with (
            patch.object(
                validator,
                'load_json',
                side_effect=[
                    self.config,
                    self.tracking,
                    self.package,
                    self.package_lock,
                ],
            ),
            contextlib.redirect_stdout(output),
        ):
            code = validator.validate(check_registry)
        return code, output.getvalue()

    def test_starter_passes_without_network(self) -> None:
        with patch.object(validator.urllib.request, 'urlopen') as request:
            code, output = self.run_validation()
        self.assertEqual(code, 0, output)
        self.assertNotIn('WARN:', output)
        request.assert_not_called()

    def test_package_extraction_handles_pins(self) -> None:
        for package in ('@scope/server', '@scope/server@1.2.3', '@scope/server@latest'):
            with self.subTest(package=package):
                config = {'command': 'npx', 'args': ['-y', package]}
                self.assertEqual(validator.extract_npm_package(config), '@scope/server')
        self.assertEqual(
            validator.extract_npm_package(
                {
                    'command': 'node',
                    'args': [
                        '${workspaceFolder}/node_modules/@scope/server/dist/index.js'
                    ],
                }
            ),
            '@scope/server',
        )
        self.assertIsNone(validator.extract_npm_package({'type': 'http', 'url': 'https://example.com'}))

    def test_registry_checks_unversioned_package_names(self) -> None:
        with patch.object(validator, 'check_npm_package_exists', return_value=True) as check:
            code, output = self.run_validation(check_registry=True)
        self.assertEqual(code, 0, output)
        self.assertEqual(
            {call.args[0] for call in check.call_args_list},
            set(self.tracking['tracked_tools']['mcp_servers']),
        )

    def test_credentials_require_valid_references(self) -> None:
        original = copy.deepcopy(self.config)
        for server, key in (('context7', 'CONTEXT7_API_KEY'), ('brave-search', 'BRAVE_API_KEY')):
            for invalid in (f'${{{key}}}', 'literal-credential-for-test', '', None):
                with self.subTest(server=server, invalid=invalid):
                    self.config = copy.deepcopy(original)
                    self.config['servers'][server]['env'][key] = invalid
                    code, output = self.run_validation()
                    self.assertEqual(code, 1)
                    self.assertIn(key, output)
                    self.assertNotIn('literal-credential-for-test', output)

    def test_password_input_reference_is_supported(self) -> None:
        self.config['servers']['brave-search']['env']['BRAVE_API_KEY'] = '${input:brave-key}'
        self.config['inputs'] = [
            {'id': 'brave-key', 'type': 'promptString', 'password': True}
        ]
        code, output = self.run_validation()
        self.assertEqual(code, 0, output)

    def test_missing_or_nonsecret_input_is_rejected(self) -> None:
        self.config['servers']['brave-search']['env']['BRAVE_API_KEY'] = '${input:brave-key}'
        for inputs in ([], [{'id': 'brave-key', 'type': 'promptString', 'password': False}]):
            with self.subTest(inputs=inputs):
                self.config['inputs'] = inputs
                code, output = self.run_validation()
                self.assertEqual(code, 1)
                self.assertIn('BRAVE_API_KEY', output)

    def test_missing_credentials_are_rejected(self) -> None:
        del self.config['servers']['context7']['env']['CONTEXT7_API_KEY']
        code, output = self.run_validation()
        self.assertEqual(code, 1)
        self.assertIn('CONTEXT7_API_KEY', output)

    def test_malformed_environment_is_reported(self) -> None:
        self.config['servers']['brave-search']['env'] = []
        code, output = self.run_validation()
        self.assertEqual(code, 1)
        self.assertIn('env must be an object', output)

    def test_unsupported_filesystem_flag_is_rejected(self) -> None:
        self.config['servers']['filesystem']['args'].insert(-1, '--allowed-directory')
        code, output = self.run_validation()
        self.assertEqual(code, 1)
        self.assertIn('positional', output)

    def test_missing_workspace_directory_is_rejected(self) -> None:
        self.config['servers']['filesystem']['args'].remove('${workspaceFolder}')
        code, output = self.run_validation()
        self.assertEqual(code, 1)
        self.assertIn('workspaceFolder', output)

    def test_untracked_pinned_package_is_rejected(self) -> None:
        self.config['servers']['memory']['args'][0] = (
            '${workspaceFolder}/node_modules/@scope/untracked/dist/index.js'
        )
        code, output = self.run_validation()
        self.assertEqual(code, 1)
        self.assertIn("Package '@scope/untracked'", output)

    def test_npx_package_is_rejected(self) -> None:
        self.config['servers']['memory'] |= {
            'command': 'npx',
            'args': ['-y', '@modelcontextprotocol/server-memory@2026.8.31'],
        }
        code, output = self.run_validation()
        self.assertEqual(code, 1)
        self.assertIn('workspace-local locked package', output)

    def test_nonexact_dependency_is_rejected(self) -> None:
        self.package['dependencies']['@modelcontextprotocol/server-memory'] = '^2026.8.31'
        code, output = self.run_validation()
        self.assertEqual(code, 1)
        self.assertIn('exact version', output)

    def test_missing_integrity_is_rejected(self) -> None:
        del self.package_lock['packages'][
            'node_modules/@modelcontextprotocol/server-memory'
        ]['integrity']
        code, output = self.run_validation()
        self.assertEqual(code, 1)
        self.assertIn('integrity-pinned', output)

    def test_missing_transitive_integrity_is_rejected(self) -> None:
        del self.package_lock['packages']['node_modules/accepts']['integrity']
        code, output = self.run_validation()
        self.assertEqual(code, 1)
        self.assertIn("Locked package 'node_modules/accepts'", output)

    def test_package_lock_root_must_match_dependencies(self) -> None:
        del self.package_lock['packages']['']['dependencies'][
            '@modelcontextprotocol/server-memory'
        ]
        code, output = self.run_validation()
        self.assertEqual(code, 1)
        self.assertIn('dependencies must match', output)

    def test_unrecognized_stdio_command_is_rejected(self) -> None:
        self.config['servers']['memory'] |= {
            'command': 'custom-server',
            'args': [],
        }
        code, output = self.run_validation()
        self.assertEqual(code, 1)
        self.assertIn('workspace-local npm package', output)

    def test_deprecated_environment_keys_are_still_rejected(self) -> None:
        self.config['servers']['brave-search']['env']['SEARCH_API_KEY'] = '${env:SEARCH_API_KEY}'
        code, output = self.run_validation()
        self.assertEqual(code, 1)
        self.assertIn('deprecated env vars', output)

    def test_unused_tracking_still_warns(self) -> None:
        del self.config['servers']['memory']
        code, output = self.run_validation()
        self.assertEqual(code, 0, output)
        self.assertIn('WARN:', output)


if __name__ == '__main__':
    unittest.main()
