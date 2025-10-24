# Skills System Implementation Roadmap

Test-Driven Development (TDD) approach: Bottom-Up implementation from lowest to highest level components.

## Implementation Strategy

For each component:
1. **RED**: Write failing tests
2. **GREEN**: Write minimal code to pass tests
3. **REFACTOR**: Improve code quality
4. **REPEAT**: Next component

---

## Phase 0: Setup Testing Infrastructure ✅

**Status**: COMPLETED

- [x] Add pytest and pyyaml to dependencies
- [x] Create tests/ directory structure
- [x] Create test fixtures for sample SKILL.md files
- [x] Create conftest.py with shared fixtures

---

## Phase 1: SkillValidator (Lowest Level - No Dependencies) ✅

**Status**: COMPLETED

### Tests Written ✅
- [x] Test YAML frontmatter parsing
- [x] Test name validation (lowercase, hyphens, max 64 chars)
- [x] Test description validation (max 1024 chars)
- [x] Test invalid YAML handling
- [x] Test missing required fields
- [x] Test metadata dataclass creation

### Implementation ✅
- [x] SkillMetadata dataclass
- [x] SkillValidator class
- [x] YAML parsing with error handling
- [x] Field validation (name, description)
- [x] Frontmatter extraction

**Files**:
- `tests/test_validation.py` (12 tests, all passing)
- `src/simple_agent/skills/validation.py`

---

## Phase 2: SkillPathResolver (Low Level - Minimal Dependencies) ✅

**Status**: COMPLETED

### Tests Written ✅
- [x] Test explicit path resolution
- [x] Test project-local path (./skills/)
- [x] Test user global path (~/.simple-agent/skills/)
- [x] Test multiple paths with priority order
- [x] Test environment variable support (SIMPLE_AGENT_SKILLS_DIR)
- [x] Test path existence checks
- [x] Test path validation
- [x] Test path expansion (~ and environment variables)
- [x] Test cross-platform compatibility (Windows/Unix)
- [x] Test path deduplication
- [x] Test edge cases

### Implementation ✅
- [x] SkillPathResolver class
- [x] Multi-path resolution with priority
- [x] Environment variable support
- [x] Path validation and existence checks
- [x] Path expansion and cross-platform support

**Files**:
- `tests/test_paths.py` (24 tests, all passing)
- `tests/conftest.py` (added path fixtures)
- `src/simple_agent/skills/paths.py`

---

## Phase 3: SkillLoader (Medium Level - Uses Validator + Paths)

**Status**: PENDING

### Tests to Write
- [ ] Test discover_skills from single directory
- [ ] Test discover_skills from multiple directories
- [ ] Test loading SKILL.md files
- [ ] Test handling invalid skills gracefully
- [ ] Test recursion into subdirectories
- [ ] Test empty directories
- [ ] Test duplicate skill names across paths

### Implementation
- [ ] SkillLoader class
- [ ] Directory scanning and SKILL.md discovery
- [ ] Integration with SkillValidator
- [ ] Error handling for invalid skills

**Files**:
- `tests/test_loader.py`
- `src/simple_agent/skills/loader.py`

---

## Phase 4: SkillRegistry (Medium Level - Uses Loader)

**Status**: PENDING

### Tests to Write
- [ ] Test skill registration and indexing
- [ ] Test duplicate skill handling (priority order)
- [ ] Test skill lookup by name
- [ ] Test listing all skills
- [ ] Test tracking loaded skills (Tier 2/3)
- [ ] Test is_loaded() checking
- [ ] Test get_skill() retrieval

### Implementation
- [ ] SkillRegistry class
- [ ] Skill indexing by name
- [ ] Duplicate handling with priority
- [ ] Loaded skills tracking

**Files**:
- `tests/test_registry.py`
- `src/simple_agent/skills/registry.py`

---

## Phase 5: PromptBuilder (Uses Registry)

**Status**: PENDING

### Tests to Write
- [ ] Test Tier 1 system prompt generation
- [ ] Test skill metadata formatting
- [ ] Test instructions for load_skill tool
- [ ] Test empty skills list handling
- [ ] Test prompt structure and formatting

### Implementation
- [ ] PromptBuilder class
- [ ] Tier 1 system prompt generation
- [ ] Skill metadata formatting for LLM
- [ ] load_skill tool usage instructions

**Files**:
- `tests/test_prompt_builder.py`
- `src/simple_agent/skills/prompt_builder.py`

---

## Phase 6: ContentLoader (Uses Registry + File I/O)

