#!/usr/bin/env python3
"""
Echo Forge - Secure Enhanced Version
Includes input validation, security scanning, and improved error handling
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from echo_forge import (
    AIType, TechStack, AppBlueprint,
    IdeaGenerator, ArchitectureDesigner, CodeGenerator
)
from validation import (
    InputValidator, SecurityScanner, PathSanitizer,
    validate_and_sanitize_domain, scan_generated_code
)


class SecureEchoForge:
    """
    Enhanced EchoForge with security and validation
    """

    def __init__(self, output_dir: str = "generated_apps"):
        self.idea_generator = IdeaGenerator()
        self.architect = ArchitectureDesigner()
        self.code_generator = CodeGenerator()
        self.logger = self._setup_logging()
        self.created_apps = []
        self.output_dir = output_dir
        self.security_warnings = []

    def _setup_logging(self) -> logging.Logger:
        """Setup enhanced logging with file output"""
        logger = logging.getLogger("SecureEchoForge")
        logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # File handler
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler(f"logs/echo_forge_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler.setLevel(logging.DEBUG)

        # Formatting
        formatter = logging.Formatter(
            '%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger

    def create_app(
        self,
        domain: str = "general",
        ai_type: Optional[AIType] = None,
        tech_stack: TechStack = TechStack.PYTHON_ML,
        custom_features: Optional[List[str]] = None
    ) -> AppBlueprint:
        """
        Create a new AI application with validation and security scanning

        Args:
            domain: Application domain (validated and sanitized)
            ai_type: Type of AI (auto-generated if not specified)
            tech_stack: Technology stack to use
            custom_features: Additional custom features (validated)

        Returns:
            Blueprint of the created application

        Raises:
            ValueError: If inputs are invalid
        """
        try:
            # Validate domain
            self.logger.info(f"Validating domain: {domain}")
            is_valid, sanitized_domain, error = InputValidator.validate_domain(domain)
            if not is_valid:
                self.logger.error(f"Invalid domain: {error}")
                raise ValueError(f"Invalid domain: {error}")

            self.logger.info(f"Creating AI app in domain: {sanitized_domain}")

            # Validate custom features if provided
            if custom_features:
                is_valid, sanitized_features, error = InputValidator.validate_features(custom_features)
                if not is_valid:
                    self.logger.error(f"Invalid features: {error}")
                    raise ValueError(f"Invalid features: {error}")
                custom_features = sanitized_features

            # 1. Generate idea
            self.logger.info("Step 1: Generating app idea...")
            idea = self.idea_generator.generate_idea(sanitized_domain)

            if ai_type:
                idea["ai_type"] = ai_type

            self.logger.info(f"Generated idea: {idea['description']}")

            # 2. Design architecture
            self.logger.info("Step 2: Designing architecture...")
            architecture = self.architect.design(idea)
            self.logger.info("Architecture designed")

            # 3. Create blueprint
            features = idea["potential_features"]
            if custom_features:
                features.extend(custom_features)

            # Validate app name
            proposed_name = f"{sanitized_domain.title()} {idea['ai_type'].value.title()}"
            is_valid, clean_name, error = InputValidator.validate_app_name(proposed_name)
            if not is_valid:
                self.logger.warning(f"App name validation issue: {error}, using fallback")
                clean_name = f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            blueprint = AppBlueprint(
                name=clean_name,
                description=idea["description"],
                ai_type=idea["ai_type"],
                tech_stack=tech_stack,
                features=features,
                architecture=architecture,
                dependencies=[],
                created_at=datetime.now().isoformat()
            )

            self.logger.info(f"Blueprint created: {blueprint.name}")

            # 4. Generate code
            self.logger.info("Step 3: Generating code...")
            code_files = self.code_generator.generate(blueprint)
            self.logger.info(f"Generated {len(code_files)} files")

            # 5. Security scan
            self.logger.info("Step 4: Security scanning...")
            warnings = scan_generated_code(code_files)
            if warnings:
                self.logger.warning(f"Found {len(warnings)} security warnings")
                for warning in warnings:
                    self.logger.warning(f"  - {warning}")
                self.security_warnings.extend(warnings)

            # 6. Save to disk
            self._save_app(blueprint, code_files)

            self.created_apps.append(blueprint)

            self.logger.info(f"✓ Successfully created: {blueprint.name}")
            return blueprint

        except Exception as e:
            self.logger.error(f"Failed to create app: {str(e)}", exc_info=True)
            raise

    def _save_app(self, blueprint: AppBlueprint, code_files: Dict[str, str]):
        """Save generated app to disk with path validation"""
        # Sanitize app directory name
        app_dir_name = blueprint.name.lower().replace(' ', '_')
        is_safe, app_dir, error = PathSanitizer.sanitize_path(
            self.output_dir,
            app_dir_name
        )

        if not is_safe:
            raise ValueError(f"Unsafe path detected: {error}")

        os.makedirs(app_dir, exist_ok=True)

        # Save all files
        for filename, content in code_files.items():
            # Validate each filename
            is_safe, filepath, error = PathSanitizer.sanitize_path(app_dir, filename)
            if not is_safe:
                self.logger.warning(f"Skipping unsafe file: {filename} - {error}")
                continue

            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'w') as f:
                f.write(content)

        # Save blueprint
        blueprint_path = os.path.join(app_dir, "blueprint.json")
        with open(blueprint_path, 'w') as f:
            json.dump(blueprint.to_dict(), f, indent=2)

        # Save security report if there are warnings
        if self.security_warnings:
            security_report_path = os.path.join(app_dir, "SECURITY_WARNINGS.md")
            with open(security_report_path, 'w') as f:
                f.write("# Security Scan Warnings\n\n")
                for warning in self.security_warnings:
                    f.write(f"- **{warning.get('severity', 'UNKNOWN')}**: {warning}\n")

        self.logger.info(f"App saved to: {app_dir}")

    def create_multiple_apps(self, count: int, domain: str = "general") -> List[AppBlueprint]:
        """Create multiple AI apps at once with validation"""
        if count <= 0 or count > 100:
            raise ValueError("Count must be between 1 and 100")

        self.logger.info(f"Creating {count} AI applications...")

        blueprints = []
        for i in range(count):
            try:
                blueprint = self.create_app(domain=f"{domain}_{i+1}")
                blueprints.append(blueprint)
            except Exception as e:
                self.logger.error(f"Failed to create app {i+1}: {str(e)}")
                # Continue with other apps

        return blueprints

    def list_created_apps(self) -> List[Dict]:
        """List all created applications"""
        return [bp.to_dict() for bp in self.created_apps]

    def get_security_report(self) -> Dict[str, Any]:
        """Get security scan report"""
        return {
            "total_warnings": len(self.security_warnings),
            "high_severity": len([w for w in self.security_warnings if w.get("severity") == "HIGH"]),
            "medium_severity": len([w for w in self.security_warnings if w.get("severity") == "MEDIUM"]),
            "warnings": self.security_warnings
        }


def main():
    """Main entry point with secure version"""
    print("=" * 60)
    print("Echo Forge - Secure Version")
    print("With Input Validation & Security Scanning")
    print("=" * 60)
    print()

    forge = SecureEchoForge()

    try:
        # Example with validation
        print("Creating a Healthcare Chatbot (with security scanning)...")
        chatbot = forge.create_app(
            domain="healthcare",
            ai_type=AIType.CHATBOT,
            tech_stack=TechStack.PYTHON_FASTAPI
        )
        print(f"✓ Created: {chatbot.name}")

        # Show security report
        report = forge.get_security_report()
        print(f"\nSecurity Scan: {report['total_warnings']} warnings found")
        if report['high_severity'] > 0:
            print(f"  ⚠️  {report['high_severity']} HIGH severity issues")

    except ValueError as e:
        print(f"❌ Validation error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
