# FileSystemAgent

A LangChain-based agent that provides intelligent file system operations through natural language.

## Setup

1. Install dependencies:
```bash
make install
```

2. Set environment variable:
```bash
export ANTHROPIC_API_KEY=your_key_here
```

## Usage

1. Start the agent:
```bash
make start
```

2. Example commands:
```
- "List files in the current directory"
- "Search for all PDF files"
- "Create a new directory called 'docs'"
- "Move file.txt to backup/file.txt"
```

3. Try the example insurance company directory:
```bash
make example-build   # Create messy directory structure
make example-clean   # Clean up example
```

## Available Operations

- List directory contents
- Search files by pattern
- Read/write files
- Find text in files (grep)
- Create/remove directories
- Move/copy files
- Get file/path info
- Generate UUIDs
- Walk directory trees

## Files

- `agent.py`: Main agent implementation using LangChain
- `tool.py`: Core filesystem operations implementation
- `config.py`: LLM configuration (supports Claude, GPT-4, DeepSeek)
- `Makefile`: Project management commands
