# E2B Quickstart Guide

## Installation

### Python
```bash
pip install e2b-code-interpreter dotenv
```

### JavaScript/TypeScript
```bash
npm i @e2b/code-interpreter dotenv
```

## Setup

### 1. Create E2B Account
- Sign up at https://e2b.dev/auth/sign-up
- New accounts get $100 in credits

### 2. Get API Key
1. Navigate to https://e2b.dev/dashboard?tab=keys
2. Copy your API key
3. Add to `.env` file:

```bash
E2B_API_KEY=e2b_***
```

## Basic Usage

### Python
```python
from e2b_code_interpreter import Sandbox

# Create sandbox (alive for 5 minutes by default)
sbx = Sandbox.create()

# Execute Python code
execution = sbx.run_code('print("hello world")')
print(execution.logs.stdout)

# List files
files = sbx.files.list('/')
print(files)

# Clean up
sbx.kill()
```

### JavaScript/TypeScript
```javascript
import 'dotenv/config'
import { Sandbox } from '@e2b/code-interpreter'

// Create sandbox
const sbx = await Sandbox.create()

// Execute Python code
const execution = await sbx.runCode('print("hello world")')
console.log(execution.logs)

// List files
const files = await sbx.files.list('/')
console.log(files)

// Clean up
await sbx.kill()
```

## Upload and Download Files

### Upload File

**Python:**
```python
import fs

# Read local file
content = fs.read_file('local/file.csv')

# Upload to sandbox (use absolute paths)
sbx.files.write('/home/user/my-file.csv', content)
```

**JavaScript:**
```javascript
import fs from 'fs'

// Read local file
const content = fs.readFileSync('local/file.csv')

// Upload to sandbox
await sbx.files.write('/home/user/my-file.csv', content)
```

### Download File

**Python:**
```python
# Download from sandbox
content = sbx.files.read('/home/user/output.png')

# Write to local file
fs.write_file('local/output.png', content)
```

**JavaScript:**
```javascript
// Download from sandbox
const content = await sbx.files.read('/home/user/output.png')

// Write to local file
fs.writeFileSync('local/output.png', content)
```

### Multiple Files

Currently, you must upload/download files one at a time. E2B is working on batch operations.

**Python:**
```python
# Upload multiple files
files_to_upload = {
    '/home/user/file-a.csv': content_a,
    '/home/user/file-b.csv': content_b,
}

for path, content in files_to_upload.items():
    sbx.files.write(path, content)
```

## Connecting LLMs

E2B works with any LLM through tool use (function calling).

### OpenAI Example

```python
from openai import OpenAI
from e2b_code_interpreter import Sandbox
import json

client = OpenAI()

# Define tool for code execution
tools = [{
    "type": "function",
    "function": {
        "name": "execute_python",
        "description": "Execute python code in a Jupyter notebook cell and return result",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The python code to execute in a single cell"
                }
            },
            "required": ["code"]
        }
    }
}]

# Send message
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": "Calculate how many r's are in the word 'strawberry'"
    }],
    tools=tools,
)

# Execute if tool was called
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        if tool_call.function.name == "execute_python":
            with Sandbox.create() as sandbox:
                code = json.loads(tool_call.function.arguments)['code']
                execution = sandbox.run_code(code)
                result = execution.text
                print(result)
```

### Anthropic Example

```python
from anthropic import Anthropic
from e2b_code_interpreter import Sandbox

client = Anthropic()

# Define tool
tools = [{
    "name": "execute_python",
    "description": "Execute python code in a Jupyter notebook cell and return result",
    "input_schema": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The python code to execute in a single cell"
            }
        },
        "required": ["code"]
    }
}]

# Send message
message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Calculate how many r's are in the word 'strawberry'"
    }],
    tools=tools
)

# Execute if tool was called
if message.stop_reason == "tool_use":
    tool_use = next(block for block in message.content if block.type == "tool_use")
    if tool_use.name == "execute_python":
        with Sandbox.create() as sandbox:
            code = tool_use.input['code']
            execution = sandbox.run_code(code)
            result = execution.text
            print(result)
```

## Next Steps

- Learn about [Sandbox Lifecycle](sandbox-lifecycle.md)
- Understand [File Operations](filesystem.md)
- Explore [Sandbox Persistence](persistence.md)
- See [Data Analysis Examples](code-interpreting.md)
