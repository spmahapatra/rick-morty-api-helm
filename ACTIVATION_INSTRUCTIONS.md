# Activating Slash Commands in VS Code - Complete Guide

## Step-by-Step Activation for VS Code Extension

### Option 1: Quick Reload (Recommended)

**Step 1: Open Command Palette**
```
Windows/Linux: Ctrl + Shift + P
Mac: Cmd + Shift + P
```

**Step 2: Execute Reload Command**
```
Type: Developer: Reload Window
Press: Enter
```

This will reload the entire VS Code window and discover the new `.kilo/commands/` directory.

**Expected Result**: VS Code restarts, Kilo extension reinitializes, commands are discovered.

---

### Option 2: Restart VS Code Completely

**Step 1: Close VS Code**
```
Windows/Linux: Ctrl + Q
Mac: Cmd + Q
Or use File → Exit
```

**Step 2: Wait 2-3 seconds**
```
Let all processes close completely
```

**Step 3: Reopen VS Code**
```
Click VS Code icon
Or: code /path/to/project
```

**Expected Result**: Fresh start, all extensions reload, commands are discovered.

---

### Option 3: Reload Kilo Extension Specifically

**Step 1: Open Extensions View**
```
Windows/Linux: Ctrl + Shift + X
Mac: Cmd + Shift + X
```

**Step 2: Search for Kilo**
```
Search: "Kilo Code"
```

**Step 3: Reload Extension**
```
Right-click on Kilo Code extension
Select: "Reload"
Or click the reload icon
```

**Expected Result**: Kilo extension restarts, discovers `.kilo/commands/`.

---

## Verification Steps

After reloading, follow these steps to confirm activation:

### Step 1: Check Command Picker

**Open Command Palette**
```
Windows/Linux: Ctrl + P
Mac: Cmd + P
```

**Type forward slash**
```
/
```

**Expected Output**
```
You should see a dropdown with:
├── opsx-explore
├── opsx-propose
├── opsx-apply
├── opsx-archive
├── opsx-update
└── opsx-sync
```

If you see these commands, **activation is successful!** ✅

### Step 2: Test a Command

**In the Command Picker (Ctrl+P), type:**
```
/opsx-explore
```

**Press Enter**

**Expected Result**: Command executes, chat window opens with exploration workflow.

### Step 3: Verify in Chat

**In Chat Interface, type:**
```
/opsx-explore
```

**Press Enter**

**Expected Result**: Slash command triggers automatically without needing to type the full prompt.

---

## Troubleshooting: Commands Still Not Appearing

### Check 1: Verify Files Exist

**Open Terminal in VS Code**
```
Windows/Linux: Ctrl + `
Mac: Cmd + `
```

**Check directory contents**
```bash
ls -la .kilo/commands/
```

**Expected Output**
```
opsx-explore.md
opsx-propose.md
opsx-apply.md
opsx-archive.md
opsx-update.md
opsx-sync.md
```

If files are missing, see "Files Missing" section below.

### Check 2: Clear Kilo Cache

**Step 1: Close VS Code**
```
Ctrl + Shift + P → Developer: Exit
Or close the window
```

**Step 2: Find Kilo Cache Directory**

On Linux:
```bash
rm -rf ~/.cache/kilo/
rm -rf ~/.config/kilo/.cache/
```

On Mac:
```bash
rm -rf ~/Library/Caches/kilo/
rm -rf ~/Library/Preferences/com.kilo.*
```

On Windows:
```
Delete: %APPDATA%\kilo\cache\
Delete: %LOCALAPPDATA%\kilo\cache\
```

**Step 3: Reopen VS Code**

**Step 4: Reload**
```
Ctrl + Shift + P → Developer: Reload Window
```

### Check 3: Verify Kilo Extension is Loaded

**Step 1: Open Extensions**
```
Ctrl + Shift + X
```

**Step 2: Search for Kilo**
```
Type: kilo
```

**Step 3: Verify Status**
```
Look for "Kilo Code" extension
Should show: "Installed" (green)
Should show: "Enabled" (not disabled)
```

If disabled, click "Enable"

### Check 4: Check File Permissions

**In Terminal:**
```bash
cd /home/localadmin/localwork/setupAppCreDepHelmPkg
chmod 644 .kilo/commands/*.md
chmod 755 .kilo/commands/
chmod 755 .kilo/
```

---

## Files Missing: How to Recreate

If the `.kilo/commands/` files are missing, follow these steps:

### Quick Fix: Verify Directory Exists

**In VS Code Terminal:**
```bash
mkdir -p .kilo/commands
```

### Verify Commands Are Created

Run this command to check:
```bash
ls -la .kilo/commands/ | wc -l
```

If output is less than 7 (should be 6 files + header), files are missing.

### Check File Creation

```bash
# Should show 6 files
ls .kilo/commands/

# Should show all with .md extension
ls -1 .kilo/commands/ | grep -c ".md"
# Output should be: 6
```

