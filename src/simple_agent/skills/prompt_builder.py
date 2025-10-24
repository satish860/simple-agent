"""
PromptBuilder - Generates Tier 1 system prompts with skill metadata.

This component creates the initial system prompt that lists available skills
so the LLM knows what capabilities it can load dynamically.
"""

from typing import List
from .registry import SkillRegistry
from .validation import SkillMetadata


class PromptBuilder:
    """
    Builds Tier 1 system prompts with skill metadata.

    Progressive Disclosure Tier 1:
    - Lists available skills by name and description
    - Provides instructions for loading skills with load_skill tool
    - Keeps prompt lightweight (metadata only, no full content)
    """

    def __init__(self, registry: SkillRegistry):
        """
        Initialize PromptBuilder.

        Args:
            registry: SkillRegistry containing discovered skills
        """
        self.registry = registry

    def build_tier1_prompt(self) -> str:
        """
        Build Tier 1 system prompt with skill metadata.

        Returns:
            Formatted prompt string with available skills and usage instructions

        Example Output:
            Available skills:
            - test-skill: A simple test skill for integration testing
            - code-review: Review code for best practices and security

            To load detailed instructions for a skill, use: load_skill("skill-name")
            Only load skills when they are relevant to the current task.
        """
        all_skills = self.registry.list_skills()

        if not all_skills:
            return ""  # No skills available, return empty string

        # Build skill list
        skills_section = self._format_skill_list(all_skills)

        # Add usage instructions
        instructions = self._get_load_skill_instructions()

        # Combine into full prompt
        prompt = f"{skills_section}\n\n{instructions}"

        return prompt

    def _format_skill_list(self, skills: List[SkillMetadata]) -> str:
        """
        Format list of skills as bullet points.

        Args:
            skills: List of SkillMetadata objects

        Returns:
            Formatted string with skill names and descriptions
        """
        lines = ["Available skills:"]

        for skill in skills:
            lines.append(f"- {skill.name}: {skill.description}")

        return "\n".join(lines)

    def _get_load_skill_instructions(self) -> str:
        """
        Get instructions for using the load_skill tool.

        Returns:
            Instructions text for the LLM
        """
        return (
            'To load detailed instructions for a skill, use: load_skill("skill-name")\n'
            'Only load skills when they are relevant to the current task.'
        )
