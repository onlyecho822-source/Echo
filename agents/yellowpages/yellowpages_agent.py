#!/usr/bin/env python3
"""
Yellowpages Agent - Builds and maintains digital directory of all repository assets
Creates searchable index, asset maps, and documentation catalogs
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.base_agent import EchoAgent

class YellowpagesAgent(EchoAgent):
    """Agent that builds digital directory of repository assets"""
    
    def __init__(self):
        super().__init__(
            agent_name='yellowpages_001',
            agent_type='yellowpages',
            work_interval=1200  # 20 minutes
        )
        self.yellowpages_dir = os.path.join(self.repo_path, 'docs', 'yellowpages')
        os.makedirs(self.yellowpages_dir, exist_ok=True)
    
    def catalog_files(self) -> Dict[str, List[Dict[str, Any]]]:
        """Catalog all files in repository by type"""
        catalog = defaultdict(list)
        
        file_types = {
            'documentation': ['.md', '.txt', '.pdf'],
            'code': ['.py', '.js', '.ts', '.tsx', '.jsx'],
            'configuration': ['.json', '.yaml', '.yml', '.toml', '.ini'],
            'scripts': ['.sh', '.bash', '.ps1', '.bat'],
            'data': ['.csv', '.jsonl', '.sql'],
            'images': ['.png', '.jpg', '.jpeg', '.gif', '.svg'],
            'other': []
        }
        
        for root, dirs, files in os.walk(self.repo_path):
            # Skip hidden directories and node_modules
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            
            for file in files:
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, self.repo_path)
                file_ext = os.path.splitext(file)[1].lower()
                
                # Categorize file
                category = 'other'
                for cat, extensions in file_types.items():
                    if file_ext in extensions:
                        category = cat
                        break
                
                # Get file stats
                try:
                    stats = os.stat(filepath)
                    file_info = {
                        'path': rel_path,
                        'name': file,
                        'size': stats.st_size,
                        'modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                        'extension': file_ext
                    }
                    catalog[category].append(file_info)
                except:
                    pass
        
        return dict(catalog)
    
    def build_directory_tree(self) -> str:
        """Build visual directory tree"""
        tree_lines = ["# Echo Universe Directory Tree\n"]
        tree_lines.append(f"*Generated: {datetime.utcnow().isoformat()}*\n\n")
        tree_lines.append("```\n")
        
        def add_directory(path, prefix="", is_last=True):
            """Recursively add directory to tree"""
            try:
                entries = sorted(os.listdir(path))
                # Filter out hidden files and node_modules
                entries = [e for e in entries if not e.startswith('.') and e != 'node_modules']
                
                for i, entry in enumerate(entries):
                    entry_path = os.path.join(path, entry)
                    is_last_entry = (i == len(entries) - 1)
                    
                    connector = "└── " if is_last_entry else "├── "
                    tree_lines.append(f"{prefix}{connector}{entry}\n")
                    
                    if os.path.isdir(entry_path):
                        extension = "    " if is_last_entry else "│   "
                        add_directory(entry_path, prefix + extension, is_last_entry)
            except PermissionError:
                pass
        
        tree_lines.append(f"{os.path.basename(self.repo_path)}/\n")
        add_directory(self.repo_path)
        tree_lines.append("```\n")
        
        return ''.join(tree_lines)
    
    def create_asset_index(self, catalog: Dict[str, List[Dict[str, Any]]]) -> str:
        """Create searchable asset index"""
        index_file = os.path.join(self.yellowpages_dir, 'ASSET_INDEX.md')
        
        total_files = sum(len(files) for files in catalog.values())
        total_size = sum(
            sum(f['size'] for f in files)
            for files in catalog.values()
        )
        
        index_content = f"""# Echo Universe Asset Index
*Last updated: {datetime.utcnow().isoformat()}*

## Repository Statistics
- **Total Files:** {total_files:,}
- **Total Size:** {total_size / 1024 / 1024:.2f} MB
- **Categories:** {len(catalog)}

## Assets by Category

"""
        
        for category, files in sorted(catalog.items()):
            category_size = sum(f['size'] for f in files)
            index_content += f"### {category.title()} ({len(files)} files, {category_size / 1024:.2f} KB)\n\n"
            
            # Sort by size (largest first)
            sorted_files = sorted(files, key=lambda x: x['size'], reverse=True)
            
            # Show top 20 files in each category
            for file_info in sorted_files[:20]:
                size_kb = file_info['size'] / 1024
                index_content += f"- `{file_info['path']}` ({size_kb:.1f} KB)\n"
            
            if len(files) > 20:
                index_content += f"\n*...and {len(files) - 20} more files*\n"
            
            index_content += "\n"
        
        index_content += """
