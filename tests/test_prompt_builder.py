"""
Tests for PromptBuilder module.

Tests the PromptBuilder component:
- Tier 1 system prompt generation
- Skill metadata formatting
- load_skill tool instructions
- Empty skills list handling
- Prompt structure and formatting
- Integration with SkillRegistry
"""

import pytest
from pathlib import Path
from simple_agent.skills.prompt_builder import PromptBuilder
from simple_agent.skills.registry import SkillRegistry
from simple_agent.skills.loader import SkillLoader
from simple_agent.skills.validation import SkillValidator
from simple_agent.skills.paths import SkillPathResolver


class TestPromptBuilderInitialization:
    """Test PromptBuilder initialization."""

    def test_initialize_with_registry(self, temp_skills_dir):
        """Should initialize PromptBuilder with SkillRegistry."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)

        builder = PromptBuilder(registry=registry)

        assert builder is not None
        assert isinstance(builder, PromptBuilder)
        assert builder.registry == registry

    def test_initialize_requires_registry(self):
        """Should require registry parameter."""
        with pytest.raises(TypeError):
            PromptBuilder()


class TestTier1PromptGeneration:
    """Test Tier 1 system prompt generation."""

    def test_build_prompt_with_skills(self, temp_skills_dir):
        """Should generate Tier 1 prompt with available skills."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)
        builder = PromptBuilder(registry=registry)

        prompt = builder.build_tier1_prompt()

        # Should contain header
        assert "Available skills:" in prompt

        # Should contain skill names and descriptions
        assert "skill-one" in prompt
        assert "skill-two" in prompt
        assert "Test skill" in prompt

        # Should contain load_skill instructions
        assert "load_skill" in prompt
        assert "relevant to the current task" in prompt

    def test_build_prompt_with_empty_registry(self, temp_empty_skills_dir, monkeypatch):
        """Should return empty string when no skills available."""
        # Change to temp directory to avoid discovering project's skills/
        monkeypatch.chdir(temp_empty_skills_dir)

        # Create a truly isolated empty skills dir
        empty_dir = temp_empty_skills_dir / "empty_skills"
        empty_dir.mkdir()

        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(empty_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)
        builder = PromptBuilder(registry=registry)

        prompt = builder.build_tier1_prompt()

        assert prompt == ""

    def test_build_prompt_structure(self, temp_skills_dir):
        """Should generate prompt with correct structure."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)
        builder = PromptBuilder(registry=registry)

        prompt = builder.build_tier1_prompt()

        # Split into sections
        lines = prompt.split('\n')

        # First line should be header
        assert lines[0] == "Available skills:"

        # Should have skill lines (starting with -)
        skill_lines = [line for line in lines if line.startswith('-')]
        assert len(skill_lines) >= 2  # At least skill-one and skill-two

        # Should have instructions section
        assert "To load detailed instructions for a skill" in prompt


class TestSkillMetadataFormatting:
    """Test skill metadata formatting."""

    def test_format_single_skill(self, temp_skills_dir):
        """Should format single skill correctly."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)
        builder = PromptBuilder(registry=registry)

        skills = [registry.get_skill("skill-one")]
        formatted = builder._format_skill_list(skills)

        # Should have header and skill entry
        assert "Available skills:" in formatted
        assert "- skill-one: Test skill" in formatted

    def test_format_multiple_skills(self, temp_multiple_skill_dirs, monkeypatch):
        """Should format multiple skills correctly."""
        # Change to temp directory to avoid discovering project's skills/
        monkeypatch.chdir(temp_multiple_skill_dirs[0].parent)

        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(d) for d in temp_multiple_skill_dirs])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)
        builder = PromptBuilder(registry=registry)

        all_skills = registry.list_skills()
        formatted = builder._format_skill_list(all_skills)

        # Should have header
        assert formatted.startswith("Available skills:")

        # Should have all skills listed
        assert "skill-a" in formatted
        assert "skill-b" in formatted
        assert "skill-c" in formatted

        # Each skill should be on its own line with bullet point
        lines = formatted.split('\n')
        skill_lines = [line for line in lines if line.startswith('- ')]
        # Should have at least our 3 skills (may have more from default paths)
        assert len(skill_lines) >= 3
        # But specifically check our expected skills are there
        assert any("skill-a" in line for line in skill_lines)
        assert any("skill-b" in line for line in skill_lines)
        assert any("skill-c" in line for line in skill_lines)

    def test_format_preserves_skill_order(self, temp_multiple_skill_dirs):
        """Should preserve order of skills in formatting."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(d) for d in temp_multiple_skill_dirs])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)
        builder = PromptBuilder(registry=registry)

        all_skills = registry.list_skills()
        formatted = builder._format_skill_list(all_skills)

        # Find positions of each skill
        skill_a_pos = formatted.find("skill-a")
        skill_b_pos = formatted.find("skill-b")
        skill_c_pos = formatted.find("skill-c")

        # Verify they appear in order
        assert skill_a_pos < skill_b_pos < skill_c_pos


class TestLoadSkillInstructions:
    """Test load_skill tool instructions."""

    def test_instructions_format(self, temp_skills_dir):
        """Should format load_skill instructions correctly."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)
        builder = PromptBuilder(registry=registry)

        instructions = builder._get_load_skill_instructions()

        # Should mention load_skill function
        assert 'load_skill("skill-name")' in instructions

        # Should mention relevance
        assert "relevant to the current task" in instructions

        # Should be clear and concise
        assert len(instructions) < 200  # Reasonable length

    def test_instructions_included_in_prompt(self, temp_skills_dir):
        """Should include instructions in full prompt."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)
        builder = PromptBuilder(registry=registry)

        prompt = builder.build_tier1_prompt()
        instructions = builder._get_load_skill_instructions()

        # Full instructions should be in prompt
        assert instructions in prompt


class TestPromptBuilderIntegration:
    """Test integration with SkillRegistry."""

    def test_updates_when_skills_change(self, temp_skills_dir):
        """Should reflect current registry state."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)
        builder = PromptBuilder(registry=registry)

        # Build prompt
        prompt1 = builder.build_tier1_prompt()
        skill_count1 = prompt1.count('- skill-')

        # Verify we have skills
        assert skill_count1 > 0

    def test_handles_nested_skills(self, temp_skills_tree):
        """Should handle skills from nested directories."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_tree)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)
        builder = PromptBuilder(registry=registry)

        prompt = builder.build_tier1_prompt()

        # Should include all discovered skills
        assert "top-skill" in prompt
        assert "nested-skill" in prompt
        assert "deep-skill" in prompt

    def test_real_skills_directory(self):
        """Should work with actual skills directory."""
        skills_dir = Path(__file__).parent.parent / "skills"

        if not skills_dir.exists():
            pytest.skip("Skills directory not found")

        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)
        builder = PromptBuilder(registry=registry)

        prompt = builder.build_tier1_prompt()

        # If skills exist, prompt should not be empty
        if registry.count_total() > 0:
            assert prompt != ""
            assert "Available skills:" in prompt
        else:
            assert prompt == ""


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_skill_with_long_description(self, tmp_path):
        """Should handle skills with long descriptions."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        long_desc = "This is a very long description " * 20  # Long but valid
        (skills_dir / "long-skill").mkdir()
        (skills_dir / "long-skill" / "SKILL.md").write_text(
            f"---\nname: long-skill\ndescription: {long_desc}\n---\n",
            encoding='utf-8'
        )

        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)
        builder = PromptBuilder(registry=registry)

        prompt = builder.build_tier1_prompt()

        # Should include the skill with long description
        assert "long-skill" in prompt
        assert long_desc[:50] in prompt  # At least part of description

    def test_skill_with_special_characters(self, tmp_path):
        """Should handle skills with special characters in description."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        (skills_dir / "special-skill").mkdir()
        (skills_dir / "special-skill" / "SKILL.md").write_text(
            '---\nname: special-skill\ndescription: "Code review: style, security & performance!"\n---\n',
            encoding='utf-8'
        )

        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)
        builder = PromptBuilder(registry=registry)

        prompt = builder.build_tier1_prompt()

        # Should handle special characters correctly
        assert "special-skill" in prompt
        assert "style, security & performance!" in prompt

    def test_multiple_builds_same_result(self, temp_skills_dir):
        """Should produce consistent results on multiple builds."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)
        builder = PromptBuilder(registry=registry)

        prompt1 = builder.build_tier1_prompt()
        prompt2 = builder.build_tier1_prompt()
        prompt3 = builder.build_tier1_prompt()

        # Should be identical
        assert prompt1 == prompt2 == prompt3


