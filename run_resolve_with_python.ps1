param(
    [string]$PythonPath = "D:\package\venv310\Scripts\python.exe",
    [string]$Input = "text_label.jsonl",
    [string]$Output = "resolved.jsonl",
    [string]$Conflicts = "conflicts.jsonl"
)

Write-Host "Running resolver with: $PythonPath"
& $PythonPath -m src.conflict_resolver --input $Input --output $Output --conflicts $Conflicts
