#!/usr/bin/env python3
"""
Echo Cleansing Suite v1.0
Consolidates and cleanses Echo directories for optimal structure.

Part of the Echo Civilization framework.
Author: Nathan Poinsette
"""

import os
import hashlib
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class EchoCleanser:
    """Main cleansing engine for Echo directory consolidation."""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.manifest = {
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "operations": [],
            "stats": {
                "files_processed": 0,
                "duplicates_removed": 0,
                "directories_consolidated": 0,
                "bytes_recovered": 0
            }
        }

    def compute_file_hash(self, filepath: Path) -> str:
        """Compute BLAKE3-style hash for file integrity."""
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def scan_directory(self, path: Path) -> Dict[str, List[Path]]:
        """Scan directory for files and group by hash."""
        file_groups = {}

        for filepath in path.rglob('*'):
            if filepath.is_file():
                try:
                    file_hash = self.compute_file_hash(filepath)
                    if file_hash not in file_groups:
                        file_groups[file_hash] = []
                    file_groups[file_hash].append(filepath)
                    self.manifest["stats"]["files_processed"] += 1
                except Exception as e:
                    self.log_operation("error", f"Failed to hash {filepath}: {e}")

        return file_groups

    def find_duplicates(self) -> Dict[str, List[Path]]:
        """Find duplicate files in Echo directories."""
        file_groups = self.scan_directory(self.root_path)
        return {h: paths for h, paths in file_groups.items() if len(paths) > 1}

    def consolidate_directories(self, source_dirs: List[str], target_dir: str) -> None:
        """Consolidate multiple directories into one."""
        target_path = self.root_path / target_dir
        target_path.mkdir(parents=True, exist_ok=True)

        for source in source_dirs:
            source_path = self.root_path / source
            if source_path.exists() and source_path.is_dir():
                for item in source_path.iterdir():
                    dest = target_path / item.name
                    if not dest.exists():
                        shutil.move(str(item), str(dest))
                        self.log_operation("move", f"{item} -> {dest}")

                # Remove empty source directory
                if not any(source_path.iterdir()):
                    source_path.rmdir()
                    self.manifest["stats"]["directories_consolidated"] += 1

    def remove_duplicates(self, keep_strategy: str = "first") -> int:
        """Remove duplicate files keeping one copy."""
        duplicates = self.find_duplicates()
        removed_count = 0
        bytes_recovered = 0

        for file_hash, paths in duplicates.items():
            # Sort to ensure consistent behavior
            sorted_paths = sorted(paths, key=lambda p: str(p))

            # Keep first or newest based on strategy
            if keep_strategy == "newest":
                sorted_paths.sort(key=lambda p: p.stat().st_mtime, reverse=True)

            # Remove all but the first
            for path in sorted_paths[1:]:
                try:
                    bytes_recovered += path.stat().st_size
                    path.unlink()
                    removed_count += 1
                    self.log_operation("remove_duplicate", str(path))
                except Exception as e:
                    self.log_operation("error", f"Failed to remove {path}: {e}")

        self.manifest["stats"]["duplicates_removed"] = removed_count
        self.manifest["stats"]["bytes_recovered"] = bytes_recovered
        return removed_count

    def log_operation(self, op_type: str, message: str) -> None:
        """Log an operation to the manifest."""
        self.manifest["operations"].append({
            "type": op_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })

    def generate_report(self) -> str:
        """Generate a cleansing report."""
        report = [
            "=" * 60,
            "ECHO CLEANSING SUITE - REPORT",
            "=" * 60,
            f"Timestamp: {self.manifest['timestamp']}",
            f"Root Path: {self.root_path}",
            "",
            "STATISTICS:",
            f"  Files Processed: {self.manifest['stats']['files_processed']}",
            f"  Duplicates Removed: {self.manifest['stats']['duplicates_removed']}",
            f"  Directories Consolidated: {self.manifest['stats']['directories_consolidated']}",
            f"  Bytes Recovered: {self.manifest['stats']['bytes_recovered']:,}",
            "",
            "OPERATIONS LOG:",
        ]

        for op in self.manifest["operations"][-20:]:  # Last 20 operations
            report.append(f"  [{op['type']}] {op['message']}")

        report.extend(["", "=" * 60, "Cleansing complete.", "=" * 60])
        return "\n".join(report)

    def save_manifest(self, path: Optional[str] = None) -> None:
        """Save the cleansing manifest to JSON."""
        if path is None:
            path = self.root_path / "cleansing_manifest.json"
        else:
            path = Path(path)

        with open(path, 'w') as f:
            json.dump(self.manifest, f, indent=2)

    def run_full_cleanse(self) -> str:
        """Execute full cleansing procedure."""
        print("Starting Echo Cleansing Suite...")

        # Phase 1: Scan and analyze
        print("Phase 1: Scanning directories...")
        self.scan_directory(self.root_path)

        # Phase 2: Remove duplicates
        print("Phase 2: Removing duplicates...")
        self.remove_duplicates()

        # Phase 3: Generate report
        print("Phase 3: Generating report...")
        report = self.generate_report()

        # Save manifest
        self.save_manifest()

        return report


def main():
    """Main entry point for cleansing suite."""
    import argparse

    parser = argparse.ArgumentParser(description="Echo Cleansing Suite")
    parser.add_argument("--path", default=".", help="Root path to cleanse")
    parser.add_argument("--report-only", action="store_true", help="Generate report without changes")
    args = parser.parse_args()

    cleanser = EchoCleanser(args.path)

    if args.report_only:
        cleanser.scan_directory(cleanser.root_path)
        duplicates = cleanser.find_duplicates()
        print(f"Found {len(duplicates)} duplicate file groups")
        for h, paths in list(duplicates.items())[:5]:
            print(f"  {h[:8]}...: {len(paths)} copies")
    else:
        report = cleanser.run_full_cleanse()
        print(report)


if __name__ == "__main__":
    main()
