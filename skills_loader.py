#!/usr/bin/env python3
"""
Skills Loader - Reads skill markdown files for agents
"""
import os


def load_skill(skill_name: str) -> str:
    """
    Load a skill file by name
    
    Args:
        skill_name: Name of skill file (without .md extension)
        
    Returns:
        Content of skill file or empty string if not found
    """
    skill_path = os.path.join("skills", f"{skill_name}.md")
    
    if os.path.exists(skill_path):
        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Warning: Could not read skill file {skill_path}: {e}")
            return ""
    else:
        print(f"Warning: Skill file not found: {skill_path}")
        return ""


def load_multiple_skills(skill_names: list) -> str:
    """
    Load multiple skill files and combine them
    
    Args:
        skill_names: List of skill file names
        
    Returns:
        Combined content of all skill files
    """
    skills = []
    for name in skill_names:
        content = load_skill(name)
        if content:
            skills.append(f"## {name.upper()} SKILLS\n\n{content}")
    
    return "\n\n".join(skills)
