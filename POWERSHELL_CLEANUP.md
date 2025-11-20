# POWERSHELL PROFILE CLEANUP GUIDE

## Overview
If you see errors when opening PowerShell related to your profile, follow these steps to clean it up.

## Step 1: Locate Your Profile
Your PowerShell profile is stored at:
```
$PROFILE
```

On Windows, this is typically:
```
C:\Users\<YourUsername>\Documents\PowerShell\profile.ps1
```

## Step 2: Open the Profile File
Run this command in PowerShell:
```powershell
notepad $PROFILE
```

Or using VS Code:
```powershell
code $PROFILE
```

## Step 3: Clean Up the Profile

### Option A: Remove Problematic Lines
Look for lines that might be causing errors:
- Import statements for missing modules
- Uncommented initialization code
- Paths that no longer exist

Common issues:
```powershell
# Remove or comment out problematic imports
# Import-Module SomeModule  # Comment this if module doesn't exist

# Remove old aliases
# Remove-Item alias:xxx
```

### Option B: Create a Fresh Profile
If your profile is too cluttered, replace everything with:
```powershell
# Clean PowerShell Profile
# Add your customizations here

# Example: Set location
Set-Location $env:USERPROFILE

# Example: Set alias
Set-Alias -Name ll -Value Get-ChildItem

# Example: Function
function prompt {
    "PS $($executionContext.sessionState.path.currentLocation)> "
}
```

## Step 4: Save and Test

1. Save the file (Ctrl+S in Notepad)
2. Close and reopen PowerShell
3. If errors persist, check the error messages for specific lines
4. Comment out those lines and try again

## Step 5: (Optional) Disable Profile Completely

If you want to disable your profile entirely:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Remove-Item $PROFILE -Force
```

Then restart PowerShell.

## Troubleshooting

### Error: "Cannot find path" 
- The profile file doesn't exist yet. You can create it:
```powershell
New-Item -Path $PROFILE -ItemType File -Force
```

### Error: "ExecutionPolicy" 
- Set the execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error: "Module not found"
- Comment out the import statement:
```powershell
# Import-Module NonExistentModule
```

## Best Practices

1. Keep your profile minimal for better startup performance
2. Comment out unused code instead of deleting it
3. Test changes incrementally
4. Use version control (git) to track profile changes
5. Back up your profile before making major changes

## For This Project

If you're using the bank_platform project, you can add this to your profile:
```powershell
# Bank Platform Shortcuts
function bank-setup {
    Set-Location "$env:USERPROFILE\bank_platform"
}

function bank-api {
    Set-Location "$env:USERPROFILE\bank_platform"
    .\venv\Scripts\Activate.ps1
    python -m src.api.main
}

function bank-admin {
    Set-Location "$env:USERPROFILE\bank_platform"
    .\venv\Scripts\Activate.ps1
    streamlit run admin_panel.py
}
```

Then you can just run:
```powershell
bank-setup      # Go to project
bank-api        # Start API
bank-admin      # Start admin panel
```

---
**Note**: Changes to your PowerShell profile take effect when you open a new PowerShell window.
