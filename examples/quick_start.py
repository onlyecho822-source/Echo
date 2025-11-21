#!/usr/bin/env python3
"""
Echo Forge - Quick Start Examples
Demonstrates how to use Echo Forge to create AI applications
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from echo_forge import EchoForge, AIType, TechStack


def example_1_simple_chatbot():
    """Create a simple chatbot"""
    print("\n" + "="*60)
    print("Example 1: Creating a Simple Chatbot")
    print("="*60 + "\n")

    forge = EchoForge()

    chatbot = forge.create_app(
        domain="customer_service",
        ai_type=AIType.CHATBOT,
        tech_stack=TechStack.PYTHON_FASTAPI
    )

    print(f"✓ Created: {chatbot.name}")
    print(f"  Type: {chatbot.ai_type.value}")
    print(f"  Features: {', '.join(chatbot.features[:3])}")
    print(f"  Location: generated_apps/{chatbot.name.lower().replace(' ', '_')}/")


def example_2_data_analyzer():
    """Create a data analysis AI"""
    print("\n" + "="*60)
    print("Example 2: Creating a Data Analyzer")
    print("="*60 + "\n")

    forge = EchoForge()

    analyzer = forge.create_app(
        domain="business_intelligence",
        ai_type=AIType.ANALYZER,
        tech_stack=TechStack.PYTHON_ML,
        custom_features=[
            "Real-time dashboard",
            "Predictive insights",
            "Export to PDF/Excel"
        ]
    )

    print(f"✓ Created: {analyzer.name}")
    print(f"  Type: {analyzer.ai_type.value}")
    print(f"  Tech Stack: {analyzer.tech_stack.value}")
    print(f"  Custom Features: {', '.join(analyzer.features[-3:])}")


def example_3_autonomous_agent():
    """Create an autonomous agent"""
    print("\n" + "="*60)
    print("Example 3: Creating an Autonomous Agent")
    print("="*60 + "\n")

    forge = EchoForge()

    agent = forge.create_app(
        domain="workflow_automation",
        ai_type=AIType.AGENT,
        tech_stack=TechStack.AUTONOMOUS_AGENT,
        custom_features=[
            "Multi-step task planning",
            "Tool integration",
            "Learning from feedback"
        ]
    )

    print(f"✓ Created: {agent.name}")
    print(f"  Type: {agent.ai_type.value}")
    print(f"  State Machine: Planning → Executing → Learning")
    print(f"  Features: {len(agent.features)} capabilities")


def example_4_content_generator():
    """Create a content generation AI"""
    print("\n" + "="*60)
    print("Example 4: Creating a Content Generator")
    print("="*60 + "\n")

    forge = EchoForge()

    generator = forge.create_app(
        domain="marketing",
        ai_type=AIType.GENERATOR,
        tech_stack=TechStack.PYTHON_FASTAPI,
        custom_features=[
            "Multiple content formats",
            "SEO optimization",
            "Brand voice consistency"
        ]
    )

    print(f"✓ Created: {generator.name}")
    print(f"  Type: {generator.ai_type.value}")
    print(f"  Output Formats: Text, HTML, Markdown")


def example_5_multi_app_generation():
    """Create multiple AI apps at once"""
    print("\n" + "="*60)
    print("Example 5: Creating Multiple Apps (AI Factory)")
    print("="*60 + "\n")

    forge = EchoForge()

    print("Creating 3 specialized AI applications...")
    apps = forge.create_multiple_apps(count=3, domain="enterprise")

    print(f"\n✓ Created {len(apps)} applications:")
    for i, app in enumerate(apps, 1):
        print(f"  {i}. {app.name}")
        print(f"     Type: {app.ai_type.value}")
        print(f"     Stack: {app.tech_stack.value}")


def example_6_nodejs_api():
    """Create a Node.js API"""
    print("\n" + "="*60)
    print("Example 6: Creating a Node.js API")
    print("="*60 + "\n")

    forge = EchoForge()

    api = forge.create_app(
        domain="e_commerce",
        ai_type=AIType.ASSISTANT,
        tech_stack=TechStack.JAVASCRIPT_NODE
    )

    print(f"✓ Created: {api.name}")
    print(f"  Runtime: Node.js + Express")
    print(f"  API Endpoints: /, /health, /process")
    print(f"  To run: cd generated_apps/{api.name.lower().replace(' ', '_')} && npm install && npm start")


def example_7_specialized_apps():
    """Create specialized AI apps for different use cases"""
    print("\n" + "="*60)
    print("Example 7: Creating Specialized AI Suite")
    print("="*60 + "\n")

    forge = EchoForge()

    apps = [
        ("medical_diagnosis", AIType.CLASSIFIER, "Healthcare classification system"),
        ("stock_prediction", AIType.PREDICTOR, "Financial forecasting tool"),
        ("customer_support", AIType.CHATBOT, "24/7 support assistant"),
        ("code_review", AIType.ANALYZER, "Automated code analysis"),
        ("task_orchestrator", AIType.ORCHESTRATOR, "Multi-agent coordinator")
    ]

    print("Building specialized AI suite...")
    created = []

    for domain, ai_type, description in apps:
        app = forge.create_app(domain=domain, ai_type=ai_type)
        created.append((app.name, description))

    print(f"\n✓ Created {len(created)} specialized AIs:")
    for name, desc in created:
        print(f"  • {name}")
        print(f"    → {desc}")


def example_8_recursive_ai():
    """Create an AI that creates AIs (meta-level)"""
    print("\n" + "="*60)
    print("Example 8: Creating Recursive AI (Meta-Builder)")
    print("="*60 + "\n")

    forge = EchoForge()

    meta_builder = forge.create_app(
        domain="ai_factory",
        ai_type=AIType.ORCHESTRATOR,
        tech_stack=TechStack.PYTHON_ML,
        custom_features=[
            "Dynamic AI generation",
            "Architecture optimization",
            "Performance monitoring",
            "Self-improvement loops"
        ]
    )

    print(f"✓ Created: {meta_builder.name}")
    print(f"  Type: Meta-AI (AI that builds AI)")
    print(f"  Capability: Can generate other AI applications")
    print(f"  Recursion Level: 2nd order intelligence")
    print("\n  This AI can now create other AIs! 🤖→🤖→🤖")


def interactive_demo():
    """Interactive demo mode"""
    print("\n" + "="*60)
    print("Interactive Mode: Build Your Own AI")
    print("="*60 + "\n")

    forge = EchoForge()

    print("Let's build a custom AI together!\n")

    # Get domain
    domain = input("Enter application domain (e.g., healthcare, finance, education): ").strip()
    if not domain:
        domain = "custom"

    # Get AI type
    print("\nAvailable AI Types:")
    for i, ai_type in enumerate(AIType, 1):
        print(f"  {i}. {ai_type.value}")

    choice = input("\nSelect AI type (1-8): ").strip()
    ai_types = list(AIType)
    ai_type = ai_types[int(choice)-1] if choice.isdigit() and 1 <= int(choice) <= 8 else AIType.ASSISTANT

    # Get tech stack
    print("\nAvailable Tech Stacks:")
    for i, stack in enumerate(TechStack, 1):
        print(f"  {i}. {stack.value}")

    choice = input("\nSelect tech stack (1-4): ").strip()
    stacks = list(TechStack)
    tech_stack = stacks[int(choice)-1] if choice.isdigit() and 1 <= int(choice) <= 4 else TechStack.PYTHON_ML

    # Create app
    print("\n🔧 Building your AI application...\n")

    app = forge.create_app(
        domain=domain,
        ai_type=ai_type,
        tech_stack=tech_stack
    )

    print(f"\n✓ Success! Created: {app.name}")
    print(f"  Location: generated_apps/{app.name.lower().replace(' ', '_')}/")
    print(f"  Type: {app.ai_type.value}")
    print(f"  Stack: {app.tech_stack.value}")
    print(f"\n  Ready to deploy! 🚀")


def main():
    """Main entry point"""
    print("=" * 60)
    print("Echo Forge - Quick Start Examples")
    print("Meta-AI Application Builder")
    print("=" * 60)

    if len(sys.argv) > 1:
        example = sys.argv[1]

        examples = {
            "1": example_1_simple_chatbot,
            "2": example_2_data_analyzer,
            "3": example_3_autonomous_agent,
            "4": example_4_content_generator,
            "5": example_5_multi_app_generation,
            "6": example_6_nodejs_api,
            "7": example_7_specialized_apps,
            "8": example_8_recursive_ai,
            "interactive": interactive_demo,
            "all": lambda: [ex() for ex in [
                example_1_simple_chatbot,
                example_2_data_analyzer,
                example_3_autonomous_agent,
                example_4_content_generator,
                example_5_multi_app_generation,
                example_6_nodejs_api,
                example_7_specialized_apps,
                example_8_recursive_ai
            ]]
        }

        example_fn = examples.get(example)
        if example_fn:
            example_fn()
        else:
            print(f"\nUnknown example: {example}")
            print_usage()
    else:
        print_usage()


def print_usage():
    """Print usage instructions"""
    print("\nUsage:")
    print("  python quick_start.py [example_number|all|interactive]")
    print("\nExamples:")
    print("  python quick_start.py 1            # Run example 1")
    print("  python quick_start.py all          # Run all examples")
    print("  python quick_start.py interactive  # Interactive mode")
    print("\nAvailable Examples:")
    print("  1 - Simple Chatbot (FastAPI)")
    print("  2 - Data Analyzer (Python ML)")
    print("  3 - Autonomous Agent")
    print("  4 - Content Generator")
    print("  5 - Multi-App Generation (Factory)")
    print("  6 - Node.js API")
    print("  7 - Specialized AI Suite")
    print("  8 - Recursive AI (Meta-Builder)")
    print()


if __name__ == "__main__":
    main()