**Status**: PENDING

### Tests to Write
- [ ] Test Tier 2 SKILL.md content loading
- [ ] Test Tier 3 resource file loading
- [ ] Test resource reference parsing from markdown
- [ ] Test caching to avoid reloads
- [ ] Test relative path resolution for resources
- [ ] Test missing resource handling
- [ ] Test loaded skill tracking

### Implementation
- [ ] ContentLoader class
- [ ] Tier 2 full SKILL.md loading
- [ ] Tier 3 resource file loading
- [ ] Markdown link parsing for resources
- [ ] Caching mechanism

**Files**:
- `tests/test_content_loader.py`
- `src/simple_agent/skills/content_loader.py`

---

## Phase 7: Tool Integration (Uses ContentLoader)

**Status**: PENDING

### Tests to Write
- [ ] Test load_skill tool definition
- [ ] Test tool schema generation
- [ ] Test tool execution with valid skill
- [ ] Test error handling (skill not found)
- [ ] Test tool integration with ToolRegistry
- [ ] Test tool response formatting

### Implementation
- [ ] LoadSkillTool class extending BaseTool
- [ ] Tool definition for LLM
- [ ] Integration with existing ToolRegistry
- [ ] Error handling and responses

**Files**:
- `tests/test_skill_tools.py`
- `src/simple_agent/tools/skill_tools.py`

---

## Phase 8: Agent Integration (Top Level - Uses Everything)

**Status**: PENDING

### Tests to Write
- [ ] Test Agent initialization with skills_dir
- [ ] Test Agent with multiple skills directories
- [ ] Test Tier 1 prompt injection into system prompt
- [ ] Test load_skill tool registration
- [ ] Test end-to-end skill loading flow
- [ ] Test LLM calling load_skill tool
- [ ] Test skill content appearing in conversation
- [ ] Test environment variable configuration

### Implementation
- [ ] Modify Agent.__init__ to accept skills configuration
- [ ] Initialize SkillRegistry at startup
- [ ] Inject Tier 1 metadata into system prompt
- [ ] Register load_skill tool with ToolRegistry
- [ ] Handle skill loading in agent loop

**Files**:
- `tests/test_agent_skills.py`
- `src/simple_agent/agent.py` (modifications)

---

## Phase 9: Example Skills & Documentation

**Status**: PENDING

### Example Skills to Create
- [ ] Create `skills/hello-world/SKILL.md` (minimal example)
- [ ] Create `skills/code-review/SKILL.md` (with resources)
- [ ] Create `skills/code-review/style_guide.md` (Tier 3)
- [ ] Create `skills/code-review/security_patterns.md` (Tier 3)

### Documentation
- [ ] Create SKILLS.md guide for writing skills
- [ ] Update README.md with skills usage
- [ ] Add skills examples to documentation
- [ ] Document best practices for skill creation
- [ ] Document the three-tier progressive disclosure

**Files**:
- `skills/` directory with examples
- `SKILLS.md`
- `README.md` (updates)

---

## Testing Coverage Goals

- Unit tests for each component (>80% coverage)
- Integration tests for component interactions
- End-to-end tests with Agent + Skills
- Fixtures for various skill scenarios

---

## Current Status Summary

| Phase | Component | Status | Tests | Implementation |
|-------|-----------|--------|-------|----------------|
| 0 | Testing Setup | ✅ DONE | N/A | ✅ Complete |
| 1 | SkillValidator | ✅ DONE | 12/12 passing | ✅ Complete |
| 2 | SkillPathResolver | ✅ DONE | 24/24 passing | ✅ Complete |
| 3 | SkillLoader | ⏳ NEXT | 0 tests | Not started |
| 4 | SkillRegistry | 📅 PENDING | 0 tests | Not started |
| 5 | PromptBuilder | 📅 PENDING | 0 tests | Not started |
| 6 | ContentLoader | 📅 PENDING | 0 tests | Not started |
| 7 | Tool Integration | 📅 PENDING | 0 tests | Not started |
| 8 | Agent Integration | 📅 PENDING | 0 tests | Not started |
| 9 | Examples & Docs | 📅 PENDING | N/A | Not started |

---

## Next Steps

**Current Focus**: Phase 3 - SkillLoader

1. Write tests for skill loading in `tests/test_loader.py`
2. Run tests (expect failures - RED)
3. Implement SkillLoader in `src/simple_agent/skills/loader.py`
4. Run tests until passing (GREEN)
5. Refactor if needed
6. Move to Phase 4
