with open('reports/EVALUATION_REPORT.md', 'r', encoding='utf-8', errors='replace') as f:
    text = f.read()

# Let's inspect git diff to see the clean version before the edit
import subprocess
result = subprocess.run(['git', 'show', 'HEAD:reports/EVALUATION_REPORT.md'], capture_output=True, text=True, encoding='utf-8', errors='replace')
original_text = result.stdout
print("Original text length:", len(original_text))

with open('reports/EVALUATION_REPORT.md', 'w', encoding='utf-8') as f:
    f.write(original_text)

print("Restored original clean UTF-8 text from HEAD.")
