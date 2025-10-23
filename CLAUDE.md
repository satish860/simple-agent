# Simple Agent - LLM-Agnostic Progressive Disclosure Architecture

## Project Overview

Simple Agent is a Python SDK that implements Progressive Disclosure Architecture for LLM agents, enabling them to work with modular, self-contained skills that load information dynamically based on relevance and need.

### What is Progressive Disclosure Architecture?

Progressive Disclosure Architecture is a design pattern where information is revealed incrementally rather than all at once. Instead of loading massive context windows with every possible detail, the system provides information in three tiers:

1. **Tier 1 - Metadata**: Lightweight skill descriptions loaded at startup
2. **Tier 2 - Instructions**: Full skill details loaded when deemed relevant
3. **Tier 3 - Resources**: Supplementary materials loaded only when specific scenarios require them

Think of it like a well-organized manual that starts with a table of contents, then specific chapters, and finally a detailed appendix - information loads only as needed.

### Why Progressive Disclosure?

**The Problem**: Modern LLMs have limited context windows. To build capable agents, you need to provide extensive instructions, examples, and domain knowledge. But loading everything upfront:
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

### Inspiration

This project is inspired by Claude Code's Agent Skills system (https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) but built to be:
- **LLM-agnostic**: Works with any LLM provider (OpenAI, Anthropic, local models, etc.)
- **Portable**: Standalone Python library, not tied to specific IDEs
- **Open**: Transparent architecture for community contributions
- **Flexible**: Adaptable to various use cases beyond code generation

---

## Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                         User Query                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         v
┌─────────────────────────────────────────────────────────────┐
│                      Agent Runtime                          │
│  ┌───────────────────────────────────────────────────┐      │
│  │  System Prompt (Tier 1 - Metadata)                │      │
│  │  - code_review: Review code for best practices    │      │
│  │  - data_analyzer: Process and analyze datasets    │      │
│  │  - git_helper: Automate git workflows             │      │
│  └───────────────────────────────────────────────────┘      │
│                         │                                    │
│                         v                                    │
│  ┌───────────────────────────────────────────────────┐      │
│  │         LLM determines relevance                  │      │
│  │  "User wants code review -> load code_review"     │      │
│  └───────────────────────────────────────────────────┘      │
│                         │                                    │
│                         v                                    │
│  ┌───────────────────────────────────────────────────┐      │
│  │  Tool Call: load_skill("code_review")             │      │
│  └───────────────────────────────────────────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         v
┌─────────────────────────────────────────────────────────────┐
│                  Progressive Disclosure Engine              │
│                                                              │
│  Tier 2: Load SKILL.md                                      │
│  ┌────────────────────────────────────────────────┐         │
│  │ # Code Review Skill                            │         │
│  │                                                 │         │
│  │ Analyze code for:                               │         │
│  │ - Style violations (see style_guide.md)        │         │
│  │ - Security issues (see security_patterns.md)   │         │
│  │ - Performance problems                          │         │
│  │ ...                                             │         │
│  └────────────────────────────────────────────────┘         │
│                         │                                    │
│  (If agent needs more details)                              │
│                         │                                    │
│                         v                                    │
│  Tier 3: Load Resources                                     │
│  ┌────────────────────────────────────────────────┐         │
│  │ style_guide.md: PEP 8 conventions              │         │
│  │ security_patterns.md: OWASP top 10             │         │
│  └────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                         │
                         v
┌─────────────────────────────────────────────────────────────┐
│              LLM generates response with full context       │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. LLM Abstraction Layer
**Purpose**: Provide unified interface across different LLM providers

**Components**:
- `BaseLLM`: Abstract base class defining standard interface
- `OpenRouterLLM`: OpenRouter implementation (supports 100+ models)
- `LLMConfig`: Configuration management for API keys, models, parameters

**Key Features**:
- Standardized message format
- Tool/function calling abstraction
- Streaming support
- Error handling and retry logic
- Model switching without code changes

#### 2. Skill System
**Purpose**: Define, validate, and manage modular agent capabilities

**Skill Structure**:
```
skills/
└── code_review/
    ├── SKILL.md              # Main skill definition
    ├── style_guide.md        # Tier 3 resource
    ├── security_patterns.md  # Tier 3 resource
    └── examples/             # Optional examples
        ├── good_example.py
        └── bad_example.py
```

