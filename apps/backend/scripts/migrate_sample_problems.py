"""Migration script to parse and populate sample problems from PG files."""
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text

from app.models.database import (
    Problem, ProblemMetadata, ProblemType, ProblemSubject, 
    ProblemCategory, ProblemKeyword, ProblemMacro, 
    ProblemRelation, ProblemDocumentation, ProblemEmbedding
)


@dataclass
class ParsedProblem:
    """Parsed problem data from PG file."""
    id: str
    name: str
    description: str
    pg_source: str
    file_path: str
    types: List[str]
    subjects: List[str]
    categories: List[str]
    keywords: List[str]
    macros: List[str]
    related_problems: List[str]
    documentation: Dict[str, str]
    metadata: Dict[str, str]


class SampleProblemMigrator:
    """Migrates sample problems from PG files to SQLite database."""
    
    def __init__(self, database_url: str = "sqlite:///problems.db"):
        self.engine = create_engine(database_url)
        self.sample_problems_dir = Path("tutorial/sample-problems")
        
    def parse_pg_file(self, file_path: Path) -> Optional[ParsedProblem]:
        """Parse a single PG file and extract metadata."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
            
        # Extract metadata from comments
        metadata = self._extract_metadata(content)
        
        # Generate problem ID from file path
        relative_path = file_path.relative_to(self.sample_problems_dir)
        problem_id = str(relative_path).replace('/', '.').replace('.pg', '')
        
        # Extract name from metadata or filename
        name = metadata.get('name', relative_path.stem.replace('_', ' ').title())
        
        # Extract description from ## DESCRIPTION section
        description = self._extract_description(content)
        
        # Extract types, subjects, categories, keywords
        types = self._parse_list_metadata(metadata.get('type', ''))
        subjects = self._parse_list_metadata(metadata.get('subject', ''))
        categories = self._parse_list_metadata(metadata.get('categories', ''))
        keywords = self._extract_keywords(content)
        
        # Extract macros from loadMacros calls
        macros = self._extract_macros(content)
        
        # Extract related problems
        related_problems = self._parse_list_metadata(metadata.get('see_also', ''))
        
        # Extract documentation sections
        documentation = self._extract_documentation(content)
        
        return ParsedProblem(
            id=problem_id,
            name=name,
            description=description,
            pg_source=content,
            file_path=str(relative_path),
            types=types,
            subjects=subjects,
            categories=categories,
            keywords=keywords,
            macros=macros,
            related_problems=related_problems,
            documentation=documentation,
            metadata=metadata
        )
    
    def _extract_metadata(self, content: str) -> Dict[str, str]:
        """Extract metadata from #:% comments."""
        metadata = {}
        
        # Pattern for #:% key = value
        pattern = r'#:%\s*(\w+)\s*=\s*(.*?)(?=\n|$)'
        matches = re.findall(pattern, content, re.MULTILINE)
        
        for key, value in matches:
            metadata[key.strip()] = value.strip()
            
        return metadata
    
    def _extract_description(self, content: str) -> str:
        """Extract description from ## DESCRIPTION section."""
        pattern = r'##\s*DESCRIPTION\s*\n(.*?)\n##\s*ENDDESCRIPTION'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        return ""
    
    def _parse_list_metadata(self, value: str) -> List[str]:
        """Parse list metadata like [item1, item2, item3]."""
        if not value:
            return []
            
        # Remove brackets and split by comma
        value = value.strip('[]')
        items = [item.strip() for item in value.split(',') if item.strip()]
        return items
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from ## KEYWORDS line."""
        pattern = r'##\s*KEYWORDS\([\'"](.*?)[\'"]\)'
        match = re.search(pattern, content)
        
        if match:
            keywords_str = match.group(1)
            return [kw.strip() for kw in keywords_str.split(',')]
        return []
    
    def _extract_macros(self, content: str) -> List[str]:
        """Extract macros from loadMacros calls."""
        macros = []
        
        # Pattern for loadMacros('macro1.pl', 'macro2.pl', ...)
        pattern = r'loadMacros\((.*?)\);'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            macros_str = match.group(1)
            # Extract quoted strings
            macro_pattern = r'[\'"]([^\'"]+\.pl)[\'"]'
            macro_matches = re.findall(macro_pattern, macros_str)
            macros.extend(macro_matches)
            
        return macros
    
    def _extract_documentation(self, content: str) -> Dict[str, str]:
        """Extract documentation sections."""
        documentation = {}
        
        # Pattern for #:% section = section_name followed by #: content
        sections = re.findall(r'#:%\s*section\s*=\s*(\w+)(.*?)(?=#:%\s*section|$)', content, re.DOTALL)
        
        for section_name, section_content in sections:
            # Extract lines starting with #:
            doc_lines = []
            for line in section_content.split('\n'):
                if line.strip().startswith('#:'):
                    doc_line = line.strip()[2:].strip()
                    if doc_line:
                        doc_lines.append(doc_line)
            
            if doc_lines:
                documentation[section_name] = '\n'.join(doc_lines)
                
        return documentation
    
    def migrate_sample_problems(self) -> int:
        """Migrate all sample problems to database."""
        if not self.sample_problems_dir.exists():
            print(f"Sample problems directory not found: {self.sample_problems_dir}")
            return 0
            
        migrated_count = 0
        
        with Session(self.engine) as session:
            # Find all PG files recursively
            pg_files = list(self.sample_problems_dir.rglob("*.pg"))
            print(f"Found {len(pg_files)} PG files to migrate")
            
            for pg_file in pg_files:
                print(f"Processing: {pg_file}")
                
                parsed_problem = self.parse_pg_file(pg_file)
                if not parsed_problem:
                    continue
                    
                # Create problem record
                problem = Problem(
                    id=parsed_problem.id,
                    name=parsed_problem.name,
                    description=parsed_problem.description,
                    pg_source=parsed_problem.pg_source,
                    file_path=parsed_problem.file_path
                )
                
                # Add metadata
                for key, value in parsed_problem.metadata.items():
                    metadata = ProblemMetadata(
                        problem_id=problem.id,
                        key=key,
                        value=value
                    )
                    session.add(metadata)
                
                # Add types
                for problem_type in parsed_problem.types:
                    ptype = ProblemType(
                        problem_id=problem.id,
                        type=problem_type.lower()
                    )
                    session.add(ptype)
                
                # Add subjects
                for subject in parsed_problem.subjects:
                    psubject = ProblemSubject(
                        problem_id=problem.id,
                        subject=subject.lower()
                    )
                    session.add(psubject)
                
                # Add categories
                for category in parsed_problem.categories:
                    pcategory = ProblemCategory(
                        problem_id=problem.id,
                        category=category.lower()
                    )
                    session.add(pcategory)
                
                # Add keywords
                for keyword in parsed_problem.keywords:
                    pkeyword = ProblemKeyword(
                        problem_id=problem.id,
                        keyword=keyword.lower()
                    )
                    session.add(pkeyword)
                
                # Add macros
                for macro in parsed_problem.macros:
                    pmacro = ProblemMacro(
                        problem_id=problem.id,
                        macro=macro
                    )
                    session.add(pmacro)
                
                # Add documentation
                for section, content in parsed_problem.documentation.items():
                    pdoc = ProblemDocumentation(
                        problem_id=problem.id,
                        section=section,
                        content=content
                    )
                    session.add(pdoc)
                
                session.add(problem)
                migrated_count += 1
            
            # Commit all changes
            session.commit()
            print(f"Successfully migrated {migrated_count} problems")
            
        return migrated_count
    
    def create_fts_index(self):
        """Create full-text search index."""
        with self.engine.connect() as conn:
            # Create FTS5 virtual table
            conn.execute(text("""
                CREATE VIRTUAL TABLE IF NOT EXISTS problems_fts USING fts5(
                    problem_id,
                    name,
                    description,
                    content,
                    keywords,
                    subjects,
                    categories,
                    content='problems_search_content',
                    content_rowid='rowid'
                )
            """))
            
            # Create content view
            conn.execute(text("""
                CREATE VIEW IF NOT EXISTS problems_search_content AS
                SELECT 
                    p.rowid,
                    p.id as problem_id,
                    p.name,
                    p.description,
                    GROUP_CONCAT(DISTINCT pd.content, ' ') as content,
                    GROUP_CONCAT(DISTINCT pk.keyword, ' ') as keywords,
                    GROUP_CONCAT(DISTINCT ps.subject, ' ') as subjects,
                    GROUP_CONCAT(DISTINCT pc.category, ' ') as categories
                FROM problems p
                LEFT JOIN problem_documentation pd ON p.id = pd.problem_id
                LEFT JOIN problem_keywords pk ON p.id = pk.problem_id
                LEFT JOIN problem_subjects ps ON p.id = ps.problem_id
                LEFT JOIN problem_categories pc ON p.id = pc.problem_id
                GROUP BY p.id
            """))
            
            conn.commit()


def main():
    """Main migration function."""
    migrator = SampleProblemMigrator()
    
    print("Starting sample problem migration...")
    
    # Create database tables
    from app.models.database import init_database
    init_database(migrator.engine)
    
    # Migrate problems
    count = migrator.migrate_sample_problems()
    
    # Create search index
    migrator.create_fts_index()
    
    print(f"Migration completed. {count} problems migrated.")


if __name__ == "__main__":
    main()
