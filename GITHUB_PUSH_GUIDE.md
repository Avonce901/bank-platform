# GitHub Push Guide for Bank Platform

## Overview
Your bank_platform project is ready to push to GitHub. Since the GitHub CLI (`gh`) isn't installed, follow these manual steps.

## Prerequisites
- Git installed (you have this ✓)
- GitHub account
- SSH key or Personal Access Token (PAT)

## Option 1: Using HTTPS (Easiest)

### Step 1: Create Repository on GitHub
1. Go to https://github.com/new
2. Repository name: `bank-platform`
3. Description: `Banking simulation platform with API, PDF extraction, Excel generation`
4. Choose: **Public** (or Private)
5. Click **Create repository**

### Step 2: Add Remote and Push
```powershell
cd $env:USERPROFILE\bank_platform

# Add remote
git remote add origin https://github.com/YOUR-USERNAME/bank-platform.git

# Rename branch to main if needed
git branch -M main

# Push to GitHub
git push -u origin main
```

When prompted, enter your GitHub credentials:
- Username: your GitHub username
- Password: Your Personal Access Token (PAT) - NOT your password

### Getting a Personal Access Token (PAT)
1. Go to https://github.com/settings/tokens
2. Click **Generate new token** → **Generate new token (classic)**
3. Set these scopes:
   - `repo` (full control of private repositories)
   - `workflow` (if using GitHub Actions)
4. Copy the token and use it as your password when pushing

---

## Option 2: Using SSH (More Secure)

### Step 1: Generate SSH Key (if you don't have one)
```powershell
ssh-keygen -t ed25519 -C "your_email@example.com"
# Press Enter for all prompts to use defaults
```

### Step 2: Add SSH Key to GitHub
1. Copy your public key:
   ```powershell
   cat $env:USERPROFILE\.ssh\id_ed25519.pub | Set-Clipboard
   ```
2. Go to https://github.com/settings/keys
3. Click **New SSH key**
4. Paste your key and click **Add SSH key**

### Step 3: Create Repository on GitHub
1. Go to https://github.com/new
2. Repository name: `bank-platform`
3. Choose: **Public** (or Private)
4. Click **Create repository**

### Step 4: Push with SSH
```powershell
cd $env:USERPROFILE\bank_platform

# Add SSH remote
git remote add origin git@github.com:YOUR-USERNAME/bank-platform.git

# Rename branch to main if needed
git branch -M main

# Push to GitHub
git push -u origin main
```

---

## Quick Commands Reference

```powershell
# Check current remotes
git remote -v

# Remove existing remote (if needed)
git remote remove origin

# Add new remote (HTTPS)
git remote add origin https://github.com/YOUR-USERNAME/bank-platform.git

# Add new remote (SSH)
git remote add origin git@github.com:YOUR-USERNAME/bank-platform.git

# Push to GitHub
git push -u origin main

# Check status
git status

# View commits
git log --oneline
```

---

## Current Repository Status

**Last Commits:**
- `26605ce` - Add: test suite, Streamlit admin panel, data initialization, and documentation
- `98783a8` - Initial commit: banking simulation platform

**Files Ready to Push:**
- `admin_panel.py` - Streamlit admin dashboard
- `init_data.py` - Data initialization script
- `tests/` - Comprehensive test suite
- `data/` - Sample data (accounts, ledger, users)
- `src/` - API and module source code
- `.env.example` - Environment template
- `docker-compose.yml` - Docker configuration
- `requirements.txt` - Python dependencies

---

## Troubleshooting

### "fatal: remote origin already exists"
```powershell
git remote remove origin
# Then add the correct remote URL
```

### "Permission denied (publickey)"
- Ensure SSH key is added to GitHub
- Or use HTTPS instead of SSH

### "Authentication failed"
- Check your GitHub username
- Use Personal Access Token (not password) for HTTPS

### "branch master -> refs/heads/master [new branch]"
- This means your branch will be renamed to `main` on GitHub
- This is normal and expected

---

## After Push

Once successfully pushed, your repository will be at:
```
https://github.com/YOUR-USERNAME/bank-platform
```

You can then:
1. Add collaborators
2. Enable GitHub Actions for CI/CD
3. Set up Branch protection rules
4. Create pull request templates
5. Add GitHub Pages documentation

---

## Complete Push Workflow Example

```powershell
cd "$env:USERPROFILE\bank_platform"

# Verify everything is committed
git status

# Should output: "nothing to commit, working tree clean"

# Add remote (replace YOUR-USERNAME)
git remote add origin https://github.com/YOUR-USERNAME/bank-platform.git

# Push to GitHub
git push -u origin main

# Verify success
git branch -vv
# Should show: main ... origin/main [ahead 0]
```

---

**Need Help?**
- GitHub Docs: https://docs.github.com/en
- SSH Setup: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
- PAT Guide: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
