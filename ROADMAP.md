# Progressive Disclosure Architecture - Project Roadmap

## Project Overview

Build an LLM-agnostic Python SDK implementing Progressive Disclosure Architecture for agent skills. This system enables agents to load information progressively - starting with metadata, then detailed instructions, and finally supplementary resources - optimizing context window usage while maintaining full capability access.

### Core Principles
- **LLM Agnostic**: Support multiple LLM providers via unified interface
- **Progressive Loading**: Three-tier information disclosure (metadata -> instructions -> resources)
- **Modular Skills**: Self-contained skill packages with SKILL.md format
- **Developer-Friendly**: Easy to create, test, and distribute skills

### Technology Stack
- Python 3.11+ with uv for package management
- OpenRouter for multi-model support (starting with Claude Haiku)
- Pydantic for data validation
- YAML + Markdown for skill format

---

## Phase 1: Foundation & Core Architecture
**Timeline**: Weeks 1-2
**Status**: Not Started

### 1.1 Project Structure Setup
- [ ] Update pyproject.toml with core dependencies
  - openai (for OpenRouter compatibility)
  - pydantic
  - pyyaml
  - rich (for CLI output)
  - python-dotenv
- [ ] Create package structure:
  ```
  src/simple_agent/
  ├── __init__.py
  ├── llm/              # LLM abstraction layer
  ├── skills/           # Skill system
  ├── engine/           # Progressive disclosure engine
  ├── runtime/          # Agent runtime
  └── utils/            # Utilities
  ```
- [ ] Set up development tools (pytest, black, mypy, ruff)

### 1.2 LLM Abstraction Layer
- [ ] Create BaseLLM abstract class
  - Standard message format
  - Tool/function calling abstraction
  - Streaming support interface
- [ ] Implement OpenRouterLLM class
  - API integration with OpenAI-compatible endpoint
  - Message formatting for different models
  - Function calling translation
  - Streaming response handling
- [ ] Create LLMConfig for provider settings
- [ ] Add support for model switching
- [ ] Implement error handling and retry logic

### 1.3 Skill Format Specification
- [ ] Define SKILL.md structure:
  ```markdown
  ---
  name: skill_name
  description: Brief description for metadata
  version: 1.0.0
  author: optional
  resources:
    - reference.md
    - examples.md
  ---

  # Full Skill Instructions
  Detailed instructions loaded in Tier 2...
  ```
- [ ] Document required vs optional fields
- [ ] Create skill validation schema
- [ ] Write skill creation best practices guide

---

## Phase 2: Progressive Disclosure Engine
**Timeline**: Weeks 3-4
**Status**: Not Started

### 2.1 Skill Discovery & Loading
- [ ] Implement SkillLoader class
  - Scan directories for SKILL.md files
  - Parse YAML frontmatter
  - Extract markdown content
  - Validate skill structure
- [ ] Create SkillRegistry
  - Index skills by name
  - Store metadata for quick access
  - Support skill versioning
  - Handle skill conflicts
- [ ] Add directory watching (optional)

### 2.2 Three-Tier Loading System
- [ ] **Tier 1**: Metadata Injection
  - Build concise skill list from metadata
  - Inject into system prompt
  - Format: "skill_name: description"
- [ ] **Tier 2**: Full Instructions Loading
  - Create tool for loading SKILL.md content
  - Implement relevance matching
  - Dynamic prompt expansion
- [ ] **Tier 3**: Resource Loading
  - Parse resource links from SKILL.md
  - Lazy load referenced files
  - Support for markdown, JSON, CSV, etc.
- [ ] Context Window Management
  - Track token usage
  - Implement LRU cache for loaded skills
  - Smart unloading of unused content

### 2.3 Resource Management
- [ ] Resource link parser
  - Support relative paths
  - Validate resource existence
  - Handle missing resources gracefully
- [ ] File type handlers
  - Markdown reader
  - JSON/YAML parser
  - CSV/TSV reader
  - Plain text handler
- [ ] Token budget calculator

---

## Phase 3: Agent Runtime
**Timeline**: Weeks 5-6
**Status**: Not Started

### 3.1 Skill Invocation System
- [ ] Create skill invocation tool
  - "load_skill" function for agents
  - Skill name validation
  - Content retrieval and formatting
- [ ] Implement relevance matching
  - Keyword matching
  - Semantic similarity (optional)
  - Manual skill selection support
- [ ] Dynamic prompt builder
  - Construct system prompts with Tier 1 metadata
  - Append loaded skill instructions
  - Manage prompt boundaries

### 3.2 Execution Engine
- [ ] Code script execution
  - Python script runner within skills
  - Sandboxing considerations
  - Input/output handling
- [ ] Shell command support
  - Powershell execution (Windows)
  - Stdout/stderr capture
  - Exit code handling
