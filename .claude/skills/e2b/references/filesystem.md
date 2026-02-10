# Filesystem Operations

## Overview

Each E2B Sandbox has an isolated filesystem with:
- **Hobby tier**: 1 GB free disk space
- **Pro tier**: 5 GB disk space

The filesystem is completely isolated from other sandboxes and the host system.

## File Operations

### Writing Files

Upload files from your local system to the sandbox.

**Python:**
```python
from e2b_code_interpreter import Sandbox

sandbox = Sandbox.create()

# Read local file
with open('local/file.csv', 'rb') as f:
    content = f.read()

# Write to sandbox (use absolute paths)
file_info = sandbox.files.write('/home/user/data.csv', content)
print(file_info.path)  # '/home/user/data.csv'
```

**JavaScript:**
```javascript
import fs from 'fs'
import { Sandbox } from '@e2b/code-interpreter'

const sandbox = await Sandbox.create()

// Read local file
const content = fs.readFileSync('local/file.csv')

// Write to sandbox
const fileInfo = await sandbox.files.write('/home/user/data.csv', content)
console.log(fileInfo.path)
```

**Important:**
- Always use absolute paths (start with `/`)
- Recommended base directory: `/home/user/`
- File info includes: path, timestamp, size

### Reading Files

Download files from the sandbox to your local system.

**Python:**
```python
# Read file from sandbox
content = sandbox.files.read('/home/user/output.png')

# Save locally
with open('local/output.png', 'wb') as f:
    f.write(content)
```

**JavaScript:**
```javascript
// Read file from sandbox
const content = await sandbox.files.read('/home/user/output.png')

// Save locally
fs.writeFileSync('local/output.png', content)
```

### Listing Files

List files and directories in the sandbox.

**Python:**
```python
# List files in directory
files = sandbox.files.list('/home/user')

for file in files:
    print(f"Name: {file.name}")
    print(f"Path: {file.path}")
    print(f"Is Directory: {file.is_dir}")
    print(f"Size: {file.size} bytes")
```

**JavaScript:**
```javascript
// List files in directory
const files = await sandbox.files.list('/home/user')

for (const file of files) {
    console.log(`Name: ${file.name}`)
    console.log(`Path: ${file.path}`)
    console.log(`Is Directory: ${file.isDir}`)
    console.log(`Size: ${file.size} bytes`)
}
```

### Deleting Files

**Python:**
```python
# Remove a file
sandbox.files.remove('/home/user/temp.txt')

# Remove a directory (recursive)
sandbox.files.remove('/home/user/temp_dir')
```

**JavaScript:**
```javascript
// Remove a file
await sandbox.files.remove('/home/user/temp.txt')

// Remove a directory
await sandbox.files.remove('/home/user/temp_dir')
```

## Working with Multiple Files

### Uploading Multiple Files

Currently, files must be uploaded individually. E2B is working on batch operations.

**Python:**
```python
files_to_upload = {
    '/home/user/file-a.csv': content_a,
    '/home/user/file-b.csv': content_b,
    '/home/user/file-c.csv': content_c,
}

for path, content in files_to_upload.items():
    sandbox.files.write(path, content)
    print(f"Uploaded: {path}")
```

**JavaScript:**
```javascript
const filesToUpload = {
    '/home/user/file-a.csv': contentA,
    '/home/user/file-b.csv': contentB,
    '/home/user/file-c.csv': contentC,
}

for (const [path, content] of Object.entries(filesToUpload)) {
    await sandbox.files.write(path, content)
    console.log(`Uploaded: ${path}`)
}
```

### Downloading Multiple Files

**Python:**
```python
files_to_download = [
    '/home/user/output-a.png',
    '/home/user/output-b.png',
]

for remote_path in files_to_download:
    content = sandbox.files.read(remote_path)
    local_path = remote_path.replace('/home/user/', 'local/')
    with open(local_path, 'wb') as f:
        f.write(content)
    print(f"Downloaded: {local_path}")
```

### Directory Operations

**Create Directory:**
```python
# Use bash command
sandbox.commands.run('mkdir -p /home/user/data/raw')
```

**List Directory Recursively:**
```python
# Use bash command
result = sandbox.commands.run('find /home/user -type f')
print(result.stdout)
```

## Watching Filesystem Changes

Monitor directories for changes in real-time.

**Python:**
```python
# Watch directory for changes
def on_change(event):
    print(f"File changed: {event.path}")
    print(f"Event type: {event.type}")

watcher = sandbox.files.watch('/home/user/outputs', on_change)

# Do work that creates files
sandbox.run_code(code_that_creates_files)

# Stop watching
watcher.stop()
```

