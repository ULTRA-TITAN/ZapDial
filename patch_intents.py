import os
import re

def wrap_start_activity(content):
    # Regex to find context.startActivity(intent) that isn't already wrapped in try-catch
    # This is tricky with regex, so let's do a line-by-line approach or find specific cases.
    
    # We will look for context.startActivity(something) and replace it if not inside a try block on the same line.
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'startActivity(' in line and 'try' not in line:
            # indent
            indent = line[:len(line) - len(line.lstrip())]
            lines[i] = f"{indent}try {{ {line.strip()} }} catch (e: Exception) {{ android.widget.Toast.makeText(context, \"Action unavailable\", android.widget.Toast.LENGTH_SHORT).show() }}"
    
    return '\n'.join(lines)

for root, _, files in os.walk('/app/applet/app/src/main/java'):
    for file in files:
        if file.endswith('.kt'):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()
            
            new_content = wrap_start_activity(content)
            if new_content != content:
                with open(path, 'w') as f:
                    f.write(new_content)
