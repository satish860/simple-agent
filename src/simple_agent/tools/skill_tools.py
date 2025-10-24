"""
Skill Tools - Tools for dynamic skill loading.

Implements the load_skill tool that allows the LLM to load
full skill instructions (Tier 2) when relevant.
"""

import json
from typing import Dict, Any
from pathlib import Path

from .base import BaseTool
from ..skills.registry import SkillRegistry


class LoadSkillTool(BaseTool):
    """
    Tool for loading full skill content (Tier 2 Progressive Disclosure).

    When the LLM determines a skill is relevant to the current task,
    it can call this tool to load the complete SKILL.md content.
    """

    def __init__(self, registry: SkillRegistry):
        """
        Initialize LoadSkillTool.

        Args:
            registry: SkillRegistry containing available skills
        """
        self.registry = registry

    @property
    def name(self) -> str:
        return "load_skill"

    @property
    def description(self) -> str:
        return "Load full instructions for a specific skill. Use this when a skill is relevant to the current task."

    @property
    def parameters(self) -> Dict[str, Any]:
        """
        Define tool parameters schema.

        Returns:
            JSON Schema for load_skill parameters
        """
        # Get available skill names for enum
        available_skills = [skill.name for skill in self.registry.list_skills()]

        return {
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": f"Name of the skill to load. Available skills: {', '.join(available_skills)}",
                    "enum": available_skills if available_skills else None
                }
            },
            "required": ["skill_name"]
        }

    def execute(self, skill_name: str) -> str:
        """
        Execute skill loading.

        Args:
            skill_name: Name of skill to load

        Returns:
            Full SKILL.md content or error message

        Raises:
            ValueError: If skill_name is invalid
        """
        if not skill_name or not skill_name.strip():
            return json.dumps({
                "error": "skill_name cannot be empty"
            })

        # Check if skill exists
        if not self.registry.has_skill(skill_name):
            available = [skill.name for skill in self.registry.list_skills()]
            return json.dumps({
                "error": f"Skill '{skill_name}' not found",
                "available_skills": available
            })

        # Get skill metadata
        skill = self.registry.get_skill(skill_name)

        # Read full SKILL.md content
        try:
            content = skill.skill_path.read_text(encoding='utf-8')

            # Mark skill as loaded
            self.registry.mark_loaded(skill_name)

            # Return the full content
            return json.dumps({
                "skill_name": skill_name,
                "content": content,
                "status": "loaded"
            })

        except Exception as e:
            return json.dumps({
                "error": f"Failed to load skill '{skill_name}': {str(e)}"
            })

    @property
    def system_reminder(self) -> str:
        """Reminder about skill usage."""
        return (
            "The skill content has been loaded into the conversation. "
            "Follow the instructions provided in the skill carefully. "
            "If the skill references additional resources, you may need to read those files separately."
        )