- [ ] Error handling
  - Graceful degradation
  - Error reporting to agent
  - Recovery strategies

### 3.3 Session Management
- [ ] Conversation state tracking
  - Message history management
  - Context accumulation
  - Session persistence (optional)
- [ ] Loaded skills cache
  - Track which skills are loaded
  - Prevent redundant loading
  - Cache invalidation
- [ ] Context optimization
  - Summarization of old messages
  - Smart truncation
  - Priority-based retention

---

## Phase 4: Developer Experience
**Timeline**: Week 7
**Status**: Not Started

### 4.1 Skill Templates & CLI
- [ ] Create skill scaffolding command
  - Generate SKILL.md template
  - Create directory structure
  - Add example resources
- [ ] Skill validation tool
  - Check YAML syntax
  - Validate required fields
  - Lint markdown content
- [ ] Testing utilities
  - Mock LLM for testing
  - Skill test harness
  - Integration test helpers

### 4.2 Example Skills
- [ ] Create 3-5 production-ready skills:
  - **code_review**: Code review with style guidelines
  - **data_analyzer**: Data processing and analysis
  - **git_helper**: Git workflow automation
  - **test_generator**: Unit test generation
  - **doc_writer**: Documentation generation
- [ ] Each skill demonstrates:
  - Tier 1: Concise metadata
  - Tier 2: Full instructions
  - Tier 3: Linked resources (style guides, examples, etc.)

### 4.3 Testing Framework
- [ ] Unit tests
  - LLM abstraction tests
  - Skill loader tests
  - Engine component tests
- [ ] Integration tests
  - End-to-end agent flows
  - OpenRouter integration
  - Skill loading scenarios
- [ ] Performance tests
  - Token usage optimization
  - Loading time benchmarks
  - Cache effectiveness

---

## Phase 5: Documentation & Polish
**Timeline**: Week 8
**Status**: Not Started

### 5.1 Comprehensive Documentation
- [ ] Architecture Guide
  - Progressive disclosure explanation
  - System components overview
  - Design decisions rationale
- [ ] Skill Development Guide
  - Creating your first skill
  - Best practices
  - Advanced patterns
  - Resource organization
- [ ] API Reference
  - Generated from docstrings
  - Code examples
  - Parameter descriptions
- [ ] Migration Guide
  - From Claude Code Skills
  - Adapting existing skills

### 5.2 Examples & Tutorials
- [ ] Quick start tutorial
- [ ] Building a custom skill walkthrough
- [ ] Multi-model usage examples
- [ ] Advanced scenarios
  - Skill composition
  - Custom resource types
  - Performance optimization

### 5.3 Community & Distribution
- [ ] Contribution guidelines
- [ ] Skill sharing recommendations
- [ ] Security best practices
- [ ] GitHub repository setup
  - README.md
  - LICENSE
  - CONTRIBUTING.md
  - Issue templates

---

## Future Enhancements
**Post v1.0**

### Advanced Features
- [ ] Skill marketplace/registry
- [ ] Package-based skill distribution
- [ ] Hot-reloading of skills
- [ ] Skill dependency management
- [ ] Multi-agent collaboration
- [ ] Skill versioning and updates

### Additional LLM Providers
- [ ] Direct Anthropic SDK support
- [ ] Google PaLM/Gemini
- [ ] Azure OpenAI
- [ ] AWS Bedrock
- [ ] Local models (Ollama, LM Studio)

### Performance Optimizations
- [ ] Parallel skill loading
- [ ] Embeddings-based skill search
- [ ] Persistent caching
- [ ] Incremental context updates

### Tooling
- [ ] Visual skill builder
- [ ] Skill analytics dashboard
- [ ] Performance profiler
- [ ] Cost tracking

---

## Success Metrics

### Technical Goals
- Support for 3+ LLM providers
- <100ms skill metadata loading
- <500ms full skill loading
- 90%+ test coverage
- Clear, comprehensive documentation

### Developer Experience Goals
- <5 minutes to create first skill
- <10 lines of code for basic agent
- Intuitive API design
- Active community engagement

### Adoption Goals
- 10+ community-contributed skills
- 100+ GitHub stars
- Usage in production applications

---

## Getting Started

Once Phase 1 is complete, you can start using the library:

```python
from simple_agent import Agent
from simple_agent.llm import OpenRouterLLM

# Initialize LLM
llm = OpenRouterLLM(
    api_key="your-openrouter-key",
    model="anthropic/claude-3.5-haiku"
)

# Create agent with skills directory
agent = Agent(
    llm=llm,
    skills_dir="./skills"
)

# Run agent
response = agent.run("Review this Python code for best practices")
print(response)
```

## Notes

- Work incrementally, completing each phase before moving to the next
- Validate with real-world usage at each phase
- Gather feedback from early adopters
- Stay flexible - adjust roadmap based on learnings
- Focus on developer experience throughout
