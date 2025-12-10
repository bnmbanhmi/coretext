from pathlib import Path

def normalize_path_to_project_root(current_file_path: Path, target_path: str, project_root: Path) -> Path:
    """
    Normalizes a given target path to be relative to the provided project root.

    This function takes a path from within the project and a target path
    (which can be absolute, relative, or relative from the current file)
    and resolves it to a canonical path relative to the provided project_root.

    Args:
        current_file_path (Path): The absolute path of the file from which the
                                  target_path is being referenced.
        target_path (str): The path to normalize. Can be relative to
                           current_file_path, absolute, or relative to project root.
        project_root (Path): The absolute path to the project's root directory.

    Returns:
        Path: The normalized path relative to the project root.

    Raises:
        ValueError: If the target_path cannot be resolved relative to the project root.
    """
    current_file_path = current_file_path.resolve()
    project_root = project_root.resolve()

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