**SKILL.md Format**:
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

## Usage
When reviewing code:
- Be constructive and specific
- Prioritize critical issues
- Suggest concrete improvements
- Reference style guide sections
```

**Components**:
- `SkillLoader`: Discovers and loads skills from directories
- `SkillRegistry`: Indexes and manages available skills
- `SkillValidator`: Validates skill structure and content

#### 3. Progressive Disclosure Engine
**Purpose**: Implement three-tier loading mechanism

**How It Works**:

**Tier 1 - System Prompt Injection**:
At agent initialization, inject lightweight metadata:
```
You have access to the following skills:
- code_review: Review code for best practices, style, and security
- data_analyzer: Process and analyze datasets with statistical methods
- git_helper: Automate git workflows and resolve common issues
...

Use load_skill(name) to access detailed instructions when needed.
```

**Tier 2 - Dynamic Skill Loading**:
When agent calls `load_skill("code_review")`:
1. Retrieve full SKILL.md content
2. Parse and format for LLM consumption
3. Inject into conversation context
4. Track loaded skills to avoid reloading

**Tier 3 - Resource Loading**:
When agent needs specific details:
1. Parse resource links from SKILL.md
2. Load referenced files on demand
3. Format and append to context
4. Cache for potential reuse

**Components**:
- `PromptBuilder`: Constructs system prompts with Tier 1 metadata
- `SkillLoader`: Handles Tier 2 skill loading
- `ResourceManager`: Manages Tier 3 resource loading
- `ContextTracker`: Monitors token usage and manages context window

#### 4. Agent Runtime
**Purpose**: Orchestrate agent execution with progressive disclosure

**Components**:
- `Agent`: Main agent class that users interact with
- `ConversationManager`: Tracks conversation state and history
- `ToolRegistry`: Manages available tools (including skill loading)
- `ExecutionEngine`: Handles code execution within skills

**Execution Flow**:
1. User submits query
2. Agent constructs prompt with Tier 1 metadata
3. LLM processes query and determines if skills needed
4. If relevant, LLM calls `load_skill` tool
5. Engine loads Tier 2 content
6. LLM may request Tier 3 resources
7. Engine loads additional resources
8. LLM generates response with full context
9. Response returned to user

---

## LLM Agnostic Design

### Why LLM Agnostic?

- **Future-proof**: New models emerge constantly
- **Flexibility**: Choose best model for each use case
- **Cost optimization**: Switch to cheaper models when possible
- **Vendor independence**: Avoid lock-in
- **Local options**: Support offline/private deployments

### Abstraction Strategy

All LLM-specific details are isolated in provider implementations:

```python
class BaseLLM(ABC):
    @abstractmethod
    def generate(self, messages: list[Message], tools: list[Tool]) -> Response:
        """Generate response from LLM"""
        pass

    @abstractmethod
    def stream(self, messages: list[Message], tools: list[Tool]) -> Iterator[Chunk]:
        """Stream response from LLM"""
        pass

class OpenRouterLLM(BaseLLM):
    """OpenRouter implementation supporting 100+ models"""

    def generate(self, messages, tools):
        # Convert to OpenAI-compatible format
        # Make API call
        # Parse response
        # Handle tool calls
        pass
```

### OpenRouter Integration

OpenRouter provides a unified API for 100+ models from multiple providers:
- Anthropic (Claude)
- OpenAI (GPT-4, GPT-3.5)
- Google (Gemini)
- Meta (Llama)
- Mistral
- Cohere
- And many more

**Benefits**:
- Single API key for all models
- Consistent interface across providers
- Automatic failover and load balancing
- Usage tracking and cost management
- No vendor-specific SDK dependencies

---

## Skill Development Guide

### Creating Your First Skill

1. **Create skill directory**:
```powershell
mkdir skills\my_skill
```

2. **Create SKILL.md**:
```markdown
---
name: my_skill
description: Brief description for Tier 1 metadata
version: 1.0.0
---

# My Skill

Detailed instructions here (Tier 2)...

## How to Use
...

## Examples
...
```

3. **Add resources** (optional):
```
skills\my_skill\
├── SKILL.md
├── reference.md
└── examples.md
```

4. **Test your skill**:
```python
from simple_agent import Agent
from simple_agent.llm import OpenRouterLLM

