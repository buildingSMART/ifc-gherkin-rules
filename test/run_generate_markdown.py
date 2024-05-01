import os
import subprocess
import re

def main():
    directory_path = os.path.join(os.path.dirname(__file__), 'files')

    folders = [name for name in os.listdir(directory_path)
               if os.path.isdir(os.path.join(directory_path, name)) and re.match(r'^[a-zA-Z]{3}\d{3}$', name)]

    subprocess.run(['python', 'generate_markdown.py'] + folders, cwd=os.path.dirname(__file__))

if __name__ == '__main__':
    main()
