# Simple Agent

> LLM-Agnostic Progressive Disclosure Architecture for Intelligent Agents

## Overview

Simple Agent is a Python SDK that implements Progressive Disclosure Architecture for LLM agents, enabling them to work with modular, self-contained skills that load information dynamically based on relevance and need.

Instead of overwhelming agents with massive context windows full of irrelevant information, Simple Agent provides information in three tiers:

1. **Tier 1 - Metadata**: Lightweight skill descriptions loaded at startup
2. **Tier 2 - Instructions**: Full skill details loaded when deemed relevant
3. **Tier 3 - Resources**: Supplementary materials loaded only when specific scenarios require them

## Current Status

**Phase 5 - Skills System Complete** ✓

- ✅ LiteLLM integration (access to 100+ models via OpenRouter)
- ✅ SimpleAgent core class with conversation management
- ✅ Beautiful console output with Rich library
- ✅ Production-ready error handling and input validation
- ✅ Single-turn task execution and multi-turn chat
- ✅ **Tool calling support with agent loop**
- ✅ **Progressive Disclosure Skills System (Tier 1 & 2)**
- ✅ **Dynamic skill loading with load_skill tool**
- ✅ **117 tests passing with TDD approach**

**Coming Soon:**
- 🔄 Tier 3 resources (ContentLoader)
- 🔄 More example skills
- 🔄 TODO tracking for complex tasks

## Key Features

- **LLM-Agnostic**: Works with any LLM provider through LiteLLM
- **OpenRouter Integration**: Access 100+ models (OpenAI, Anthropic, Google, Meta, etc.) with one API
- **Progressive Disclosure Skills**: Load knowledge dynamically based on relevance
- **Tool Calling**: Full agent loop with tool execution support
- **Beautiful Output**: Rich console formatting with automatic Unicode handling
- **Production Ready**: Comprehensive error handling, input validation, configurable timeouts
- **Test-Driven Development**: 117 tests passing, TDD approach throughout
- **Simple API**: Clean interface for both single-turn tasks and multi-turn conversations
- **Portable**: Standalone Python library, not tied to specific IDEs

## Installation

```powershell
# Clone the repository
git clone https://github.com/satish860/simple-agent
cd simple-agent

# Install dependencies
uv sync
```

## Quick Start

### Setup

1. Create a `.env` file (use `.env.example` as template):
```env
OPENROUTER_API_KEY=your_api_key_here
LITELLM_MODEL=openrouter/anthropic/claude-haiku-4.5
```

