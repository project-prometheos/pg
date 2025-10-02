"""Pure Python parser for PG files - replaces Perl dependency."""

import re
from pathlib import Path
from typing import Dict, Any, List


class PGParser:
    """Parse PG files to extract metadata."""
    
    @staticmethod
    def parse_file(file_path: Path) -> Dict[str, Any]:
        """Parse a single PG file and extract all metadata."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return {
            'name': PGParser._extract_name(content, file_path),
            'description': PGParser._extract_description(content),
            'types': PGParser._extract_list_meta(content, 'type'),
            'subjects': PGParser._extract_list_meta(content, 'subject'),
            'categories': PGParser._extract_list_meta(content, 'categor'),
            'keywords': PGParser._extract_keywords(content),
            'macros': PGParser._extract_macros(content),
            'related': PGParser._extract_list_meta(content, 'see_also'),
            'dir': file_path.parent.name
        }
    
    @staticmethod
    def _extract_name(content: str, file_path: Path) -> str:
        """Extract problem name from #:% name = ... or filename."""
        if match := re.search(r'#:%\s*name\s*=\s*(.+)', content, re.IGNORECASE):
            return match.group(1).strip()
        return file_path.stem.replace('_', ' ').replace('-', ' ').title()
    
    @staticmethod
    def _extract_description(content: str) -> str:
        """Extract ## DESCRIPTION section."""
        pattern = r'##\s*DESCRIPTION\s*\n(.*?)\n##\s*ENDDESCRIPTION'
        if match := re.search(pattern, content, re.DOTALL | re.IGNORECASE):
            return match.group(1).strip()
        return ""
    
    @staticmethod
    def _extract_list_meta(content: str, key: str) -> List[str]:
        """Extract list metadata like #:% types = [sample, technique]."""
        # Try with brackets first
        pattern = f'#:%\\s*{key}\\w*\\s*=\\s*\\[([^\\]]+)\\]'
        if match := re.search(pattern, content, re.IGNORECASE):
            items = [item.strip().strip('"\'').lower() for item in match.group(1).split(',')]
            return [item for item in items if item]
        
        # Try without brackets
        pattern = f'#:%\\s*{key}\\w*\\s*=\\s*(.+)'
        if match := re.search(pattern, content, re.IGNORECASE):
            value = match.group(1).strip().strip('[]"\'')
            if value:
                items = [item.strip().lower() for item in value.split(',')]
                return [item for item in items if item]
        
        return []
    
    @staticmethod
    def _extract_keywords(content: str) -> List[str]:
        """Extract ## KEYWORDS(...) or #:% keywords."""
        # Try #:% keywords first
        keywords = PGParser._extract_list_meta(content, 'keyword')
        if keywords:
            return keywords
        
        # Try ## KEYWORDS format
        pattern = r'##\s*KEYWORDS\([\'"](.+?)[\'"]\)'
        if match := re.search(pattern, content, re.IGNORECASE):
            keywords_str = match.group(1)
            return [kw.strip().lower() for kw in keywords_str.split(',') if kw.strip()]
        
        return []
    
    @staticmethod
    def _extract_macros(content: str) -> List[str]:
        """Extract macros from loadMacros(...) calls."""
        pattern = r'loadMacros\((.*?)\);'
        if match := re.search(pattern, content, re.DOTALL):
            macros_str = match.group(1)
            # Extract quoted strings
            macro_pattern = r'[\'"]([^\'"]+\.pl)[\'"]'
            macros = re.findall(macro_pattern, macros_str)
            return macros
        return []
    
    @staticmethod
    def generate_metadata(problems_dir: Path) -> Dict[str, Dict[str, Any]]:
        """Generate metadata for all PG files in directory."""
        metadata = {}
        
        for pg_file in problems_dir.rglob("*.pg"):
            try:
                problem_meta = PGParser.parse_file(pg_file)
                relative_path = pg_file.relative_to(problems_dir)
                problem_meta['dir'] = str(relative_path.parent) if relative_path.parent != Path('.') else ''
                metadata[pg_file.name] = problem_meta
            except Exception as e:
                print(f"  [WARN] Failed to parse {pg_file.name}: {e}")
        
        return metadata