agent = Agent(
    llm=OpenRouterLLM(model="anthropic/claude-3.5-haiku"),
    skills_dir="./skills"
)

response = agent.run("Use my_skill to...")
```

### Best Practices

**Tier 1 Metadata**:
- Keep description under 100 characters
- Focus on what, not how
- Use clear, searchable keywords
- Examples: "Review code for quality issues", "Analyze datasets statistically"

**Tier 2 Instructions**:
- Start with overview
- Provide step-by-step process
- Link to Tier 3 resources sparingly
- Include examples inline for common cases
- Keep focused - split complex skills

**Tier 3 Resources**:
- Use for reference materials (style guides, schemas)
- Include detailed examples
- Provide edge case documentation
- Format for easy scanning (headers, lists, tables)

**Code Scripts**:
- Embed deterministic operations as code
- Faster and more reliable than LLM generation
- Examples: parsing, validation, formatting
- Always handle errors gracefully

---

## Use Cases

### Code Generation & Review
Skills for language-specific best practices, framework patterns, testing strategies

### Data Processing
Skills for ETL patterns, statistical analysis, data validation, visualization

### DevOps & Automation
Skills for deployment workflows, infrastructure management, monitoring setup

### Documentation
Skills for API docs, README generation, tutorial writing, diagram creation

### Testing
Skills for test generation, coverage analysis, test data creation

### General Productivity
Skills for email drafting, meeting notes, research summarization

---

## Comparison with Claude Code Skills

| Feature | Claude Code Skills | Simple Agent |
|---------|-------------------|--------------|
| **LLM Support** | Claude only | Any LLM (via OpenRouter) |
| **Environment** | VSCode extension | Standalone library |
| **Skill Format** | SKILL.md | SKILL.md (compatible) |
| **Progressive Disclosure** | Yes (3 tiers) | Yes (3 tiers) |
| **Code Execution** | Built-in | Built-in |
| **Use Cases** | Code development | General purpose |
| **Distribution** | Local directories | Local directories |
| **Migration** | N/A | Easy from Claude Code |

### Migration from Claude Code Skills

Simple Agent skills use the same SKILL.md format, making migration straightforward:

1. Copy your skill directories
2. Update any Claude-specific tool calls
3. Test with your preferred LLM
4. Adjust prompts if needed for different models

---

## Technical Decisions

### Why Python?
- Rich LLM ecosystem
- Excellent for rapid development
- Strong typing with type hints
- Great packaging tools (uv)
- Cross-platform support

### Why OpenRouter First?
- Single integration supports 100+ models
- Reduces initial development complexity
- Provides model flexibility from day one
- Can add direct provider support later

### Why YAML + Markdown?
- Human-readable and editable
- Standard formats with broad tool support
- Easy to version control
- Natural separation of metadata and content

### Why Local Directory Structure?
- Simple to understand and debug
- No complex package management
- Easy to share and version
- Natural organization
- Future: can add package-based distribution

---

## Getting Started

### Installation
```powershell
# Once published
uv add simple-agent

# For development
git clone https://github.com/yourusername/simple-agent
cd simple-agent
uv sync
```

### Basic Usage
```python
from simple_agent import Agent
from simple_agent.llm import OpenRouterLLM
import os

# Initialize LLM
llm = OpenRouterLLM(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="anthropic/claude-3.5-haiku"
)

# Create agent with skills
agent = Agent(
    llm=llm,
    skills_dir="./skills"
)

# Run query
response = agent.run("Review this Python code for best practices")
print(response)
```

### With Streaming
```python
for chunk in agent.stream("Analyze this dataset"):
    print(chunk, end="", flush=True)
```

---

## Project Status

**Current Phase**: Planning and Documentation
**Next Phase**: Phase 1 - Foundation & Core Architecture

See [ROADMAP.md](./ROADMAP.md) for detailed implementation plan.

---

## Contributing

We welcome contributions! Areas of interest:
- New skill implementations
- Additional LLM provider integrations
- Performance optimizations
- Documentation improvements
- Bug reports and feature requests

---

## License

[To be determined]

---

## Resources

- **Anthropic's Agent Skills Article**: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- **OpenRouter Documentation**: https://openrouter.ai/docs
- **Project Roadmap**: [ROADMAP.md](./ROADMAP.md)

---

## Contact

[To be determined]
