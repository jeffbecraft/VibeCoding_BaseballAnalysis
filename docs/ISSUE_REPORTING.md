# 🐛 Issue Reporting Setup Guide

This guide explains how users can report issues directly from your Streamlit app, with **automatic GitHub issue creation**.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [For Users - How to Report Issues](#for-users---how-to-report-issues)
3. [For Developers - Setup Instructions](#for-developers---setup-instructions)
4. [Configuration Options](#configuration-options)
5. [Security Best Practices](#security-best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Overview

### What This Does

Users can report issues directly from the Streamlit app sidebar, and **issues are automatically created** in your GitHub repository!

**Benefits:**
- ✅ **Zero friction** - Users don't need GitHub accounts
- ✅ **Automatic tracking** - All issues logged in GitHub Issues
- ✅ **Contextual information** - Captures query context, errors, user email
- ✅ **Organized** - Auto-labels (bug, feature, feedback)
- ✅ **Optional** - Works with or without configuration

### Issue Types Supported

1. **🐛 Bug Reports** - Something broken or incorrect
2. **💡 Feature Requests** - New features or improvements
3. **💬 General Feedback** - Questions, comments, suggestions

---

## For Users - How to Report Issues

### Step 1: Open the Feedback Form

1. Look in the **sidebar** (left side of the app)
2. Scroll down to **"💬 Report an Issue"**
3. Click **"📝 Submit Feedback"** to expand the form

### Step 2: Choose Issue Type

Select from:
- **Bug Report** - Something isn't working
- **Feature Request** - Suggest a new feature
- **General Feedback** - Any other comments

### Step 3: Fill Out the Form

**For Bug Reports:**
```
What went wrong?
└─> Describe the issue (required)

Query (if applicable):
└─> The question you asked that caused the bug

Your email (optional):
└─> For follow-up if we need more info
```

**For Feature Requests:**
```
Feature title:
└─> Brief name for the feature

Description:
└─> Detailed explanation of what you want

Your email (optional):
└─> For updates on your request
```

**For General Feedback:**
```
Your feedback:
└─> Tell us what you think!

Your email (optional):
└─> If you want a response
```

### Step 4: Submit

Click the **Submit** button. You'll see:
- ✅ **Success message** with issue number
- 🔗 **Direct link** to view the issue on GitHub

### Example Bug Report

```
Type: Bug Report

What went wrong?
"I asked 'Top 10 home runs' but got ERA leaders instead"

Query: Top 10 home runs in 2024

Your email: user@example.com
```

**Result:** GitHub issue created automatically!
```
Issue #42: Bug Report: I asked 'Top 10 home runs' but got...

Labels: bug, user-reported
```

---

## For Developers - Setup Instructions

### Option 1: Enable Automatic GitHub Issues (Recommended)

#### Prerequisites
- GitHub account with repo access
- GitHub Personal Access Token

#### Step 1: Create GitHub Token

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. **Name:** `Streamlit App Issue Reporter`
4. **Expiration:** 90 days (or longer)
5. **Scopes:** Select:
   - ✅ `public_repo` (if your repo is public)
   - ✅ `repo` (if your repo is private)
6. Click **"Generate token"**
7. **Copy the token** (you won't see it again!)

#### Step 2: Configure Streamlit Cloud Secrets

**For Streamlit Cloud:**

1. Go to your app dashboard: https://share.streamlit.io
2. Click your app → **Settings** → **Secrets**
3. Add:
   ```toml
   # GitHub Issue Reporting
   GITHUB_TOKEN = "ghp_your_actual_token_here"
   GITHUB_REPO_OWNER = "your-github-username"
   GITHUB_REPO_NAME = "VibeCoding_BaseballAnalysis"
   ```
4. Click **Save**
5. App will restart automatically

**For Local Development:**

Create `.env` file (already in `.gitignore`):
```bash
# GitHub Issue Reporting
GITHUB_TOKEN=ghp_your_actual_token_here
GITHUB_REPO_OWNER=your-github-username
GITHUB_REPO_NAME=VibeCoding_BaseballAnalysis
```

#### Step 3: Test It!

1. Run your app
2. Go to sidebar → **"💬 Report an Issue"**
3. Submit a test bug report
4. Check your GitHub repo → **Issues** tab
5. You should see the new issue! 🎉

### Option 2: Manual Issue Reporting (Fallback)

If GitHub token is **not configured**, users will see:

```
📧 To report issues, please:
- Email: jeffbecraft@gmail.com
- GitHub: Create an issue manually
```

This ensures users always have a way to report issues, even without automation.

---

## Configuration Options

### Environment Variables

| Variable | Required? | Default | Description |
|----------|-----------|---------|-------------|
| `GITHUB_TOKEN` | Optional | None | GitHub Personal Access Token |
| `GITHUB_REPO_OWNER` | Optional | `jeffbecraft` | Your GitHub username |
| `GITHUB_REPO_NAME` | Optional | `VibeCoding_BaseballAnalysis` | Your repo name |

### Customization

**Change Repository:**
```toml
GITHUB_REPO_OWNER = "your-username"
GITHUB_REPO_NAME = "your-repo-name"
```

**Change Fallback Email:**

Edit `streamlit_app.py`:
```python
st.info("""
📧 To report issues, please:
- Email: your.email@example.com
- GitHub: [Create an issue](https://github.com/...)
""")
```

---

## Security Best Practices

### ✅ DO

- ✅ Use **GitHub Personal Access Token** (not password)
- ✅ Set **minimal scopes** (`public_repo` only)
- ✅ Set token **expiration** (90 days recommended)
- ✅ Store token in **Streamlit Secrets** (never commit to git)
- ✅ Rotate tokens regularly

### ❌ DON'T

- ❌ Commit tokens to git
- ❌ Share tokens publicly
- ❌ Use tokens with admin/delete permissions
- ❌ Store tokens in code files

### Token Rotation

When token expires:
1. Generate new token (same steps)
2. Update Streamlit Cloud Secrets
3. App restarts automatically

---

## What Information Gets Collected?

### Bug Reports
```yaml
Title: "Bug Report: [User's description]"
Body:
  - User's description
  - Query that caused the issue (if provided)
  - Error details (if available)
  - User email (if provided)
Labels: ["bug", "user-reported"]
```

### Feature Requests
```yaml
Title: "Feature Request: [User's title]"
Body:
  - User's description
  - User email (if provided)
Labels: ["feature", "enhancement"]
```

### General Feedback
```yaml
Title: "User Feedback: [First 50 chars]"
Body:
  - User's feedback
  - User email (if provided)
Labels: ["feedback"]
```

### Privacy

- ✅ **Email is optional** - Users can remain anonymous
- ✅ **No tracking** - Only what user explicitly submits
- ✅ **Public issues** - All issues visible on GitHub (public repo)
- ❌ **Not for sensitive data** - Don't submit passwords, etc.

---

## Troubleshooting

### Issue Not Created

**Problem:** User submits feedback but no GitHub issue appears

**Solutions:**

1. **Check token validity:**
   ```bash
   curl -H "Authorization: token YOUR_TOKEN" \
        https://api.github.com/user
   ```
   Should return your GitHub user info.

2. **Check token permissions:**
   - Go to: https://github.com/settings/tokens
   - Verify `repo` or `public_repo` scope is checked

3. **Check repository name:**
   - Verify `GITHUB_REPO_OWNER` and `GITHUB_REPO_NAME` are correct
   - Case-sensitive!

4. **Check app logs:**
   - Streamlit Cloud: Dashboard → Logs
   - Look for "GitHub issue reporting enabled" message

### Form Not Showing

**Problem:** Sidebar doesn't show feedback form

**Solutions:**

1. **Update app:**
   ```bash
   git pull
   ```

2. **Check imports:**
   ```python
   from github_issue_reporter import GitHubIssueReporter
   ```
   Should be in `streamlit_app.py`

3. **Restart app:**
   - Streamlit Cloud: Auto-restarts on push
   - Local: Stop and restart

### API Rate Limits

**Problem:** GitHub API rate limit exceeded

**GitHub Limits:**
- Authenticated: 5,000 requests/hour
- Unauthenticated: 60 requests/hour

**This app uses:** ~1 request per issue submitted

**Solution:** Very unlikely to hit limits unless thousands of users submit issues simultaneously.

---

## Advanced Usage

### Programmatic Issue Creation

```python
from github_issue_reporter import GitHubIssueReporter

# Initialize
reporter = GitHubIssueReporter()

# Create bug report
result = reporter.create_bug_report(
    description="Query returned wrong results",
    query="Top 10 home runs 2024",
    error="IndexError: list index out of range",
    user_email="user@example.com"
)

if result['success']:
    print(f"Issue created: {result['url']}")
    print(f"Issue number: {result['issue_number']}")
```

### Custom Issue Creation

```python
result = reporter.create_issue(
    title="Custom Issue Title",
    description="Detailed description",
    issue_type='bug',  # 'bug', 'feature', 'question', 'feedback'
    user_info={'email': 'user@example.com', 'name': 'John Doe'},
    query_context="User's query here",
    error_details="Error traceback here"
)
```

---

## Monitoring Issues

### GitHub Notifications

**Email Notifications:**
1. Go to: https://github.com/settings/notifications
2. Enable **"Email"** for:
   - ✅ Issues
   - ✅ Pull requests
   - ✅ Comments

**Watch Your Repo:**
1. Go to your repository
2. Click **Watch** (top right)
3. Select **"All Activity"**

### Issue Management

**Triage New Issues:**
```
New user-reported issue arrives:
1. Review description
2. Add additional labels if needed
3. Assign to team member
4. Respond to user (if email provided)
5. Close when resolved
```

**Auto-Labels Applied:**
- `bug` - Bug reports
- `user-reported` - All user-submitted bugs
- `feature` - Feature requests
- `enhancement` - Also added to feature requests
- `feedback` - General feedback

---

## Cost Analysis

### FREE Tier (Recommended)

**GitHub Personal Account:**
- ✅ Unlimited public repos
- ✅ Unlimited issues
- ✅ 5,000 API calls/hour
- ✅ No cost

**Total Cost:** $0.00/month

### GitHub Pro (Optional)

If you need:
- Private repositories
- Advanced features
- Priority support

**Cost:** $4/month

---

## Quick Start Checklist

For new deployments:

- [ ] Create GitHub Personal Access Token
- [ ] Add token to Streamlit Cloud Secrets
- [ ] Configure `GITHUB_REPO_OWNER` and `GITHUB_REPO_NAME`
- [ ] Test feedback form (submit test issue)
- [ ] Verify issue appears in GitHub
- [ ] Enable GitHub notifications
- [ ] Document your custom contact email (if different)
- [ ] Share app with users! 🎉

---

## Example User Workflow

**Scenario:** User finds a bug

1. **User Action:**
   - Opens sidebar
   - Clicks "Report an Issue"
   - Selects "Bug Report"
   - Describes: "Top 10 query returned wrong year"
   - Enters query: "Top 10 home runs"
   - Optionally provides email
   - Clicks "Submit Bug Report"

2. **System Response:**
   - Creates GitHub issue #123
   - Shows success: "✅ Issue created successfully (#123)"
   - Provides link: "View issue"

3. **Developer Action:**
   - Receives GitHub notification
   - Reviews issue #123
   - Fixes bug
   - Closes issue with comment
   - User gets email (if they subscribed to issue)

**Result:** 🎉 Bug tracked, fixed, and user notified!

---

## Support

**Setup Help:**
- GitHub Token Guide: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- Streamlit Secrets: https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management

**Issues with This Feature:**
- Open an issue: https://github.com/jeffbecraft/VibeCoding_BaseballAnalysis/issues
- Email: jeffbecraft.professional@gmail.com

---

**Users can now report issues with one click! 🚀**
