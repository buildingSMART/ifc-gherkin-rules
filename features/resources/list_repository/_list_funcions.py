if __name__ == "__main__":
    import ast
    import glob
    import json
    import os
    from pathlib import Path

    curr_dir_name = os.path.dirname(__file__)
    parent_path = Path(curr_dir_name).parent.parent
    steps_path = os.path.join(parent_path, 'steps')

    signatures = {'givens': 'given', 'thens': 'then', 'utils': 'def'}
    skips = ['__init__.py']

    for directory, signature in signatures.items():
        functions = {}

        dir_path = os.path.join(steps_path, directory)
        pys_path = os.path.join(dir_path, '*.py')
        utils_files = glob.glob(pys_path)

        for file_path in utils_files:
            base_path = os.path.basename(os.path.normpath(file_path))
            if base_path in skips:
                continue
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read())
                functions[base_path] = []
                for node in ast.walk(tree):
                    if directory in ['givens', 'thens'] and isinstance(node, ast.FunctionDef) and node.decorator_list:
                        for decorator in node.decorator_list:
                            if signature == decorator.func.id:
                                functions[base_path].append(decorator.args[0].value)
                    elif directory in ['utils'] and isinstance(node, ast.FunctionDef):
                        functions[base_path].append(node.name)
            functions[os.path.basename(os.path.normpath(file_path))].sort()
        with open(f'{directory}_functions.json', 'w') as f:
            json.dump(functions, f)
