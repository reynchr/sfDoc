# Salesforce Org Analyzer

A comprehensive tool for analyzing and documenting Salesforce org metadata, execution paths, and automations using AI-powered analysis.

## System Requirements
- macOS 12.0 or later
- Python 3.8 or later
- At least 16GB RAM
- 20GB free disk space (for Python packages and ML models)
- Internet connection for initial setup

## Project Structure
```
salesforce-analyzer/
├── src/
│   ├── apex/
│   │   ├── __init__.py
│   │   ├── parser.py          # Enhanced Apex parsing logic
│   │   └── analyzer.py        # Apex code analysis
│   ├── automations/
│   │   ├── __init__.py
│   │   ├── process_builder.py # Process Builder analysis
│   │   ├── flow.py           # Flow analysis
│   │   └── workflow.py        # Workflow rule analysis
│   ├── execution/
│   │   ├── __init__.py
│   │   ├── path_analyzer.py   # Execution path tracking
│   │   └── visualizer.py      # Mermaid diagram generation
│   ├── llm/
│   │   ├── __init__.py
│   │   └── documenter.py      # AI documentation generation
│   └── utils/
│       ├── __init__.py
│       └── sfdx_helper.py     # SFDX project utilities
├── tests/                     # Test files for each module
├── config/
│   └── default_config.yaml    # Configuration settings
├── requirements.txt           # Python dependencies
├── setup.py                   # Package installation
└── README.md                  # This documentation
```

## Setup Instructions

### 1. Check Current System State

```bash
# Create and run the system check script
cat << 'EOF' > check_system.sh
#!/bin/bash

echo "Checking system requirements..."

# Check macOS version
os_version=$(sw_vers -productVersion)
echo "macOS Version: $os_version"
if [[ $os_version < "12.0" ]]; then
    echo "⚠️  Warning: macOS 12.0 or later recommended"
fi

# Check Python installation
if command -v python3 &>/dev/null; then
    python_version=$(python3 --version)
    echo "✅ Python installed: $python_version"
else
    echo "❌ Python not installed"
fi

# Check Homebrew installation
if command -v brew &>/dev/null; then
    brew_version=$(brew --version | head -n 1)
    echo "✅ Homebrew installed: $brew_version"
else
    echo "❌ Homebrew not installed"
fi

# Check available RAM
total_ram=$(sysctl hw.memsize | awk '{print $2}')
ram_gb=$((total_ram / 1024 / 1024 / 1024))
echo "Available RAM: ${ram_gb}GB"
if [[ $ram_gb -lt 16 ]]; then
    echo "⚠️  Warning: 16GB RAM or more recommended"
fi

# Check available disk space
free_space=$(df -h / | awk 'NR==2 {print $4}' | sed 's/Gi//')
echo "Available disk space: ${free_space}GB"
if [[ $free_space -lt 20 ]]; then
    echo "⚠️  Warning: 20GB free space recommended"
fi
EOF

chmod +x check_system.sh
./check_system.sh
```

### 2. Install Required Software

If Homebrew is not installed:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

If Python is not installed:
```bash
brew install python@3.10
```

Install Poetry (Python dependency management):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 3. Clone and Setup Project

```bash
# Clone the repository
git clone https://github.com/your-repo/salesforce-analyzer.git
cd salesforce-analyzer

# Install dependencies using Poetry
poetry install
```

### 4. Configure Environment

```bash
# Create virtual environment and install dependencies
poetry shell

# Configure GPU support (if available)
# Check if you have an NVIDIA GPU
system_profiler SPDisplaysDataType | grep NVIDIA

# If NVIDIA GPU is present, install CUDA support
brew install cuda
```

### 5. Verify Installation

```bash
# Run the verification script
poetry run python -m salesforce_analyzer.verify
```

## Usage

### Basic Usage

1. Extract your Salesforce metadata:
```bash
sfdx force:source:retrieve -x path/to/package.xml -r ./force-app
```

2. Run the analyzer:
```bash
poetry run python -m salesforce_analyzer analyze --project-path ./force-app --output-dir ./documentation
```

### Advanced Usage

#### Analyzing Specific Components

```bash
# Analyze specific objects
poetry run python -m salesforce_analyzer analyze \
    --project-path ./force-app \
    --objects Account,Contact \
    --output-dir ./documentation

# Generate execution path diagrams
poetry run python -m salesforce_analyzer visualize \
    --project-path ./force-app \
    --object Account \
    --trigger-context "before insert" \
    --output-dir ./documentation
```

#### Configuration Options

Create a `config.yaml` file:
```yaml
llm:
  model: "codellama/CodeLlama-7b-hf"
  temperature: 0.1
  max_length: 2048

analysis:
  include_internal_classes: false
  parse_comments: true
  follow_interfaces: true

visualization:
  diagram_type: "mermaid"
  include_conditions: true
  show_order: true
```

## Troubleshooting

### Common Issues

1. **Memory Issues**
```bash
# Increase available memory for Python
export PYTHON_MEMORY_LIMIT=8G
```

2. **GPU Issues**
```bash
# Check GPU availability
python -c "import torch; print(torch.cuda.is_available())"
```

3. **Missing Dependencies**
```bash
poetry install --no-dev  # Install only production dependencies
```

### Getting Help

- Check the [Issues](https://github.com/your-repo/salesforce-analyzer/issues) page
- Run diagnostics:
```bash
poetry run python -m salesforce_analyzer diagnose
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests:
```bash
poetry run pytest
```
5. Submit a pull request

## License

MIT License - see LICENSE file for details