**JavaScript:**
```javascript
// Watch directory for changes
const watcher = await sandbox.files.watch('/home/user/outputs', (event) => {
    console.log(`File changed: ${event.path}`)
    console.log(`Event type: ${event.type}`)
})

// Do work that creates files
await sandbox.runCode(codeThereateFiles)

// Stop watching
await watcher.stop()
```

## File Paths Best Practices

### Use Absolute Paths

```python
# Good
sandbox.files.write('/home/user/data.csv', content)

# Bad - relative paths may not work as expected
sandbox.files.write('data.csv', content)
```

### Recommended Directory Structure

```
/home/user/
├── data/           # Input datasets
│   ├── raw/
│   └── processed/
├── outputs/        # Generated files
│   ├── charts/
│   └── reports/
└── scripts/        # Code files
```

### Creating the Structure

```python
sandbox.commands.run('''
mkdir -p /home/user/data/raw
mkdir -p /home/user/data/processed
mkdir -p /home/user/outputs/charts
mkdir -p /home/user/outputs/reports
mkdir -p /home/user/scripts
''')
```

## Common Patterns

### Pattern 1: Upload Dataset, Run Analysis, Download Results

```python
# 1. Upload dataset
with open('sales_data.csv', 'rb') as f:
    content = f.read()
sandbox.files.write('/home/user/data/sales.csv', content)

# 2. Run analysis
code = """
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('/home/user/data/sales.csv')
df.plot()
plt.savefig('/home/user/outputs/chart.png')
"""
sandbox.run_code(code)

# 3. Download result
chart = sandbox.files.read('/home/user/outputs/chart.png')
with open('sales_chart.png', 'wb') as f:
    f.write(chart)
```

### Pattern 2: Process Multiple Files

```python
# Upload multiple data files
for i, dataset in enumerate(datasets):
    path = f'/home/user/data/dataset_{i}.csv'
    sandbox.files.write(path, dataset)

# Process all at once
code = """
import pandas as pd
from pathlib import Path

data_files = list(Path('/home/user/data').glob('dataset_*.csv'))
dfs = [pd.read_csv(f) for f in data_files]
combined = pd.concat(dfs)
combined.to_csv('/home/user/outputs/combined.csv', index=False)
"""
sandbox.run_code(code)

# Download result
result = sandbox.files.read('/home/user/outputs/combined.csv')
```

### Pattern 3: Working with Binary Files

```python
# Upload image for processing
with open('input.jpg', 'rb') as f:
    image_data = f.read()
sandbox.files.write('/home/user/image.jpg', image_data)

# Process image
code = """
from PIL import Image

img = Image.open('/home/user/image.jpg')
img = img.resize((800, 600))
img.save('/home/user/output.jpg')
"""
sandbox.run_code(code)

# Download processed image
output = sandbox.files.read('/home/user/output.jpg')
with open('output.jpg', 'wb') as f:
    f.write(output)
```

## Handling Different File Types

### Text Files

```python
# Write text file
text = "Hello, World!"
sandbox.files.write('/home/user/message.txt', text.encode('utf-8'))

# Read text file
content = sandbox.files.read('/home/user/message.txt')
text = content.decode('utf-8')
```

### CSV Files

```python
import csv
import io

# Create CSV
output = io.StringIO()
writer = csv.writer(output)
writer.writerow(['Name', 'Age'])
writer.writerow(['Alice', 30])
csv_content = output.getvalue()

sandbox.files.write('/home/user/data.csv', csv_content.encode('utf-8'))
```

### JSON Files

```python
import json

# Write JSON
data = {'name': 'Alice', 'age': 30}
json_str = json.dumps(data)
sandbox.files.write('/home/user/data.json', json_str.encode('utf-8'))

# Read JSON
content = sandbox.files.read('/home/user/data.json')
data = json.loads(content.decode('utf-8'))
```

## Troubleshooting

### File Not Found Errors

```python
# Check if file exists before reading
files = sandbox.files.list('/home/user')
file_paths = [f.path for f in files]

if '/home/user/data.csv' in file_paths:
    content = sandbox.files.read('/home/user/data.csv')
else:
    print("File not found")
```

### Permission Errors

Files in `/home/user/` should always be writable. If you get permission errors:

```python
# Fix permissions
sandbox.commands.run('chmod -R 755 /home/user')
```

### Large File Handling

For files larger than 10MB, consider:
1. Compressing before upload
2. Uploading to cloud storage and downloading in sandbox
3. Processing in chunks

```python
# Download large file in sandbox
code = """
import urllib.request
url = 'https://example.com/large-dataset.csv'
urllib.request.urlretrieve(url, '/home/user/data.csv')
"""
sandbox.run_code(code)
```

### Disk Space Issues

Monitor disk usage:

```python
# Check disk usage
result = sandbox.commands.run('df -h /home/user')
print(result.stdout)

# Clean up temporary files
sandbox.commands.run('rm -rf /home/user/tmp/*')
```