If files are truly missing, they can be recreated. Let me know and I'll regenerate them.

---

## Advanced: Manual Kilo Configuration

If reload doesn't work, create `.kilo/kilo.jsonc`:

**Step 1: Create config file**
```
File: .kilo/kilo.jsonc
Location: Project root/.kilo/kilo.jsonc
```

**Step 2: Add content**
```json
{
  "$schema": "https://app.kilo.ai/config.json",
  "permission": {
    "read": "allow",
    "edit": "allow",
    "bash": {
      "openspec *": "allow"
    }
  }
}
```

**Step 3: Save file**

**Step 4: Reload VS Code**
```
Ctrl + Shift + P → Developer: Reload Window
```

---

## Complete Reload Sequence (If Stuck)

Use this if nothing else works:

### Step 1: Close Everything
```
Close all open files
Close all VS Code windows
Wait 3 seconds
```

### Step 2: Clear Cache
```bash
# Clear Kilo cache
rm -rf ~/.cache/kilo/ 2>/dev/null
rm -rf ~/.config/kilo/.cache/ 2>/dev/null

# Clear VS Code cache
rm -rf ~/.vscode/ 2>/dev/null
```

### Step 3: Verify Files
```bash
cd /home/localadmin/localwork/setupAppCreDepHelmPkg
ls -la .kilo/commands/
# Should show 6 .md files
```

### Step 4: Reopen VS Code
```
Open VS Code fresh
Open your project folder
Wait for extensions to load (30 seconds)
```

### Step 5: Test Commands
```
Ctrl + P
Type: /
Should see all 6 commands
```

---

## Expected Behavior After Activation

### ✅ Commands Appear in Picker
```
Ctrl + P → Type "/" → See all 6 commands
```

### ✅ Slash Commands Work
```
Type: /opsx-explore
Press: Enter
Result: Command executes
```

### ✅ Auto-Complete Works
```
Type: /opsx-
Auto-complete suggestions appear
```

### ✅ Help Text Shows
```
Hover over command in picker
Description appears below
```

---

## Keyboard Shortcuts for Quick Access

After activation, use these shortcuts:

| Action | Shortcut |
|--------|----------|
| Open Command Picker | Ctrl+P |
| Show All Slash Commands | Ctrl+P then / |
| Quick Reload | Ctrl+Shift+P → Reload |
| Open Chat | Ctrl+L (in Kilo) |
| New Chat Session | Ctrl+Shift+L |

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Commands not showing | Reload window (Ctrl+Shift+P) |
| Commands show but don't work | Check permissions (.kilo.jsonc) |
| Commands disappeared after update | Clear cache, reload |
| Slash commands not recognized | Verify .md files in .kilo/commands/ |
| Only some commands appear | Check file permissions |

---

## Success Checklist

After completing activation steps:

- [ ] VS Code reloaded successfully
- [ ] No error messages in console
- [ ] Command Picker opens with Ctrl+P
- [ ] Typing "/" shows command list
- [ ] At least one command appears in picker
- [ ] Can see all 6 commands:
  - [ ] opsx-explore
  - [ ] opsx-propose
  - [ ] opsx-apply
  - [ ] opsx-archive
  - [ ] opsx-update
  - [ ] opsx-sync
- [ ] Clicking a command executes it
- [ ] Chat opens with command output

---

## Next Steps

Once commands are active:

1. **Test exploration command**
   ```
   /opsx-explore
   ```

2. **Test proposal command**
   ```
   /opsx-propose test feature
   ```

3. **Test apply command**
   ```
   /opsx-apply
   ```

4. **Start using workflows**
   ```
   Use commands in your daily workflow
   ```

---

## Getting Help

If activation still doesn't work:

1. **Check VS Code Console**
   ```
   Ctrl + Shift + P → Toggle Output
   Look for errors related to "kilo" or "commands"
   ```

2. **Check Extension Logs**
   ```
   Ctrl + Shift + X (Extensions)
   Search: Kilo Code
   Click output icon → View Extension Logs
   ```

3. **Verify Network**
   ```
   Check internet connection
   Some extensions load resources from cloud
   ```

4. **Report Issue**
   ```
   GitHub: https://github.com/Kilo-Org/kilocode/issues
   Include: VS Code version, Kilo version, error message
   ```

---

## Summary

**To activate commands:**

1. **Quick Method**: `Ctrl + Shift + P` → `Developer: Reload Window` → Press Enter
2. **Verify**: `Ctrl + P` → Type `/` → See 6 commands
3. **Test**: Type `/opsx-explore` → Commands work!

**If that fails:**
- Restart VS Code completely
- Clear cache directories
- Verify files exist in `.kilo/commands/`
- Check Kilo extension is enabled

**You should see all 6 slash commands within 1-2 minutes after reload.** ✅
