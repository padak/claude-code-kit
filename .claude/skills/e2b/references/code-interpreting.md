# Code Interpreting and Data Analysis

## Overview

E2B Sandbox is ideal for running AI-generated code to analyze data, create visualizations, and perform computations. This guide covers common patterns for code interpreting with AI.

## Typical Workflow

1. User provides dataset (CSV, JSON, Excel, etc.)
2. LLM generates analysis code based on user request
3. Sandbox executes the code
4. Extract and return results (text, charts, tables)

## Running Python Code

### Basic Execution

**Python:**
```python
from e2b_code_interpreter import Sandbox

sandbox = Sandbox.create()

# Run code
execution = sandbox.run_code('print("hello world")')

# Access results
print(execution.text)         # Combined output
print(execution.logs.stdout)  # Standard output
print(execution.logs.stderr)  # Standard error
print(execution.results)      # Charts, tables, etc.
```

**JavaScript:**
```javascript
import { Sandbox } from '@e2b/code-interpreter'

const sandbox = await Sandbox.create()

// Run code
const execution = await sandbox.runCode('print("hello world")')

// Access results
console.log(execution.text)        // Combined output
console.log(execution.logs.stdout) // Standard output
console.log(execution.logs.stderr) // Standard error
console.log(execution.results)     // Charts, tables, etc.
```

### Handling Execution Results

```python
execution = sandbox.run_code(code)

# Check for errors
if execution.error:
    print(f"Error: {execution.error.name}")
    print(f"Message: {execution.error.value}")
    print(f"Traceback:\n{execution.error.traceback}")
else:
    # Process successful results
    print(f"Output: {execution.text}")

    # Process different result types
    for result in execution.results:
        if result.png:
            # Save chart/image (base64 encoded)
            save_base64_image(result.png, 'chart.png')
        elif result.jpeg:
            save_base64_image(result.jpeg, 'image.jpg')
        elif result.html:
            save_html(result.html, 'output.html')
        elif result.text:
            print(f"Text result: {result.text}")
```

## Data Analysis Pattern

### Complete Example: CSV Analysis

```python
from e2b_code_interpreter import Sandbox
from anthropic import Anthropic
import base64

# 1. Create sandbox
sandbox = Sandbox.create()

# 2. Upload dataset
with open('sales_data.csv', 'rb') as f:
    content = f.read()
dataset_path = sandbox.files.write('/home/user/sales.csv', content)

# 3. Prepare analysis request
client = Anthropic()
prompt = f"""
I have a sales dataset at {dataset_path.path}.
Columns: date, product, quantity, revenue

Analyze:
1. Total revenue by product
2. Monthly sales trend
3. Top 10 selling products

Create a visualization showing the monthly revenue trend.
"""

# 4. Define tool for code execution
tools = [{
    "name": "execute_python",
    "description": "Execute python code in a Jupyter notebook",
    "input_schema": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to execute"
            }
        },
        "required": ["code"]
    }
}]

# 5. Get code from LLM
message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=2048,
    messages=[{"role": "user", "content": prompt}],
    tools=tools
)

# 6. Execute generated code
if message.stop_reason == "tool_use":
    tool_use = next(block for block in message.content if block.type == "tool_use")
    if tool_use.name == "execute_python":
        code = tool_use.input['code']
        execution = sandbox.run_code(code)

        # 7. Process results
        if execution.error:
            print(f"Error: {execution.error.value}")
        else:
            # Save any charts generated
            for i, result in enumerate(execution.results):
                if result.png:
                    # Decode base64 and save
                    img_data = base64.b64decode(result.png)
                    with open(f'chart_{i}.png', 'wb') as f:
                        f.write(img_data)
                    print(f"Saved chart_{i}.png")

            # Print text output
            print(execution.text)

# 8. Clean up
sandbox.kill()
```

## Working with Different Data Formats

### CSV Files

```python
# Upload CSV
dataset = sandbox.files.write('/home/user/data.csv', csv_content)

# Analyze
code = f"""
import pandas as pd

df = pd.read_csv('{dataset.path}')
print(df.describe())
print(df.head())
"""
result = sandbox.run_code(code)
print(result.text)
```

### JSON Files

