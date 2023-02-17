if __name__ == "__main__":
    import glob
    import json

    utils_files = glob.glob("*.py")
    functions = {}

    for file_path in utils_files:
        with open(file_path, "r") as f:
            functions[file_path] = []
            file_lines = f.readlines()
            for line in file_lines:
                if 'def ' in line:
                    line = line.replace(':\n', '')
                    line = line.replace('def ', '')
                    line = line.strip()
                    functions[file_path].append(line)
        functions[file_path].sort()

    with open('util_functions.json', 'w') as f:
        json.dump(functions, f)
