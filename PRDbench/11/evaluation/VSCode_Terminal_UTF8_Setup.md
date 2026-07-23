# VSCode Terminal UTF-8 Encoding Configuration Guide

## Completed Configuration

I have created a `.vscode/settings.json` configuration file for this project with the following settings:

```json
{
    "terminal.integrated.env.windows": {
        "PYTHONIOENCODING": "utf-8"
    },
    "terminal.integrated.profiles.windows": {
        "Command Prompt UTF-8": {
            "path": "C:\\windows\\System32\\cmd.exe",
            "args": ["/k", "chcp 65001"]
        }
    },
    "terminal.integrated.defaultProfile.windows": "Command Prompt UTF-8"
}
```

## Steps to Activate Configuration

### Method 1: Reload VSCode Window
1. Press `Ctrl + Shift + P` to open the command palette
2. Type `Developer: Reload Window`
3. Press Enter, VSCode will reload

### Method 2: Create New Terminal
1. Close the current terminal (click the trash icon)
2. Press `Ctrl + Shift + `` to create a new terminal
3. The new terminal will automatically apply UTF-8 configuration

### Method 3: Manually Select Terminal Profile
1. Click the dropdown arrow next to `+` in the upper right corner of the terminal
2. Select "Command Prompt UTF-8"
3. The new terminal will use UTF-8 encoding

## Verify Configuration is Effective

After creating a new terminal, run the following commands to verify:

```bash
# Check code page (should display 65001)
chcp

# Check Python encoding environment variable
echo %PYTHONIOENCODING%

# Test Chinese character display
python evaluation/verify_file_comparison_test.py
```

## Expected Results

- `chcp` should display `Active code page: 65001`
- `echo %PYTHONIOENCODING%` should display `utf-8`
- Python script's Chinese output should display normally without garbled characters

## Additional Notes

- This configuration is only effective for the current project (workspace-level settings)
- To make it effective globally, add the same configuration to user settings
- Configuration file location: `.vscode/settings.json`