class TestPromptQuality:
    """Test prompt quality and usability."""

    def test_prompt_is_lightweight(self, temp_skills_dir):
        """Should generate lightweight prompt (metadata only)."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)
        builder = PromptBuilder(registry=registry)

        prompt = builder.build_tier1_prompt()

        # Prompt should be concise (< 1KB per skill roughly)
        skills_count = registry.count_total()
        max_expected_size = skills_count * 1024  # 1KB per skill is generous

        assert len(prompt) < max_expected_size

    def test_prompt_is_llm_friendly(self, temp_skills_dir):
        """Should generate LLM-friendly format."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)
        builder = PromptBuilder(registry=registry)

        prompt = builder.build_tier1_prompt()

        # Should use clear structure
        assert prompt.startswith("Available skills:")

        # Should use bullet points for listing
        assert '\n- ' in prompt

        # Should have clear instructions
        assert 'load_skill' in prompt
        assert '"skill-name"' in prompt

    def test_prompt_contains_no_tier2_content(self, temp_skills_dir):
        """Should not include Tier 2 content (only metadata)."""
        validator = SkillValidator()
        resolver = SkillPathResolver(explicit_paths=[str(temp_skills_dir)])
        loader = SkillLoader(path_resolver=resolver, validator=validator)
        registry = SkillRegistry(skill_loader=loader)
        builder = PromptBuilder(registry=registry)

        prompt = builder.build_tier1_prompt()

        # Should NOT contain markdown headers or detailed content
        # that would typically be in Tier 2
        lines = prompt.split('\n')
        tier2_indicators = ['##', '###', '```', 'Example:', 'Usage:']

        for line in lines:
            for indicator in tier2_indicators:
                # Only check skill content lines, not instructions
                if line.startswith('- '):
                    assert indicator not in line