2. Get your OpenRouter API key at [https://openrouter.ai/keys](https://openrouter.ai/keys)

### Basic Usage

```python
from simple_agent import SimpleAgent

# Create agent (reads config from .env)
agent = SimpleAgent()

# Single-turn task execution
result = agent.run("Explain what recursion is in simple terms")
print(result['result'])

# Multi-turn conversation
agent = SimpleAgent()
response1 = agent.chat("What is 2+2?")
response2 = agent.chat("What about 3+3?")
response3 = agent.chat("Add those results together")  # Remembers context
```

### Using Skills (Progressive Disclosure)

```python
from simple_agent import SimpleAgent

# Agent automatically loads skills from ./skills/ directory
agent = SimpleAgent()

# The LLM sees available skills in Tier 1 (metadata only)
# and can call load_skill() when relevant
result = agent.run("Review this code for best practices")

# Skills are loaded dynamically (Tier 2) only when needed
# This saves tokens and keeps context focused
```

### Advanced Configuration

```python
from simple_agent import SimpleAgent

# Custom configuration with skills
agent = SimpleAgent(
    model="openrouter/anthropic/claude-haiku-4.5",
    api_key="your-api-key",
    system_prompt="You are a helpful code review assistant.",
    skills_dir="./my-custom-skills",  # Custom skills directory
    enable_skills=True,  # Enable skills system (default: True)
    timeout=60,  # Request timeout in seconds
    max_iterations=15  # Maximum agent loop iterations
)

# Run task with tools
result = agent.run("Review this Python code for security issues")

# Check result
if result['success']:
    print(result['result'])
    print(f"Iterations: {result['iterations']}")
    print(f"Tokens used: {result['usage']['total_tokens']}")
```

### Running Examples

```powershell
# Hello World - Direct LiteLLM usage
uv run python examples/hello_world.py

# Simple Chat - SimpleAgent with all features
uv run python examples/simple_chat.py

# Skills System E2E Test
uv run python examples/test_skills_e2e.py

# Manual LLM Skills Test
uv run python examples/test_real_llm.py
```

## Features in Detail

### Beautiful Console Output

Uses the Rich library for:
- Styled panels and tables
- Automatic Unicode handling (no more Windows console issues!)
- Colored output for better readability
- Token usage statistics

### Error Handling

Comprehensive error handling for:
- `AuthenticationError` - Invalid API keys
- `RateLimitError` - Rate limiting
- `Timeout` - Request timeouts
- `APIError` - General API errors
- Proper error messages with context

### Input Validation

Automatic validation for:
- Empty or whitespace-only inputs
- Maximum length limits (50,000 characters)
- Clear error messages

### Conversation Management

- `run(task)` - Single-turn execution, resets conversation
- `chat(message)` - Multi-turn conversation, maintains context
- `reset()` - Clear conversation history

## Architecture

### Current Architecture (Phase 5 - Working!)

```
User Query -> SimpleAgent (Tier 1: Skill Metadata in System Prompt)
                    |
                    v
              Agent Loop Iteration
                    |
                    v
         LiteLLM (via OpenRouter) - Any Model
                    |
                    v
              LLM determines relevance
                    |
        +-----------+-----------+
        |                       |
        v                       v
   No tool calls         load_skill() tool call
        |                       |
        |                       v
        |              Tier 2: Load SKILL.md content
        |                       |
        |                       v
        |              Add to conversation context
        |                       |
        +----------+------------+
                   |
                   v
          LLM generates response
                   |
                   v
          Response with Rich Formatting
```

### Future Enhancement (Phase 6 - Optional)

- **Tier 3 Resources**: Load supplementary files (style guides, schemas, etc.) on demand
- Already working for most use cases with Tier 1 + 2!

## Why Progressive Disclosure?

**The Problem**: Modern LLMs have limited context windows. Loading everything upfront:
- Wastes tokens on irrelevant information
- Increases latency and cost
- Hits context window limits quickly
- Makes agents slower and less focused

**The Solution**: Progressive Disclosure lets agents:
- Start with minimal context (just skill names/descriptions)
- Load full instructions only when a skill is relevant
- Access detailed resources only for specific edge cases
- Scale to effectively unlimited procedural knowledge
- Maintain fast response times and low costs

## Creating Skills

### Skill Structure

```
skills/
└── code_review/
    ├── SKILL.md              # Main skill definition (Tier 2)
    ├── style_guide.md        # Tier 3 resource
    ├── security_patterns.md  # Tier 3 resource
    └── examples/             # Optional examples
```

### Example SKILL.md

```markdown
---
name: code_review
description: Review code for best practices, style, and security
version: 1.0.0
author: Your Name
resources:
  - style_guide.md
  - security_patterns.md
---

# Code Review Skill

This skill analyzes code submissions for quality, style, and security issues.

## Review Process
1. Check style adherence (see style_guide.md for standards)
2. Identify security vulnerabilities (see security_patterns.md)
3. Suggest performance improvements
4. Provide actionable feedback
```

## Use Cases

- **Code Generation & Review**: Language-specific best practices, framework patterns, testing strategies
- **Data Processing**: ETL patterns, statistical analysis, data validation, visualization
- **DevOps & Automation**: Deployment workflows, infrastructure management, monitoring setup
- **Documentation**: API docs, README generation, tutorial writing, diagram creation
- **Testing**: Test generation, coverage analysis, test data creation
- **General Productivity**: Email drafting, meeting notes, research summarization

## Inspiration

This project is inspired by [Claude Code's Agent Skills system](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) but built to be:
- **LLM-agnostic**: Works with any LLM provider
- **Portable**: Standalone Python library
- **Open**: Transparent architecture for community contributions
- **Flexible**: Adaptable to various use cases beyond code generation

## Comparison with Claude Code Skills

| Feature | Claude Code Skills | Simple Agent |
|---------|-------------------|--------------|
| **LLM Support** | Claude only | Any LLM (via LiteLLM) |
| **Environment** | VSCode extension | Standalone library |
| **Skill Format** | SKILL.md | SKILL.md (compatible) |
| **Progressive Disclosure** | Yes (3 tiers) | Yes (Tier 1 & 2 working!) |
| **Code Execution** | Built-in | Planned |
| **Test Coverage** | Unknown | 117 tests, TDD approach |
| **Status** | Production | Phase 5 Complete |

### Migration from Claude Code Skills

Simple Agent will use the same SKILL.md format, making migration straightforward:

1. Copy your skill directories
2. Update any Claude-specific tool calls
3. Test with your preferred LLM
4. Adjust prompts if needed for different models

## Project Status

**Current Phase**: Phase 5 Complete ✓

**Completed:**
- ✅ Phase 0: Testing Infrastructure (pytest, fixtures)
- ✅ Phase 1: SkillValidator (12 tests)
- ✅ Phase 2: SkillPathResolver (28 tests)
- ✅ Phase 3: SkillLoader (26 tests)
- ✅ Phase 4: SkillRegistry (32 tests)
- ✅ Phase 5: PromptBuilder (19 tests)
- ✅ Phase 7: Tool Integration (load_skill tool)
- ✅ Phase 8: Agent Integration (E2E verified)

**Next Phase**: Phase 6 - ContentLoader (Tier 3 resources - optional enhancement)

See [SkillRoadmap.md](./SkillRoadmap.md) for detailed implementation plan.

## API Reference

### SimpleAgent

```python
class SimpleAgent:
    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None,
        timeout: int = 30,
        tool_registry: Optional[ToolRegistry] = None,
        max_iterations: int = 15,
        skills_dir: Optional[str] = None,
        enable_skills: bool = True
    )
```

**Parameters:**
- `model`: LiteLLM model identifier (default: from LITELLM_MODEL env var)
- `api_key`: API key for model provider (default: from OPENROUTER_API_KEY env var)
- `system_prompt`: Custom system prompt (optional)
- `timeout`: Request timeout in seconds (default: 30)
- `tool_registry`: Custom tool registry (optional, created automatically if None)
- `max_iterations`: Maximum agent loop iterations (default: 15)
- `skills_dir`: Path to skills directory (default: ./skills/ and ~/.simple-agent/skills/)
- `enable_skills`: Enable skills system (default: True)

**Methods:**

- `run(task: str) -> Dict[str, Any]` - Execute single-turn task with agent loop
- `chat(message: str) -> str` - Multi-turn conversation (no tools)
- `reset()` - Clear conversation history

**Returns (run method):**
```python
{
    "success": bool,
    "result": str,
    "iterations": int,  # Number of agent loop iterations
    "usage": {
        "prompt_tokens": int,
        "completion_tokens": int,
        "total_tokens": int
    }
}
```

## Contributing

We welcome contributions! Areas of interest:
- Creating new skills for common use cases
- Tier 3 resource loading (ContentLoader)
- Additional LLM provider integrations
- Performance optimizations
- Documentation improvements
- Bug reports and feature requests

**Development Setup:**
```powershell
# Clone and setup
git clone https://github.com/satish860/simple-agent
cd simple-agent
uv sync

# Run tests
uv run pytest tests/ -v

# Run E2E tests
uv run python examples/test_skills_e2e.py
```

## Dependencies

- **Python**: >=3.12
- **LiteLLM**: >=1.56.3 (LLM abstraction layer)
- **python-dotenv**: >=1.0.0 (Environment management)
- **rich**: >=13.7.0 (Beautiful console output)
- **pyyaml**: >=6.0.0 (SKILL.md frontmatter parsing)

**Development Dependencies:**
- **pytest**: >=8.4.2 (Testing framework)
- **pytest-cov**: >=7.0.0 (Coverage reporting)

## License

[To be determined]

## Resources

- [Anthropic's Agent Skills Article](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Project Roadmap](./ROADMAP.md)
- [Project Architecture Details](./CLAUDE.md)

## Contact

GitHub: [satish860/simple-agent](https://github.com/satish860/simple-agent)
