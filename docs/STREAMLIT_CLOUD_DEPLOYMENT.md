# 🚀 Streamlit Cloud Deployment Guide

Complete guide to deploy the MLB Statistics app to **Streamlit Cloud (FREE tier)**.

## ✅ Why Streamlit Cloud?

- ✅ **100% FREE** for public repos
- ✅ **Automatic deploys** from GitHub
- ✅ **HTTPS included** (free SSL)
- ✅ **Serverless** (scales to zero when not in use)
- ✅ **Built-in monitoring** (logs, resource usage)
- ✅ **No credit card required**

## 📋 Prerequisites

- [x] GitHub account (you have this!)
- [x] Repository pushed to GitHub (already done!)
- [x] Streamlit Community Cloud account (we'll create)

## 🎯 Deployment Steps (5 minutes)

### Step 1: Sign up for Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign up"**
3. Choose **"Continue with GitHub"**
4. Authorize Streamlit to access your GitHub repos
5. ✅ **Done!** No credit card needed.

### Step 2: Deploy Your App

1. Click **"New app"** in Streamlit Cloud dashboard
2. Select repository: `jeffbecraft/VibeCoding_BaseballAnalysis`
3. Select branch: `master`
4. Main file path: `streamlit_app.py`
5. Requirements file: `requirements_streamlit.txt` (IMPORTANT - use this one!)
6. Click **"Deploy!"**

### Step 3: Wait for Deployment (2-3 minutes)

Streamlit Cloud will:
- ✅ Clone your repo
- ✅ Create Python environment
- ✅ Install dependencies from `requirements_streamlit.txt`
- ✅ Start your app
- ✅ Assign you a public URL: `https://your-app.streamlit.app`

### Step 4: Test Your App

1. Click the auto-generated URL
2. Test a query: **"Show me Aaron Judge's 2024 stats"**
3. ✅ Should work perfectly!

### Step 5: Optional - Configure Secrets (Advanced)

Only needed if you want:
- OpenAI AI queries (costs money)
- Sentry error monitoring (FREE tier available)

**In Streamlit Cloud dashboard:**
1. Click your app → **"Settings"** → **"Secrets"**
2. Copy contents from `.streamlit/secrets.toml.example`
3. Paste and update with your real values
4. Click **"Save"**

## 🎯 What Works on FREE Tier

### ✅ Full Functionality (No AI)
- All standard queries work perfectly
- Team statistics
- Player statistics
- Season comparisons
- League leaders
- Historical data
- Caching (faster responses)
- Visualizations (Plotly charts)

### ⚠️ AI Queries Not Available (Unless You Pay)
- Ollama (local FREE AI) - **Won't work** (needs local install)
- OpenAI (cloud AI) - **Costs money** (requires API key + payment)

**Recommendation:** Use the FREE tier without AI. The standard queries handle 95% of use cases!

## 📊 Monitoring Your App

### Built-in Streamlit Cloud Features (FREE):

**Logs:**
1. Go to your app in Streamlit Cloud dashboard
2. Click **"Manage app"** → **"Logs"**
3. See real-time application logs
4. Filter by error/warning/info

**Resource Usage:**
- CPU usage
- Memory usage
- Deployment history
- Uptime (automatic restarts)

**Automatic Features:**
- HTTPS (free SSL certificate)
- Auto-sleep after inactivity (saves resources)
- Auto-wake on visit (instant)
- Auto-redeploy on git push

### Optional: Add Sentry Monitoring (FREE tier)

1. Sign up at [sentry.io](https://sentry.io) (FREE tier: 5K errors/month)
2. Create new project → Python → Streamlit
3. Copy your DSN
4. Add to Streamlit Cloud secrets:
   ```toml
   SENTRY_DSN = "https://your_key@sentry.io/project"
   ENVIRONMENT = "production"
   ```
5. Uncomment in `requirements_streamlit.txt`:
   ```
   sentry-sdk>=1.40.0
   ```
6. Redeploy app

## 🔄 Updating Your App

**Automatic updates:**
1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update feature"
   git push
   ```
3. Streamlit Cloud **auto-deploys** within 1-2 minutes!

**Manual redeploy:**
- In Streamlit Cloud dashboard → Click **"Reboot"**

## ⚙️ Configuration

### Environment Variables

Streamlit Cloud uses **Secrets** instead of `.env` files:

**To configure:**
1. App dashboard → **"Settings"** → **"Secrets"**
2. Use TOML format (not .env):
   ```toml
   CACHE_TTL_HOURS = "24"
   LOG_LEVEL = "INFO"
   ENVIRONMENT = "production"
   ```

### Required Files

- ✅ `streamlit_app.py` - Main application (already exists)
- ✅ `requirements_streamlit.txt` - Cloud dependencies (just created)
- ✅ `.streamlit/config.toml` - Streamlit settings (already exists)

### File Structure

```
VibeCoding_BaseballAnalysis/
├── streamlit_app.py          # Main app (entry point)
├── requirements_streamlit.txt # Cloud dependencies (use this!)
├── requirements.txt          # Local dev dependencies (ignore)
├── .streamlit/
│   ├── config.toml          # Streamlit settings
│   └── secrets.toml.example # Secrets template (for reference)
├── src/                     # Source code
├── utils/                   # Utilities
└── data/                    # Cache (created automatically)
```

## 💰 Cost Breakdown

### Streamlit Cloud FREE Tier:

| Feature | Limit |
|---------|-------|
| **Apps** | 1 public app |
| **Resources** | 1 GB RAM, shared CPU |
| **Bandwidth** | Unlimited |
| **Deploys** | Unlimited |
| **SSL** | Included |
| **Uptime** | 99%+ (with auto-sleep) |
| **Cost** | **$0.00** |

**Paid tiers:** ($20/mo for private repos, more resources)

### Optional Add-ons:

| Service | FREE Tier | Cost |
|---------|-----------|------|
| **Sentry** | 5K errors/mo | $0 (FREE tier) |
| **OpenAI** | No free tier | ~$0.02-0.06/query |

**Total minimum cost:** **$0.00** (fully FREE!)

## 🔧 Troubleshooting

### App won't start

**Check logs:**
1. Dashboard → "Manage app" → "Logs"
2. Look for error messages

**Common issues:**
- ❌ Wrong requirements file (use `requirements_streamlit.txt`)
- ❌ Missing dependencies (check `requirements_streamlit.txt`)
- ❌ Python version mismatch (app uses 3.11)

**Fix:**
1. Update `requirements_streamlit.txt`
2. Push to GitHub
3. Auto-redeploys in 1-2 minutes

### App is slow

**Normal behavior:**
- First visit after sleep: 10-30 seconds (cold start)
- Subsequent visits: Instant (warm)
- Queries with cache: < 1 second
- Queries without cache: 2-5 seconds

**Speed up:**
- Cache is automatically enabled (24-hour TTL)
- Increase cache TTL in secrets:
  ```toml
  CACHE_TTL_HOURS = "168"  # 1 week
  ```

### AI queries not working

**Expected behavior:**
- Ollama: **Won't work** (local only)
- OpenAI: **Costs money** (requires API key)

**Solution:**
- Use standard queries (work perfectly!)
- Or pay for OpenAI ($0.02-0.06/query)

### App randomly restarts

**Normal behavior:**
- Streamlit Cloud auto-restarts inactive apps
- Scales to zero after ~15 minutes of inactivity
- Wakes up instantly on next visit

**This is GOOD:**
- Saves resources
- Reduces costs
- No impact on user experience

## 📈 Best Practices

### Performance:

1. **Use caching** (already enabled)
   - 24-hour TTL by default
   - Speeds up repeat queries
   
2. **Monitor resource usage**
   - Check dashboard regularly
   - 1 GB RAM limit on FREE tier
   
3. **Optimize queries**
   - Standard queries are faster than AI
   - Cache hit rate shown in app

### Security:

1. **Never commit secrets**
   - Use Streamlit Cloud secrets manager
   - Add `.env` to `.gitignore` (already done)
   
2. **Keep dependencies updated**
   - Check for security updates monthly
   - Update `requirements_streamlit.txt`

3. **Enable Sentry** (optional)
   - Track production errors
   - FREE tier: 5K errors/month

### Monitoring:

1. **Check logs weekly**
   - Look for errors
   - Track usage patterns
   
2. **Add Sentry** (recommended)
   - Real user error tracking
   - Performance monitoring
   - FREE tier available

3. **Share status updates**
   - Use Streamlit Cloud URL
   - Share with users/stakeholders

## 🎉 Success Checklist

After deployment, verify:

- [ ] App URL loads: `https://your-app.streamlit.app`
- [ ] Query works: "Show me Aaron Judge's 2024 stats"
- [ ] Cache is enabled (check sidebar)
- [ ] Logs show no errors
- [ ] Auto-deploy works (push a small change)
- [ ] Optional: Sentry tracking enabled
- [ ] Share URL with team/users

## 📚 Additional Resources

- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Forums](https://discuss.streamlit.io)
- [Sentry Setup](https://docs.sentry.io/platforms/python/guides/streamlit/)
- [Your GitHub Repo](https://github.com/jeffbecraft/VibeCoding_BaseballAnalysis)

## 🆘 Need Help?

**Streamlit Cloud Support:**
- [Community Forum](https://discuss.streamlit.io)
- [Documentation](https://docs.streamlit.io)
- Email: support@streamlit.io

**App-Specific Issues:**
- Check logs in Streamlit Cloud dashboard
- Review GitHub issues
- Check Sentry dashboard (if enabled)

---

**Ready to deploy?** Follow Step 1 above! 🚀

Your app will be live at: `https://your-username-app-name.streamlit.app`
