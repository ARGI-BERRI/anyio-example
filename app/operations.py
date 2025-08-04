"""File operations module for AnyIO test project."""

import secrets

import uvloop
from anyio import Path, create_task_group
from loguru import logger


async def main() -> None:
    """Main entry point for file operations."""
    dest_dir = await initialize_dirs()

    logger.info("Starting file operations...")

    try:
        async with create_task_group() as tg:
            for i in range(10):
                file_path = dest_dir / f"file_{i}.txt"
                tg.start_soon(write_file, file_path)

    except* Exception:
        logger.exception("An error occurred during file operations!")

    finally:
        await flush_dir(dest_dir)

    logger.success("File operations completed.")


async def initialize_dirs(pwd: Path | None = None) -> Path:
    """Initialize the directory structure.

    Args:
        pwd (Path | None, optional): The parent directory path. Defaults to None.

    Returns:
        Path: The path to the destination directory.
    """
    if pwd is None:
        pwd = await Path.cwd()

    dest_dir = pwd / "out"
    await dest_dir.mkdir(exist_ok=True)

    logger.debug(f"Current working directory: {pwd}")
    logger.debug(f"Destination path: {dest_dir}")

    return dest_dir


async def write_file(dest_path: Path) -> None:
    """Write a file with a simulated error.

    Args:
        dest_path (Path): The path to the destination file.

    Raises:
        ValueError: If a simulated error occurs during file writing.
    """
    await dest_path.write_text("Hello, World!")

    if secrets.randbelow(10) < 5:
        raise ValueError(f"Simulated error during file write: {dest_path.name}")


async def flush_dir(dir_path: Path) -> None:
    """Flush the contents of a directory.

    Args:
        dir_path (Path): The path to the directory to flush.
    """
    async for item in dir_path.iterdir():
        await item.unlink()


if __name__ == "__main__":
    logger.add("./logs/{time}.log", level="DEBUG", retention=3)

    uvloop.install()
    uvloop.run(main())
