from pathlib import Path

def normalize_path_to_project_root(current_file_path: Path, target_path: str) -> Path:
    """
    Normalizes a given target path to be relative to the project root.

    This function takes a path from within the project and a target path
    (which can be absolute, relative, or relative from the current file)
    and resolves it to a canonical path relative to the project's root directory.

    The project root is determined by traversing up from the current_file_path
    until a marker file like 'pyproject.toml' or '.git' directory is found.

    Args:
        current_file_path (Path): The absolute path of the file from which the
                                  target_path is being referenced.
        target_path (str): The path to normalize. Can be relative to
                           current_file_path, absolute, or relative to project root.

    Returns:
        Path: The normalized path relative to the project root.

    Raises:
        ValueError: If the project root cannot be determined or if the
                    target_path cannot be resolved relative to the project root.
    """
    current_file_path = current_file_path.resolve()

    # Find project root
    project_root = None
    for parent in current_file_path.parents:
        if (parent / "pyproject.toml").exists() or (parent / ".git").is_dir():
            project_root = parent
            break
    if project_root is None:
        raise ValueError("Could not determine project root. 'pyproject.toml' or '.git' not found.")

    target_full_path = None
    try:
        # If target_path is already absolute, just resolve it
        if Path(target_path).is_absolute():
            target_full_path = Path(target_path).resolve()
        else:
            # Resolve relative to the current file's directory first
            target_full_path = (current_file_path.parent / target_path).resolve()

        # Ensure the target path is within the project root
        return target_full_path.relative_to(project_root)
    except ValueError as e:
        raise ValueError(f"Could not normalize path '{target_path}' relative to project root '{project_root}': {e}")
    except Exception as e:
        raise ValueError(f"An unexpected error occurred while normalizing path '{target_path}': {e}")



