#!/usr/bin/env python3
"""
Aletheia Methods Registry
==========================
Stores protocols, instrument configs, script hashes, and runtime
environment manifests for reproducible analysis.

Author: Echo Nexus Omega
Version: 1.0.0
"""

import json
import hashlib
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class MethodEntry:
    """Registry entry for a reproducible method."""
    method_id: str
    name: str
    version: str
    description: str

    # Pipeline details
    pipeline_type: str
    scripts: List[Dict[str, str]]  # [{name, version, hash, path}]
    parameters: Dict[str, Any]

    # Environment
    environment_hash: str
    required_packages: Dict[str, str]

    # Validation
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    tolerance: Dict[str, float]

    # Metadata
    created_at: str
    created_by: str
    references: List[str]
    status: str  # "active", "deprecated", "draft"


@dataclass
class InstrumentConfig:
    """Configuration for an analysis instrument."""
    config_id: str
    instrument_make: str
    instrument_model: str
    serial_number: Optional[str]
    calibration_date: str
    parameters: Dict[str, Any]
    validation_data: Dict[str, Any]
    created_at: str


class MethodsRegistry:
    """
    Registry for analysis methods and instrument configurations.

    Enables reproducibility by tracking exact versions, parameters,
    and environment specifications.
    """

    def __init__(self, registry_path: str):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)

        self.methods_file = self.registry_path / "methods.json"
        self.instruments_file = self.registry_path / "instruments.json"

        self.methods: Dict[str, MethodEntry] = {}
        self.instruments: Dict[str, InstrumentConfig] = {}

        self._load_registry()

    def _load_registry(self):
        """Load registry from disk."""
        if self.methods_file.exists():
            with open(self.methods_file) as f:
                data = json.load(f)
                self.methods = {k: MethodEntry(**v) for k, v in data.items()}

        if self.instruments_file.exists():
            with open(self.instruments_file) as f:
                data = json.load(f)
                self.instruments = {k: InstrumentConfig(**v) for k, v in data.items()}

    def _save_registry(self):
        """Save registry to disk."""
        with open(self.methods_file, "w") as f:
            json.dump({k: asdict(v) for k, v in self.methods.items()}, f, indent=2)

        with open(self.instruments_file, "w") as f:
            json.dump({k: asdict(v) for k, v in self.instruments.items()}, f, indent=2)

    def register_method(
        self,
        name: str,
        version: str,
        description: str,
        pipeline_type: str,
        scripts: List[Dict[str, str]],
        parameters: Dict[str, Any],
        environment_hash: str,
        required_packages: Dict[str, str],
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        tolerance: Dict[str, float],
        created_by: str,
        references: List[str] = None
    ) -> str:
        """
        Register a new analysis method.

        Returns: method_id
        """
        method_id = f"METHOD-{name.upper().replace(' ', '-')}-{version.replace('.', '')}"

        if method_id in self.methods:
            # Update existing with new version
            old_entry = self.methods[method_id]
            old_entry.status = "deprecated"
            method_id = f"{method_id}-{secrets.token_hex(4).upper()}"

        entry = MethodEntry(
            method_id=method_id,
            name=name,
            version=version,
            description=description,
            pipeline_type=pipeline_type,
            scripts=scripts,
            parameters=parameters,
            environment_hash=environment_hash,
            required_packages=required_packages,
            input_schema=input_schema,
            output_schema=output_schema,
            tolerance=tolerance,
            created_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            created_by=created_by,
            references=references or [],
            status="active"
        )

        self.methods[method_id] = entry
        self._save_registry()

        return method_id

    def register_instrument(
        self,
        instrument_make: str,
        instrument_model: str,
        serial_number: Optional[str],
        calibration_date: str,
        parameters: Dict[str, Any],
        validation_data: Dict[str, Any] = None
    ) -> str:
        """
        Register an instrument configuration.

        Returns: config_id
        """
        config_id = f"INST-{instrument_make[:4].upper()}-{instrument_model[:4].upper()}-{secrets.token_hex(4).upper()}"

        config = InstrumentConfig(
            config_id=config_id,
            instrument_make=instrument_make,
            instrument_model=instrument_model,
            serial_number=serial_number,
            calibration_date=calibration_date,
            parameters=parameters,
            validation_data=validation_data or {},
            created_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        self.instruments[config_id] = config
        self._save_registry()

        return config_id

    def get_method(self, method_id: str) -> Optional[MethodEntry]:
        """Get a method by ID."""
        return self.methods.get(method_id)

    def get_instrument(self, config_id: str) -> Optional[InstrumentConfig]:
        """Get an instrument config by ID."""
        return self.instruments.get(config_id)

    def find_methods(
        self,
        pipeline_type: Optional[str] = None,
        status: str = "active"
    ) -> List[MethodEntry]:
        """Find methods matching criteria."""
        results = []
        for entry in self.methods.values():
            if status and entry.status != status:
                continue
            if pipeline_type and entry.pipeline_type != pipeline_type:
                continue
            results.append(entry)
        return results

    def validate_method_inputs(
        self,
        method_id: str,
        inputs: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate inputs against method schema.

        Returns: (is_valid, list of errors)
        """
        method = self.get_method(method_id)
        if not method:
            return False, [f"Method not found: {method_id}"]

        errors = []
        schema = method.input_schema

        # Check required fields
        for field in schema.get("required", []):
            if field not in inputs:
                errors.append(f"Missing required input: {field}")

        return len(errors) == 0, errors

    def create_method_manifest(self, method_id: str) -> Dict[str, Any]:
        """
        Create a complete method manifest for reproducibility.

        Returns manifest suitable for inclusion in derivation graph.
        """
        method = self.get_method(method_id)
        if not method:
            raise KeyError(f"Method not found: {method_id}")

        return {
            "method_id": method.method_id,
            "name": method.name,
            "version": method.version,
            "pipeline_type": method.pipeline_type,
            "scripts": method.scripts,
            "parameters": method.parameters,
            "environment": {
                "hash": method.environment_hash,
                "packages": method.required_packages
            },
            "schemas": {
                "input": method.input_schema,
                "output": method.output_schema
            },
            "tolerance": method.tolerance,
            "references": method.references,
            "registry_timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

    def export_registry(self) -> Dict[str, Any]:
        """Export entire registry for backup/transfer."""
        return {
            "methods": {k: asdict(v) for k, v in self.methods.items()},
            "instruments": {k: asdict(v) for k, v in self.instruments.items()},
            "exported_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }


# Type hint
from typing import Tuple


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Aletheia Methods Registry CLI")
    parser.add_argument("--registry", default="./registry_data")
    subparsers = parser.add_subparsers(dest="command")

    # List methods
    list_parser = subparsers.add_parser("list", help="List methods")
    list_parser.add_argument("--type", help="Filter by pipeline type")

    # Get method
    get_parser = subparsers.add_parser("get", help="Get method details")
    get_parser.add_argument("--id", required=True)

    # Export
    export_parser = subparsers.add_parser("export", help="Export registry")
    export_parser.add_argument("--output", "-o", required=True)

    args = parser.parse_args()

    registry = MethodsRegistry(args.registry)

    if args.command == "list":
        methods = registry.find_methods(pipeline_type=args.type)
        for m in methods:
            print(f"{m.method_id}: {m.name} v{m.version} [{m.status}]")

    elif args.command == "get":
        method = registry.get_method(args.id)
        if method:
            print(json.dumps(asdict(method), indent=2))
        else:
            print(f"Method not found: {args.id}")

    elif args.command == "export":
        data = registry.export_registry()
        with open(args.output, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Registry exported to {args.output}")

    else:
        parser.print_help()
