import typer
import random
import shutil
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.progress import track

console = Console()
app = typer.Typer()

@app.command()
def generate(
    output_dir: Path = typer.Argument(..., help="Directory to output generated files"),
    file_count: int = typer.Option(100, help="Number of markdown files to generate"),
    link_density: int = typer.Option(5, help="Average number of links per file"),
    header_depth: int = typer.Option(3, help="Max depth of headers (1-6)"),
    broken_link_probability: float = typer.Option(0.1, help="Probability of a link being broken"),
    clean: bool = typer.Option(True, help="Clean output directory before generation")
):
    """
    Generates a dataset of inter-linked markdown files for stress testing.
    """
    if clean and output_dir.exists():
        console.print(f"[yellow]Cleaning {output_dir}...[/yellow]")
        shutil.rmtree(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filenames = [f"doc_{i}.md" for i in range(file_count)]
    
    console.print(f"[bold green]Generating {file_count} files in {output_dir}...[/bold green]")
    
    for i, filename in track(enumerate(filenames), description="Generating files...", total=file_count):
        file_path = output_dir / filename
        content = []
        
        # Title
        content.append(f"# Document {i}\n")
        content.append("This is a generated stress test document.\n")
        
        # Random headers and content
        num_sections = random.randint(2, 5)
        for s in range(num_sections):
            level = random.randint(2, header_depth)
            content.append(f"{'#' * level} Section {s}\n")
            content.append(f"Content for section {s}. Random text here.\n")
            
            # Add links
            num_links = random.randint(0, link_density * 2) # Average around link_density
            for _ in range(num_links):
                is_broken = random.random() < broken_link_probability
                
                if is_broken:
                    target = f"non_existent_{random.randint(0, 1000)}.md"
                else:
                    target = random.choice(filenames)
                    # Avoid self-links mostly, but they are valid
                
                content.append(f"- Reference to [{target}]({target})\n")
            
            content.append("\n")
            
        file_path.write_text("".join(content))
        
    console.print(f"[bold blue]Done![/bold blue] Generated {file_count} files.")

if __name__ == "__main__":
    app()