```python
import json

# Upload JSON
data = {'sales': [100, 200, 300]}
json_str = json.dumps(data)
sandbox.files.write('/home/user/data.json', json_str.encode('utf-8'))

# Analyze
code = """
import json
import pandas as pd

with open('/home/user/data.json') as f:
    data = json.load(f)

df = pd.DataFrame(data)
print(df.describe())
"""
result = sandbox.run_code(code)
```

### Excel Files

```python
# Upload Excel file
with open('workbook.xlsx', 'rb') as f:
    content = f.read()
sandbox.files.write('/home/user/data.xlsx', content)

# Analyze
code = """
import pandas as pd

# Read all sheets
excel_file = pd.ExcelFile('/home/user/data.xlsx')
sheets = {sheet: excel_file.parse(sheet) for sheet in excel_file.sheet_names}

for name, df in sheets.items():
    print(f"Sheet: {name}")
    print(df.head())
    print()
"""
result = sandbox.run_code(code)
```

## Creating Visualizations

### Matplotlib Charts

```python
code = """
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y)
plt.title('Sine Wave')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)
plt.savefig('/home/user/sine_wave.png', dpi=150, bbox_inches='tight')
plt.show()  # This triggers the result
"""

execution = sandbox.run_code(code)

# Extract chart
for result in execution.results:
    if result.png:
        # result.png is base64 encoded
        import base64
        img_data = base64.b64decode(result.png)
        with open('sine_wave.png', 'wb') as f:
            f.write(img_data)
```

### Seaborn Visualizations

```python
code = """
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Create sample data
df = pd.DataFrame({
    'category': ['A', 'B', 'C', 'D'] * 5,
    'value': np.random.randn(20)
})

plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='category', y='value')
plt.title('Distribution by Category')
plt.savefig('/home/user/boxplot.png')
plt.show()
"""

execution = sandbox.run_code(code)
```

### Plotly Interactive Charts

```python
code = """
import plotly.graph_objects as go

fig = go.Figure(data=go.Scatter(
    x=[1, 2, 3, 4],
    y=[10, 11, 12, 13]
))

fig.update_layout(title='Interactive Chart')
fig.write_html('/home/user/chart.html')
fig.show()
"""

execution = sandbox.run_code(code)

# Download HTML chart
html_content = sandbox.files.read('/home/user/chart.html')
with open('chart.html', 'wb') as f:
    f.write(html_content)
```

## Multi-Step Analysis

For complex analysis, execute code in steps:

```python
sandbox = Sandbox.create(timeout=300)

# Step 1: Load data
sandbox.run_code("""
import pandas as pd
df = pd.read_csv('/home/user/sales.csv')
df['date'] = pd.to_datetime(df['date'])
print(f"Loaded {len(df)} rows")
""")

# Step 2: Clean data
sandbox.run_code("""
# Remove outliers
Q1 = df['revenue'].quantile(0.25)
Q3 = df['revenue'].quantile(0.75)
IQR = Q3 - Q1
df_clean = df[(df['revenue'] >= Q1 - 1.5*IQR) & (df['revenue'] <= Q3 + 1.5*IQR)]
print(f"After cleaning: {len(df_clean)} rows")
""")

# Step 3: Aggregate
result = sandbox.run_code("""
monthly = df_clean.groupby(df_clean['date'].dt.to_period('M'))['revenue'].sum()
print(monthly)
""")

print(result.text)

sandbox.kill()
```

## Pre-installed Libraries

E2B sandboxes come with many popular Python libraries:

**Data Analysis:**
- pandas
- numpy
- scipy
- statsmodels

**Visualization:**
- matplotlib
- seaborn
- plotly

**Machine Learning:**
- scikit-learn
- tensorflow
- pytorch

**Others:**
- requests
- beautifulsoup4
- pillow

See full list: https://e2b.dev/docs/code-interpreting/analyze-data-with-ai/pre-installed-libraries

## Installing Additional Packages

```python
# Install packages during execution
code = """
!pip install xgboost

import xgboost as xgb
print(f"XGBoost version: {xgb.__version__}")
"""

execution = sandbox.run_code(code)
```

## Error Handling

### Comprehensive Error Handling