## Quick Links

### Core Documentation
- [Master Roadmap](../../planning/MASTER_ROADMAP.md)
- [Transformation Strategy](../../global-nexus/ECHO_UNIVERSE_TRANSFORMATION_STRATEGY.md)
- [72-Hour Execution Plan](../../global-nexus/72_HOUR_EXECUTION_PLAN.md)

### Agent Documentation
- [Planner Agent](../../agents/planner/planner_agent.py)
- [Cleaner Agent](../../agents/cleaner/cleaner_agent.py)
- [Yellowpages Agent](../../agents/yellowpages/yellowpages_agent.py)

### Enterprise Materials
- [Enterprise Partnership Strategy](../../global-nexus/ENTERPRISE_PARTNERSHIP_STRATEGY.md)
- [Presentation Script](../../global-nexus/PRESENTATION_SCRIPT.md)

---

*This index is automatically updated every {self.work_interval // 60} minutes by Yellowpages Agent*

∇θ — chain sealed, truth preserved.
"""
        
        with open(index_file, 'w') as f:
            f.write(index_content)
        
        return index_file
    
    def create_documentation_map(self, catalog: Dict[str, List[Dict[str, Any]]]) -> str:
        """Create map of all documentation"""
        map_file = os.path.join(self.yellowpages_dir, 'DOCUMENTATION_MAP.md')
        
        docs = catalog.get('documentation', [])
        
        # Organize by directory
        docs_by_dir = defaultdict(list)
        for doc in docs:
            dir_name = os.path.dirname(doc['path']) or 'root'
            docs_by_dir[dir_name].append(doc)
        
        map_content = f"""# Echo Universe Documentation Map
*Last updated: {datetime.utcnow().isoformat()}*

## Overview
Total documentation files: {len(docs)}

## Documentation by Directory

"""
        
        for dir_name, dir_docs in sorted(docs_by_dir.items()):
            map_content += f"### {dir_name}\n\n"
            
            for doc in sorted(dir_docs, key=lambda x: x['name']):
                map_content += f"- [{doc['name']}](../../{doc['path']})\n"
            
            map_content += "\n"
        
        map_content += """
## Documentation Categories

### Strategic Planning
Documents related to strategy, roadmaps, and high-level planning.

### Technical Documentation
Code documentation, API references, and implementation guides.

### Operational Procedures
Agent documentation, deployment procedures, and operational guides.

### Business Materials
Partnership strategies, presentations, and business development.

---

*This map is automatically updated every {self.work_interval // 60} minutes by Yellowpages Agent*

∇θ — chain sealed, truth preserved.
"""
        
        with open(map_file, 'w') as f:
            f.write(map_content)
        
        return map_file
    
    def create_quick_reference(self) -> str:
        """Create quick reference guide"""
        ref_file = os.path.join(self.yellowpages_dir, 'QUICK_REFERENCE.md')
        
        ref_content = f"""# Echo Universe Quick Reference
*Last updated: {datetime.utcnow().isoformat()}*

## Essential Commands

### Agent Operations
```bash
# Run Planner Agent (autopilot)
python3 agents/planner/planner_agent.py

# Run Cleaner Agent (autopilot)
python3 agents/cleaner/cleaner_agent.py

# Run Yellowpages Agent (autopilot)
python3 agents/yellowpages/yellowpages_agent.py

# Run agent once (testing)
python3 agents/planner/planner_agent.py --once
```

### Git Operations
```bash
# Pull latest changes
git pull origin main

# Push changes
git add .
git commit -m "Your message"
git push origin main

# Create branch
git checkout -b branch-name
git push origin branch-name

# Create pull request
gh pr create --title "Title" --body "Description"
```

### Repository Navigation
```bash
# Core directories
cd agents/          # Autonomous agents
cd planning/        # Plans and roadmaps
cd global-nexus/    # Enterprise strategy
cd docs/            # Documentation
cd ledgers/         # Constitutional Ledger

# View agent activity
cat ledgers/agent_activity/planner_001_*.jsonl
cat ledgers/agent_activity/cleaner_001_*.jsonl
cat ledgers/agent_activity/yellowpages_001_*.jsonl
```

## Key Files

### Strategic Documents
- `global-nexus/ECHO_UNIVERSE_TRANSFORMATION_STRATEGY.md` - Complete transformation strategy
- `global-nexus/72_HOUR_EXECUTION_PLAN.md` - Detailed execution plan
- `global-nexus/ENTERPRISE_PARTNERSHIP_STRATEGY.md` - Partnership strategy
- `global-nexus/PRESENTATION_SCRIPT.md` - Enterprise pitch script

### Planning Documents
- `planning/MASTER_ROADMAP.md` - Master project roadmap
- `planning/daily_plan_YYYY-MM-DD.md` - Daily work plans

### Agent State
- `agents/shared/state/planner_001.json` - Planner agent state
- `agents/shared/state/cleaner_001.json` - Cleaner agent state
- `agents/shared/state/yellowpages_001.json` - Yellowpages agent state

## Directory Structure

```
Echo/
├── agents/              # Autonomous agents
│   ├── planner/        # Planning agent
│   ├── cleaner/        # Cleaning agent
│   ├── yellowpages/    # Directory agent
│   └── shared/         # Shared utilities
├── global-nexus/       # Enterprise strategy
├── planning/           # Plans and roadmaps
├── ledgers/            # Constitutional Ledger
├── docs/               # Documentation
│   └── yellowpages/    # Digital directory
└── artifacts/          # Build artifacts
```

## Agent Schedules

- **Planner Agent:** Every 10 minutes
- **Cleaner Agent:** Every 15 minutes
- **Yellowpages Agent:** Every 20 minutes

## Emergency Procedures

### Stop All Agents
```bash
pkill -f "python3.*agent.py"
```

### View Agent Logs
```bash
tail -f ledgers/agent_activity/*.jsonl
```

### Reset Agent State
```bash
rm agents/shared/state/*.json
```

---

*This reference is automatically updated every {self.work_interval // 60} minutes by Yellowpages Agent*

∇θ — chain sealed, truth preserved.
"""
        
        with open(ref_file, 'w') as f:
            f.write(ref_content)
        
        return ref_file
    
    def do_work(self) -> Dict[str, Any]:
        """Perform yellowpages work"""
        results = {
            'tasks_completed': 0,
            'files_cataloged': 0,
            'files_created': []
        }
        
        # Catalog all files
        print("Cataloging repository files...")
        catalog = self.catalog_files()
        results['files_cataloged'] = sum(len(files) for files in catalog.values())
        print(f"✓ Cataloged {results['files_cataloged']} files across {len(catalog)} categories")
        results['tasks_completed'] += 1
        
        # Create asset index
        print("Creating asset index...")
        index_file = self.create_asset_index(catalog)
        results['files_created'].append(index_file)
        print(f"✓ Asset index created: {index_file}")
        results['tasks_completed'] += 1
        
        # Create documentation map
        print("Creating documentation map...")
        map_file = self.create_documentation_map(catalog)
        results['files_created'].append(map_file)
        print(f"✓ Documentation map created: {map_file}")
        results['tasks_completed'] += 1
        
        # Create quick reference
        print("Creating quick reference...")
        ref_file = self.create_quick_reference()
        results['files_created'].append(ref_file)
        print(f"✓ Quick reference created: {ref_file}")
        results['tasks_completed'] += 1
        
        # Build directory tree (only once per day to avoid spam)
        if self.cycle_count % 72 == 1:  # Once per day (assuming 20-min intervals)
            print("Building directory tree...")
            tree_content = self.build_directory_tree()
            tree_file = os.path.join(self.yellowpages_dir, 'DIRECTORY_TREE.md')
            with open(tree_file, 'w') as f:
                f.write(tree_content)
            results['files_created'].append(tree_file)
            print(f"✓ Directory tree created: {tree_file}")
            results['tasks_completed'] += 1
        
        # Sync to GitHub
        print("Syncing to GitHub...")
        self.git_sync(
            f"Yellowpages Agent: Updated digital directory ({results['files_cataloged']} files cataloged, Cycle {self.cycle_count})",
            files=results['files_created']
        )
        
        return results

if __name__ == '__main__':
    agent = YellowpagesAgent()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        agent.run_once()
    else:
        agent.run_autopilot()
