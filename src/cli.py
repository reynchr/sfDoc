"""
    Command Line Interface for Salesforce Org Analyzer.
    This module provides the main CLI interface for analyzing Salesforce org metadata,
    generating documentation, and visualizing automation execution paths.
"""
import logging
from pathlib import Path
from typing import Optional, List
import click
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
# Import core components for analysis and visualization
from src.utils.sfdx_helper import SFDXHelper, ConfigManager, LogManager
from src.execution.path_analyzer import ExecutionPathAnalyzer
from src.execution.visualizer import ExecutionPathVisualizer
from src.llm.documenter import LLMDocumenter
# Initialize rich console for enhanced terminal output
console = Console()
logger = logging.getLogger(__name__)

def setup_logging():
    """
        Configure logging with rich output for enhanced readability.
        Uses RichHandler for formatted console output with tracebacks.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )

def validate_project_path(ctx, param, value):
    """
        Validate that the provided path contains a valid SFDX project.
        
        Args:
            ctx: Click context
            param: Click parameter
            value: Project path to validate
        
        Returns:
            Path: Validated project path
        
        Raises:
            click.BadParameter: If path is not a valid SFDX project
    """
    path = Path(value)
    try:
        SFDXHelper(path)._validate_sfdx_project()
        return path
    except ValueError as e:
        raise click.BadParameter(str(e))

@click.group()
@click.option(
    '--project-path', 
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    callback=validate_project_path,
    help='Path to SFDX project root'
)
@click.option(
    '--config', 
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    help='Path to configuration file'
)
@click.option('--debug/--no-debug', default=False, help='Enable debug logging')
@click.pass_context
def cli(ctx, project_path: Path, config: Optional[Path], debug: bool):
    """
        Main entry point for the Salesforce Org Analyzer CLI.
        Initializes configuration and logging, and sets up the CLI context.
    """
    setup_logging()
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    # Initialize configuration and logging
    try:
        config_manager = ConfigManager(config)
        log_manager = LogManager(config_manager.config)
    except Exception as e:
        console.print(f"[red]Error loading configuration: {str(e)}[/red]")
        raise click.Abort()
    # Store common objects in context for access by subcommands
    ctx.ensure_object(dict)
    ctx.obj['project_path'] = project_path
    ctx.obj['config'] = config_manager.config
    ctx.obj['sfdx_helper'] = SFDXHelper(project_path)

@cli.command()
@click.option(
    '--objects', 
    help='Comma-separated list of objects to analyze'
)
@click.option(
    '--output-dir', 
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default='documentation',
    help='Output directory for analysis results'
)
@click.option(
    '--skip-llm/--use-llm',
    default=False,
    help='Skip LLM documentation generation'
)
@click.pass_context
def analyze(ctx, objects: Optional[str], output_dir: Path, skip_llm: bool):
    """
        Analyze Salesforce org automation and generate documentation.
        
        Performs comprehensive analysis of Salesforce automation for specified objects,
        generating documentation and visualization diagrams for execution paths.
        
        Args:
            ctx: Click context object containing configuration and helper instances
                - project_path: Path to SFDX project
                - config: Loaded configuration dictionary
                - sfdx_helper: Initialized SFDXHelper instance
            objects: Comma-separated string of Salesforce object names to analyze
                Example: "Account,Contact,Opportunity"
            output_dir: Directory path where analysis results will be saved
                Creates subdirectories for each analyzed object
            skip_llm: Boolean flag to skip LLM-based documentation generation
                True: Generate basic documentation only
                False: Include AI-generated documentation
        
        Returns:
            None
        
        Raises:
            click.ClickException: If project validation fails or critical errors occur
            Exception: Handles individual object analysis failures without stopping execution
        
        Output Structure:
            output_dir/
            ├── Object1/
            │   └── documentation.md
            ├── Object2/
            │   └── documentation.md
            └── ...
                
        Documentation Contents:
            - Overview (LLM-generated if enabled)
            - Technical Details
            - Business Impact Analysis
            - Automation Entry Points
            - Recursion Risks
            - Mermaid Execution Path Diagrams
    """
    sfdx_helper: SFDXHelper = ctx.obj['sfdx_helper']
    config = ctx.obj['config']

    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    # Parse object list from comma-separated string
    object_list = objects.split(',') if objects else None
    # Initialize progress display
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        try:
            # Verify project structure
            task = progress.add_task("Verifying SFDX project...", total=None)
            project_path = ctx.obj['project_path']
            if not (project_path / 'sfdx-project.json').exists():
                raise click.ClickException(
                    f"No sfdx-project.json found in {project_path}. "
                    "Please ensure this is a valid Salesforce project directory."
                )
            # Ensure manifest directory exists for metadata retrieval
            manifest_dir = project_path / 'manifest'
            manifest_dir.mkdir(exist_ok=True)
            # Retrieve metadata for specified objects
            progress.update(task, description="Fetching metadata...")
            if object_list:
                metadata_types = ['CustomObject', 'ApexTrigger', 'Flow', 'WorkflowRule']
                package_xml = sfdx_helper.create_package_xml(metadata_types)
                if not sfdx_helper.retrieve_source(package_xml):
                    console.print("[yellow]Warning: Some metadata retrieval failed[/yellow]")
            # Initialize analysis components
            analyzer = ExecutionPathAnalyzer(config)
            visualizer = ExecutionPathVisualizer(config)
            # Initialize LLM documentation generator if enabled
            if not skip_llm:
                try:
                    documenter = LLMDocumenter(config)
                except Exception as e:
                    console.print(f"[yellow]Warning: LLM initialization failed: {str(e)}[/yellow]")
                    console.print("[yellow]Continuing without LLM documentation[/yellow]")
                    skip_llm = True
            # Process each object
            for obj in object_list or []:
                try:
                    # Analyze automation and execution paths
                    progress.update(task, description=f"Analyzing {obj}...")
                    analysis_result = analyzer.analyze_object(obj, {})
                    # Generate LLM documentation if enabled
                    if not skip_llm:
                        progress.update(task, description=f"Generating documentation for {obj}...")
                        doc_result = documenter.generate_documentation(analysis_result)
                    else:
                        doc_result = None
                    # Generate execution path diagrams
                    progress.update(task, description=f"Generating diagrams for {obj}...")
                    diagram = visualizer.generate_mermaid(analysis_result)
                    # Create output directory for object
                    obj_dir = output_dir / obj
                    obj_dir.mkdir(exist_ok=True)
                    # Write documentation and diagrams to file
                    with open(obj_dir / 'documentation.md', 'w') as f:
                        f.write(f"# {obj} Automation Analysis\n\n")
                        if doc_result:
                            # Include LLM-generated documentation
                            f.write(f"## Overview\n\n{doc_result.overview}\n\n")
                            f.write(f"## Technical Details\n\n{doc_result.technical_details}\n\n")
                            f.write(f"## Business Impact\n\n{doc_result.business_impact}\n\n")
                            f.write("## Recommendations\n\n")
                            for rec in doc_result.recommendations:
                                f.write(f"- {rec}\n")
                        else:
                            # Include basic analysis results
                            f.write("## Analysis Results\n\n")
                            f.write(f"Found {len(analysis_result.entry_points)} automation entry points.\n\n")
                            if analysis_result.recursion_risks:
                                f.write("### Potential Risks\n\n")
                                for risk in analysis_result.recursion_risks:
                                    f.write(f"- {risk}\n")
                        # Include execution path diagram
                        f.write("\n## Execution Path Diagram\n\n")
                        f.write("```mermaid\n")
                        f.write(diagram)
                        f.write("\n```\n")
                    console.print(f"[green]✓[/green] Completed analysis of {obj}")
                except Exception as e:
                    console.print(f"[red]Error analyzing {obj}: {str(e)}[/red]")
                    logger.exception(f"Error analyzing {obj}")
        except Exception as e:
            raise click.ClickException(str(e))

@cli.command()
@click.option(
    '--object', 
    required=True,
    help='Object to visualize'
)
@click.option(
    '--context',
    type=click.Choice(['before_insert', 'after_insert', 'before_update', 'after_update',
                      'before_delete', 'after_delete', 'after_undelete']),
    help='Specific trigger context to visualize'
)
@click.option(
    '--output-dir', 
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default='diagrams',
    help='Output directory for diagrams'
)

@click.pass_context
def visualize(ctx, object: str, context: Optional[str], output_dir: Path):
    """
        Generate visualization of execution paths for a specific object.
        Creates Mermaid diagrams showing automation execution paths. Can focus
        on a specific trigger context or show all contexts for the object.
        
        Args:
            ctx: Click context containing configuration and helpers
            object: Name of the Salesforce object to visualize
            context: Optional trigger context to filter visualization
            output_dir: Directory where diagram files will be saved
    """
    config = ctx.obj['config']
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    try:
        # Initialize analysis components
        analyzer = ExecutionPathAnalyzer(config)
        visualizer = ExecutionPathVisualizer(config)
        # Analyze object's automation and execution paths
        analysis_result = analyzer.analyze_object(object, {})
        # Generate appropriate diagram based on context
        if context:
            # Generate diagram for specific trigger context
            diagram = visualizer.generate_mermaid(analysis_result, context)
            filename = f"{object}_{context}_execution_path.mmd"
        else:
            # Generate diagram for all contexts
            diagram = visualizer.generate_mermaid(analysis_result)
            filename = f"{object}_execution_paths.mmd"
        # Save diagram to file
        with open(output_dir / filename, 'w') as f:
            f.write(diagram)
        console.print(f"[green]✓[/green] Generated diagram: {filename}")
    except Exception as e:
        console.print(f"[red]Error generating visualization: {str(e)}[/red]")
        logger.exception("Error generating visualization")

@cli.command()
@click.pass_context
def configure(ctx):
    """
        Interactive configuration for the analyzer.

        Allows users to customize:
            - LLM settings for documentation generation
            - Analysis parameters for code parsing
            - Visualization options for diagrams

        Updates are saved to the configuration file for future use.
    """
    config = ctx.obj['config']
    config_manager = ConfigManager()
    # Store configuration updates
    updates = {}
    # Create interactive configuration screen
    with console.screen():
        console.print("[bold]Salesforce Org Analyzer Configuration[/bold]\n")
        # Configure LLM settings
        updates['llm'] = {
            'model': click.prompt(
                "LLM Model",
                default=config['llm']['model']
            ),
            'temperature': click.prompt(
                "Temperature",
                default=config['llm']['temperature'],
                type=float
            ),
        }
        # Configure analysis settings
        updates['analysis'] = {
            'parser': {
                'include_inner_classes': click.confirm(
                    "Include inner classes?",
                    default=config['analysis']['parser']['include_inner_classes']
                ),
                'parse_annotations': click.confirm(
                    "Parse annotations?",
                    default=config['analysis']['parser']['parse_annotations']
                )
            }
        }
        # Configure visualization settings
        updates['visualization'] = {
            'include_conditions': click.confirm(
                "Include conditions in diagrams?",
                default=config['visualization']['include_conditions']
            ),
            'show_dml_operations': click.confirm(
                "Show DML operations in diagrams?",
                default=config['visualization']['show_dml_operations']
            )
        }
    # Save configuration updates
    try:
        config_manager.update_config(updates)
        console.print("[green]✓[/green] Configuration updated successfully")
    except Exception as e:
        console.print(f"[red]Error updating configuration: {str(e)}[/red]")

@cli.command()
def version():
    """
        Display the current version of the Salesforce Org Analyzer.    
        Retrieves version information from the package metadata.
        If the package is not installed via pip/poetry, version info may not be available.
    """
    import pkg_resources
    try:
        # Attempt to get version from package metadata
        version = pkg_resources.get_distribution('salesforce-analyzer').version
        console.print(f"Salesforce Org Analyzer v{version}")
    except pkg_resources.DistributionNotFound:
        console.print("Version information not available")

if __name__ == '__main__':
    # Entry point when script is run directly
    cli(obj={})