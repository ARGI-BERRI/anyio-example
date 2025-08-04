from typing import Literal
from unittest.mock import MagicMock, patch

import pytest
from anyio import Path, TemporaryDirectory

from app.operations import flush_dir, initialize_dirs, main, write_file

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> Literal["asyncio"]:
    return "asyncio"


@patch("app.operations.initialize_dirs")
async def test_main(mock_initialize_dirs: MagicMock) -> None:
    async with TemporaryDirectory() as temp_dir:
        await Path(temp_dir).mkdir(exist_ok=True)
        mock_initialize_dirs.return_value = Path(temp_dir)

        await main()


async def test_initialize_dirs() -> None:
    async with TemporaryDirectory() as temp_dir:
        dest_dir = await initialize_dirs(Path(temp_dir))
        assert dest_dir.exists()
        assert dest_dir.is_dir()


@patch("app.operations.secrets.randbelow", return_value=10)
async def test_write_file(mock_randbelow: MagicMock) -> None:
    async with TemporaryDirectory() as temp_dir:
        dest_path = Path(temp_dir) / "file.txt"
        await write_file(dest_path)
        assert await dest_path.exists()
        assert await dest_path.read_text() == "Hello, World!"

        mock_randbelow.return_value = 0
        with pytest.raises(ValueError):
            await write_file(dest_path)


async def test_flush_dir() -> None:
    async with TemporaryDirectory() as temp_dir:
        dest_dir = Path(temp_dir)

        for i in range(5):
            file_path = dest_dir / f"file_{i}.txt"
            await file_path.write_text("Test content")

        assert len([item async for item in dest_dir.iterdir()]) == 5

        await flush_dir(dest_dir)

        assert len([item async for item in dest_dir.iterdir()]) == 0