```python
def safe_execute(sandbox, code):
    """Execute code with comprehensive error handling"""
    try:
        execution = sandbox.run_code(code)

        if execution.error:
            # Runtime error in code
            error_info = {
                'type': execution.error.name,
                'message': execution.error.value,
                'traceback': execution.error.traceback
            }
            return {'success': False, 'error': error_info}

        # Successful execution
        results = {
            'success': True,
            'text': execution.text,
            'stdout': execution.logs.stdout,
            'stderr': execution.logs.stderr,
            'charts': [],
            'html': []
        }

        # Extract different result types
        for result in execution.results:
            if result.png:
                results['charts'].append(result.png)
            elif result.html:
                results['html'].append(result.html)

        return results

    except Exception as e:
        # SDK or network error
        return {
            'success': False,
            'error': {
                'type': 'SDKError',
                'message': str(e)
            }
        }

# Usage
result = safe_execute(sandbox, llm_generated_code)
if result['success']:
    print(result['text'])
    for chart in result['charts']:
        save_chart(chart)
else:
    print(f"Error: {result['error']['message']}")
```

## Best Practices

### 1. Set Appropriate Timeout

```python
# Quick analysis: 60-120 seconds
sandbox = Sandbox.create(timeout=120)

# Complex processing: 300-600 seconds
sandbox = Sandbox.create(timeout=600)

# Very long tasks: Use persistence
sandbox = Sandbox.beta_create(auto_pause=True, timeout=600)
```

### 2. Upload Data Before Running Code

```python
# Good: Upload first
sandbox.files.write('/home/user/data.csv', dataset)
result = sandbox.run_code(f"df = pd.read_csv('/home/user/data.csv')")

# Bad: Inline data (size limits, slower)
code = f"""
data = {large_list}
df = pd.DataFrame(data)
"""
```

### 3. Save Outputs to Files

```python
# Generate outputs and save
code = """
import matplotlib.pyplot as plt

# ... create chart ...
plt.savefig('/home/user/output.png')

# ... generate report ...
with open('/home/user/report.txt', 'w') as f:
    f.write(report)
"""

sandbox.run_code(code)

# Download outputs
chart = sandbox.files.read('/home/user/output.png')
report = sandbox.files.read('/home/user/report.txt')
```

### 4. Validate LLM-Generated Code

```python
def validate_code(code):
    """Basic validation of LLM-generated code"""
    dangerous_patterns = [
        'import os',
        'import subprocess',
        'eval(',
        'exec(',
        '__import__',
    ]

    for pattern in dangerous_patterns:
        if pattern in code:
            return False, f"Potentially dangerous pattern: {pattern}"

    return True, "Code validated"

# Use before execution
is_safe, message = validate_code(llm_code)
if is_safe:
    execution = sandbox.run_code(llm_code)
else:
    print(f"Code validation failed: {message}")
```

## Common Patterns

### Pattern 1: Quick Data Summary

```python
with Sandbox.create() as sandbox:
    # Upload data
    sandbox.files.write('/home/user/data.csv', dataset)

    # Get summary
    result = sandbox.run_code("""
    import pandas as pd
    df = pd.read_csv('/home/user/data.csv')
    print(df.info())
    print(df.describe())
    print(df.head())
    """)

    print(result.text)
```

### Pattern 2: Generate Multiple Charts

```python
sandbox = Sandbox.create()
sandbox.files.write('/home/user/sales.csv', data)

# Generate multiple visualizations
code = """
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('/home/user/sales.csv')

# Chart 1: Revenue by product
df.groupby('product')['revenue'].sum().plot(kind='bar')
plt.title('Revenue by Product')
plt.savefig('/home/user/chart1.png')
plt.close()

# Chart 2: Monthly trend
df.groupby('month')['revenue'].sum().plot()
plt.title('Monthly Trend')
plt.savefig('/home/user/chart2.png')
plt.close()
"""

sandbox.run_code(code)

# Download both charts
chart1 = sandbox.files.read('/home/user/chart1.png')
chart2 = sandbox.files.read('/home/user/chart2.png')

sandbox.kill()
```

### Pattern 3: Interactive Analysis Session

```python
# Start session
sandbox = Sandbox.beta_create(auto_pause=True, timeout=600)

# Load data once
sandbox.files.write('/home/user/dataset.csv', data)
sandbox.run_code("import pandas as pd; df = pd.read_csv('/home/user/dataset.csv')")

# User asks multiple questions
for user_query in user_queries:
    # Generate code for each query
    analysis_code = llm.generate_code(user_query)

    # Execute
    result = sandbox.run_code(analysis_code)

    # Return results
    yield result

# Pause when done
sandbox.beta_pause()
```
