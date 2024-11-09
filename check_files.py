# check_files.py
from pathlib import Path
import sys

def check_files():
    required_files = [
        'src/init.py',
        'src/cli.py',
        'src/apex/init.py',
        'src/apex/parser.py',
        'src/apex/analyzer.py',
        'src/models/init.py',
        'src/models/apex_models.py',
        'src/models/analysis_models.py',
        'src/automations/init.py',
        'src/execution/init.py',
        'src/execution/path_analyzer.py',
        'src/execution/visualizer.py',
        'src/llm/init.py',
        'src/llm/documenter.py',
        'src/utils/init.py',
        'src/utils/sfdx_helper.py',
        'config/default_config.yaml'
    ]

    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)

    if missing:
        print("\n❌ Missing files:")
        for file in missing:
            print(f"  - {file}")
        return False
    else:
        print("\n✅ All required files present!")
        return True

if __name__ == "__main__":
    if not check_files():
        print("\nRun these commands to create missing files:")
        print("mkdir -p src/apex src/models src/automations src/execution src/llm src/utils config")
        print("touch src/init.py src/cli.py")
        print("touch src/apex/init.py src/apex/parser.py src/apex/analyzer.py")
        print("touch src/models/init.py src/models/apex_models.py src/models/analysis_models.py")
        print("touch src/automations/init.py")
        print("touch src/execution/init.py src/execution/path_analyzer.py src/execution/visualizer.py")
        print("touch src/llm/init.py src/llm/documenter.py")
        print("touch src/utils/init.py src/utils/sfdx_helper.py")
        print("touch config/default_config.yaml")
        sys.exit(1)