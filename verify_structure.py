from pathlib import Path

def check_structure():
    required_paths = [
        'src/init.py',
        'src/cli.py',
        'src/apex/init.py',
        'src/apex/parser.py',
        'src/apex/analyzer.py',
        'src/models/init.py',
        'src/automations/init.py',
        'src/execution/init.py',
        'src/llm/init.py',
        'src/utils/init.py',
        'config/default_config.yaml'
    ]

    missing = []
    for path in required_paths:
        if not Path(path).exists():
            missing.append(path)

    if missing:
        print("Missing files/directories:")
        for path in missing:
            print(f"  - {path}")
    else:
        print("All required files present!")

if __name__ == "__main__":
    check_structure()