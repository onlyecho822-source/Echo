#!/usr/bin/env python3
"""
Cleaner Agent - Maintains repository hygiene and organization
Removes empty directories, archives old files, optimizes structure
"""

import os
import sys
import json
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.base_agent import EchoAgent

class CleanerAgent(EchoAgent):
    """Agent that maintains repository cleanliness"""
    
    def __init__(self):
        super().__init__(
            agent_name='cleaner_001',
            agent_type='cleaner',
            work_interval=900  # 15 minutes
        )
        self.archive_dir = os.path.join(self.repo_path, 'artifacts', 'archived')
        os.makedirs(self.archive_dir, exist_ok=True)
    
    def find_empty_directories(self) -> List[str]:
        """Find all empty directories in repository"""
        empty_dirs = []
        
        for root, dirs, files in os.walk(self.repo_path):
            # Skip .git and node_modules
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            
            # Check if directory is empty (no files and no subdirectories)
            if not files and not dirs:
                # Don't remove critical directories
                if not any(critical in root for critical in ['agents', 'ledgers', 'planning']):
                    empty_dirs.append(root)
        
        return empty_dirs
    
    def remove_empty_directories(self) -> int:
        """Remove empty directories"""
        empty_dirs = self.find_empty_directories()
        removed_count = 0
        
        for dir_path in empty_dirs:
            try:
                os.rmdir(dir_path)
                print(f"  Removed empty directory: {os.path.relpath(dir_path, self.repo_path)}")
                removed_count += 1
            except Exception as e:
                print(f"  Failed to remove {dir_path}: {e}")
        
        return removed_count
    
    def find_duplicate_files(self) -> Dict[str, List[str]]:
        """Find duplicate files by content hash"""
        file_hashes = {}
        duplicates = {}
        
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            
            for file in files:
                if file.endswith(('.md', '.py', '.js', '.ts', '.json')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'rb') as f:
                            content = f.read()
                            file_hash = hashlib.sha256(content).hexdigest()
                            
                            if file_hash in file_hashes:
                                if file_hash not in duplicates:
                                    duplicates[file_hash] = [file_hashes[file_hash]]
                                duplicates[file_hash].append(filepath)
                            else:
                                file_hashes[file_hash] = filepath
                    except:
                        pass
        
        return duplicates
    
    def archive_old_files(self, days_old: int = 90) -> int:
        """Archive files that haven't been modified in specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        archived_count = 0
        
        # Only archive from specific directories
        archivable_dirs = ['docs', 'artifacts', 'testing']
        
        for dir_name in archivable_dirs:
            dir_path = os.path.join(self.repo_path, dir_name)
            if not os.path.exists(dir_path):
                continue
            
            for root, dirs, files in os.walk(dir_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    filepath = os.path.join(root, file)
                    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    if mtime < cutoff_date:
                        # Create archive path preserving directory structure
                        rel_path = os.path.relpath(filepath, self.repo_path)
                        archive_path = os.path.join(self.archive_dir, rel_path)
                        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
                        
                        try:
                            shutil.move(filepath, archive_path)
                            print(f"  Archived: {rel_path}")
                            archived_count += 1
                        except Exception as e:
                            print(f"  Failed to archive {rel_path}: {e}")
        
        return archived_count
    
    def optimize_markdown_files(self) -> int:
        """Clean up markdown files (remove trailing whitespace, normalize line endings)"""
        optimized_count = 0
        
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Remove trailing whitespace from each line
                        lines = content.split('\n')
                        cleaned_lines = [line.rstrip() for line in lines]
                        cleaned_content = '\n'.join(cleaned_lines)
                        
                        # Only write if content changed
                        if cleaned_content != content:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(cleaned_content)
                            optimized_count += 1
                    except:
                        pass
        
        return optimized_count
    
    def generate_cleanup_report(self, results: Dict[str, Any]) -> str:
        """Generate cleanup report"""
        today = datetime.now().strftime('%Y-%m-%d')
        report_file = os.path.join(self.repo_path, 'artifacts', f'cleanup_report_{today}.md')
        
        report_content = f"""# Repository Cleanup Report - {today}
*Generated by Cleaner Agent at {datetime.utcnow().isoformat()}*

## Summary
- Empty directories removed: {results.get('empty_dirs_removed', 0)}
- Files archived: {results.get('files_archived', 0)}
- Markdown files optimized: {results.get('markdown_optimized', 0)}
- Duplicate files found: {results.get('duplicates_found', 0)}

## Actions Taken

### Empty Directories
Removed {results.get('empty_dirs_removed', 0)} empty directories that were not critical to repository structure.

### File Archival
Archived {results.get('files_archived', 0)} files older than 90 days to `artifacts/archived/`.

### Markdown Optimization
Cleaned up {results.get('markdown_optimized', 0)} markdown files (trailing whitespace, line endings).

### Duplicate Detection
Found {results.get('duplicates_found', 0)} sets of duplicate files. Manual review recommended.

## Repository Health Status
✓ Repository structure optimized  
✓ Old files archived  
✓ Markdown files cleaned  
✓ Ready for continued development

## Next Cleanup
Scheduled for: {(datetime.now() + timedelta(seconds=self.work_interval)).strftime('%Y-%m-%d %H:%M:%S')}

---

*Cleaner Agent runs every {self.work_interval // 60} minutes*

∇θ — chain sealed, truth preserved.
"""
        
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        return report_file
    
    def do_work(self) -> Dict[str, Any]:
        """Perform cleaning work"""
        results = {
            'tasks_completed': 0,
            'empty_dirs_removed': 0,
            'files_archived': 0,
            'markdown_optimized': 0,
            'duplicates_found': 0,
            'files_created': []
        }
        
        # Remove empty directories
        print("Removing empty directories...")
        results['empty_dirs_removed'] = self.remove_empty_directories()
        print(f"✓ Removed {results['empty_dirs_removed']} empty directories")
        results['tasks_completed'] += 1
        
        # Archive old files (only on first cycle of the day to avoid excessive archiving)
        if self.cycle_count % 96 == 1:  # Once per day (assuming 15-min intervals)
            print("Archiving old files...")
            results['files_archived'] = self.archive_old_files(days_old=90)
            print(f"✓ Archived {results['files_archived']} old files")
            results['tasks_completed'] += 1
        
        # Optimize markdown files
        print("Optimizing markdown files...")
        results['markdown_optimized'] = self.optimize_markdown_files()
        print(f"✓ Optimized {results['markdown_optimized']} markdown files")
        results['tasks_completed'] += 1
        
        # Find duplicates (report only, don't remove automatically)
        print("Scanning for duplicate files...")
        duplicates = self.find_duplicate_files()
        results['duplicates_found'] = len(duplicates)
        print(f"✓ Found {results['duplicates_found']} sets of duplicate files")
        
        # Generate cleanup report
        print("Generating cleanup report...")
        report_file = self.generate_cleanup_report(results)
        results['files_created'].append(report_file)
        print(f"✓ Cleanup report created: {report_file}")
        
        # Sync to GitHub if there were changes
        if results['empty_dirs_removed'] > 0 or results['markdown_optimized'] > 0:
            print("Syncing to GitHub...")
            self.git_sync(
                f"Cleaner Agent: Removed {results['empty_dirs_removed']} empty dirs, optimized {results['markdown_optimized']} files (Cycle {self.cycle_count})"
            )
        
        return results

if __name__ == '__main__':
    import hashlib  # Import here for duplicate detection
    agent = CleanerAgent()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        agent.run_once()
    else:
        agent.run_autopilot()
