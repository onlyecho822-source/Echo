"""File collector for file-based sources."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from echo_engine.collectors.base import BaseCollector
from echo_engine.core.models import Source, SourceType
from echo_engine.core.exceptions import SourceNotFoundError, CollectionError


class FileCollector(BaseCollector):
    """Collector for file-based sources."""

    SUPPORTED_EXTENSIONS = {
        '.txt', '.md', '.json', '.xml', '.html', '.htm',
        '.csv', '.log', '.py', '.js', '.yaml', '.yml',
        '.rst', '.tex', '.rtf',
    }

    def collect(
        self,
        filepath: str,
        name: Optional[str] = None,
        encoding: str = "utf-8",
        metadata: Optional[dict] = None,
    ) -> Source:
        """
        Collect a file as a source.

        Args:
            filepath: Path to the file
            name: Optional name (defaults to filename)
            encoding: File encoding
            metadata: Additional metadata

        Returns:
            A Source object
        """
        if not self.validate_input(filepath):
            raise SourceNotFoundError(f"Cannot collect file: {filepath}")

        path = Path(filepath)

        try:
            with open(filepath, "r", encoding=encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(filepath, "r", encoding="latin-1") as f:
                    content = f.read()
            except Exception as e:
                raise CollectionError(f"Failed to read file: {e}")
        except Exception as e:
            raise CollectionError(f"Failed to read file: {e}")

        # Get file metadata
        file_stats = os.stat(filepath)
        file_timestamp = datetime.fromtimestamp(file_stats.st_mtime)

        processed_content = self.preprocess(content)

        file_metadata = {
            "file_size": file_stats.st_size,
            "extension": path.suffix,
            "absolute_path": str(path.absolute()),
            **(metadata or {}),
        }

        return Source(
            name=name or path.name,
            source_type=self.get_source_type(),
            content=processed_content,
            filepath=str(path.absolute()),
            timestamp=file_timestamp,
            metadata=file_metadata,
        )

    def validate_input(self, filepath: str) -> bool:
        """Validate file can be collected."""
        if not filepath:
            return False

        path = Path(filepath)

        if not path.exists():
            return False

        if not path.is_file():
            return False

        # Check if extension is supported
        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return False

        return True

    def get_source_type(self) -> SourceType:
        """Get source type."""
        return SourceType.FILE

    def collect_directory(
        self,
        directory: str,
        pattern: str = "*",
        recursive: bool = False,
        encoding: str = "utf-8",
    ) -> list[Source]:
        """
        Collect all matching files from a directory.

        Args:
            directory: Directory path
            pattern: Glob pattern for files
            recursive: Whether to search recursively
            encoding: File encoding

        Returns:
            List of Source objects
        """
        dir_path = Path(directory)

        if not dir_path.is_dir():
            raise SourceNotFoundError(f"Directory not found: {directory}")

        sources = []
        glob_method = dir_path.rglob if recursive else dir_path.glob

        for filepath in glob_method(pattern):
            if filepath.is_file() and filepath.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                try:
                    source = self.collect(str(filepath), encoding=encoding)
                    sources.append(source)
                except (CollectionError, SourceNotFoundError):
                    # Skip files that can't be collected
                    continue

        return sources

    def collect_multiple(
        self,
        filepaths: list[str],
        encoding: str = "utf-8",
    ) -> list[Source]:
        """
        Collect multiple files.

        Args:
            filepaths: List of file paths
            encoding: File encoding

        Returns:
            List of Source objects
        """
        sources = []
        for filepath in filepaths:
            try:
                source = self.collect(filepath, encoding=encoding)
                sources.append(source)
            except (CollectionError, SourceNotFoundError):
                continue
        return sources
