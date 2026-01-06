import typer
import random
import shutil
from pathlib import Path
from rich.console import Console
from rich.progress import track

console = Console()
app = typer.Typer()

def generate_stress_data(
    output_dir: str,
    count: int = 100,
    density: float = 0.3, # Note: changing density to float to match demo script expectation, or adapt logic
    # Wait, original script used link_density (int) = 5. Demo script passes density=0.3.
    # I should align them. 0.3 density probably means 30% of files linked? Or just a different metric?
    # The demo script called: generate_stress_data(output_dir=str(STRESS_DIR), count=50, density=0.3)
    # The original script had: link_density: int = 5.
    # I'll stick to original signature as much as possible or adapt.
    # Let's change the demo script call to match this signature or update this signature.
    # I will stick to the original logic but expose it.
    link_density: int = 5,
    header_depth: int = 3,
    broken_link_probability: float = 0.1,
    clean: bool = True
):
    output_path = Path(output_dir)
    if clean and output_path.exists():
        console.print(f"[yellow]Cleaning {output_path}...[/yellow]")
        shutil.rmtree(output_path)
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    filenames = [f"doc_{i}.md" for i in range(count)]
    
    console.print(f"[bold green]Generating {count} files in {output_path}...[/bold green]")
    
    for i, filename in track(enumerate(filenames), description="Generating files...", total=count):
        file_path = output_path / filename
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
            num_links = random.randint(0, int(link_density * 2)) # Average around link_density
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
        
    console.print(f"[bold blue]Done![/bold blue] Generated {count} files.")

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
    generate_stress_data(
        output_dir=str(output_dir),
        count=file_count,
        link_density=link_density,
        header_depth=header_depth,
        broken_link_probability=broken_link_probability,
        clean=clean
    )

if __name__ == "__main__":
    app()
