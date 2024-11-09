from pathlib import Path
import json

def verify_sfdx_project():
    project_path = Path('/Users/reynchr/VSC Projects/docsTest')

    print("\n=== Verifying SFDX Project ===\n")

    # Check sfdx-project.json
    sfdx_project = project_path / 'sfdx-project.json'
    print(f"1. Checking sfdx-project.json:")
    if sfdx_project.exists():
        print("✅ sfdx-project.json found")
        try:
            with open(sfdx_project, 'r') as f:
                config = json.load(f)
                print("  Contents:", json.dumps(config, indent=2))
        except Exception as e:
            print(f"❌ Error reading sfdx-project.json: {str(e)}")
    else:
        print("❌ sfdx-project.json not found")

    # Check manifest directory
    manifest_dir = project_path / 'manifest'
    print("\n2. Checking manifest directory:")
    if manifest_dir.exists():
        print("✅ manifest directory found")
    else:
        print("❌ manifest directory not found")

    # Check force-app directory
    force_app = project_path / 'force-app'
    print("\n3. Checking force-app directory:")
    if force_app.exists():
        print("✅ force-app directory found")
    else:
        print("❌ force-app directory not found")

    # Check SFDX auth
    import subprocess
    print("\n4. Checking SFDX authentication:")
    try:
        result = subprocess.run(
            ['sfdx', 'force:org:list', '--json'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            orgs = json.loads(result.stdout)
            if orgs.get('result'):
                print("✅ Found authenticated orgs:")
                for org in orgs['result']:
                    if 'alias' in org:
                        print(f"  - {org.get('alias')} ({org.get('username')})")
        else:
            print("❌ Error checking org authentication")
    except Exception as e:
        print(f"❌ Error running sfdx command: {str(e)}")

if __name__ == "__main__":
    verify_sfdx_project()