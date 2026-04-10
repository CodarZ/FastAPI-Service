#!/usr/bin/env python3
import ast
import sys

from pathlib import Path


def check_file(path: str) -> bool:
    try:
        content = Path(path).read_text(encoding='utf-8')
        tree = ast.parse(content)
    except (FileNotFoundError, SyntaxError) as e:
        print(f'[Warn] Failed to parse {path}: {e}', file=sys.stderr)
        return False

    has_error = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in ('ForeignKey', 'relationship', 'back_populates'):
            print(
                f'\n[Error] {path}:{node.lineno} - Physical '
                f'FKs/relationships are strictly forbidden! Found: `{node.id}`',
                file=sys.stderr,
            )
            has_error = True
    return has_error


if __name__ == '__main__':
    paths = sys.argv[1:]
    if not paths:
        sys.exit(0)

    has_error = any(check_file(p) for p in paths)
    if has_error:
        print('\n[create-model-schema] Validation FAILED! Zero Physical Foreign Keys rule violated.', file=sys.stderr)
        print(
            '[create-model-schema] You MUST remove SQLAlchemy `ForeignKey` and `relationship`. '
            'Use plain `int` logic references instead.',
            file=sys.stderr,
        )
        sys.exit(1)

    print('[create-model-schema] Validation PASSED. Zero Physical Foreign Keys strictly verified.', file=sys.stdout)
    sys.exit(0)
