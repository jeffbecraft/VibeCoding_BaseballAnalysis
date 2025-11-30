# 📊 Uptime Monitoring Setup Guide

Simple guide to set up FREE uptime monitoring for your MLB Statistics application.

## ⚠️ IMPORTANT: Serverless Considerations

**If deploying to serverless platforms** (Streamlit Cloud, AWS Lambda, Cloud Run, Vercel):
- Apps **scale to zero** when not in use to save resources
- Traditional uptime monitoring **wakes up the app** constantly
- This defeats serverless benefits (cost savings, efficiency)

### Recommended Approaches for Serverless:

1. ✅ **User-Triggered Monitoring Only**
   - Monitor actual user traffic (via Sentry, CloudWatch)
   - Get alerts on **real user errors**, not synthetic checks
   - Let app sleep when unused

2. ✅ **Selective Health Checks**
   - Only ping during **business hours** (when users expected)
   - Use longer intervals (30-60 minutes instead of 5)
   - Accept that app may be "down" (sleeping) outside hours

3. ✅ **Real User Monitoring (RUM)**
   - Track actual user experience
   - No synthetic pings
   - See `src/monitoring.py` for Sentry RUM

4. ⚠️ **Traditional Uptime Monitoring** (See below)
   - Use ONLY for always-on deployments
   - NOT recommended for serverless
   - Will increase costs and prevent scaling to zero

---

## Choose Your Deployment Type

### Serverless Deployments
**Platforms:** Streamlit Cloud, AWS Lambda, Cloud Run, Vercel, Netlify Functions

✅ **Recommended:** Real User Monitoring (Sentry)  
⚠️ **NOT Recommended:** Traditional uptime pings

**Skip to:** [Serverless Monitoring Strategy](#serverless-monitoring-strategy)

### Always-On Deployments
**Platforms:** EC2, ECS, VPS, Dedicated Servers, Docker on VM

✅ **Recommended:** Traditional uptime monitoring  
✅ **Also Use:** Real User Monitoring (Sentry)

**Continue to:** Traditional monitoring options below

---

## Serverless Monitoring Strategy

### Best Practices for Serverless:

#### 1. **Use Sentry for Real User Monitoring** ✅ RECOMMENDED

Already integrated in `streamlit_app.py`!

```bash
# 1. Install Sentry SDK
pip install sentry-sdk

# 2. Sign up at sentry.io (FREE tier)
# 3. Add to .env:
SENTRY_DSN=https://your_key@sentry.io/project

# 4. Run setup wizard:
python setup_production_env.py
```

**What You Get:**
- ✅ Real user error tracking
- ✅ Performance monitoring
- ✅ No synthetic pings (app sleeps normally)
- ✅ Alerts on actual issues
- ✅ User session tracking

**Sentry tracks:**
- Errors when users actually visit
- Performance during real usage
- Query execution times
- Cache hit rates
- NO false alerts from sleeping app

#### 2. **Platform-Native Monitoring**

**Streamlit Cloud:**
```
Built-in monitoring dashboard:
- View logs in Streamlit Cloud UI
- Track deployments
- No extra setup needed
- Free with your deployment
```

**AWS Lambda/App Runner:**
```bash
# CloudWatch automatically tracks:
- Invocation count
- Errors
- Duration
- Throttles

# View in AWS Console:
CloudWatch → Logs → /aws/lambda/your-function
```

**Google Cloud Run:**
```bash
# Cloud Logging tracks:
- Request count
- Latency
- Error rate
- CPU/Memory usage

# View in GCP Console:
Cloud Run → Your Service → Logs
```

#### 3. **Conditional Health Checks** (Advanced)

If you MUST use uptime monitoring with serverless:

```yaml
# UptimeRobot Configuration for Serverless

Monitor Type: HTTP(s)
URL: https://your-app/_stcore/health
Interval: 60 minutes  # NOT 5 minutes!
Monitor Only: Business hours (9 AM - 6 PM Mon-Fri)
Expected Downtime: 
  - Nights: 6 PM - 9 AM
  - Weekends: All day
```

**Limitations:**
- App won't truly scale to zero (woken hourly)
- Increased costs (compute time)
- Defeats serverless benefits

---

## Why Uptime Monitoring?

- Get alerts when your app goes down
- Track uptime percentage (99.9% goal)
- Response time tracking
- FREE tier available for most services

**⚠️ For Always-On Deployments Only**

---

## Option 1: UptimeRobot (For Always-On Deployments)

**Best for:** Traditional hosting, VPS, EC2, dedicated servers  
**⚠️ NOT for:** Serverless platforms (use Sentry instead)

### Setup Steps (5 minutes):

1. **Sign up for FREE account:**
   - Go to: https://uptimerobot.com
   - Click "Register for FREE"
   - Verify email

2. **Add Monitor:**
   - Click "+ Add New Monitor"
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** MLB Stats Production
   - **URL:** Your app URL + `/_stcore/health`
     - Streamlit Cloud: `https://your-app.streamlit.app/_stcore/health`
     - Custom domain: `https://mlbstats.yourdomain.com/_stcore/health`
   - **Monitoring Interval:** 5 minutes (FREE tier)
   - Click "Create Monitor"

3. **Add Alert Contacts:**
   - Go to "My Settings" → "Alert Contacts"
   - Add your email
   - Optionally add:
     - SMS (requires phone number)
     - Slack webhook
     - Discord webhook

4. **Configure Alerts:**
   - Email when monitor goes down
   - Email when monitor comes back up
   - Optional: Weekly uptime summary

### Monitor Settings:

```
Monitor Type: HTTP(s)
URL: https://your-app.streamlit.app/_stcore/health
Interval: 5 minutes
Timeout: 30 seconds
Expected Status: 200

Alert When:
  ✅ Monitor is down
  ✅ Monitor is back up
  ⬜ SSL certificate expires (if using HTTPS)
```

### What You Get (FREE):

- ✅ 50 monitors
- ✅ 5-minute check intervals
- ✅ Email + SMS alerts
- ✅ Uptime percentage tracking
- ✅ Response time graphs
- ✅ Public status pages

---

## Option 2: Pingdom (Professional)

**Best for:** Detailed analytics, multiple locations

### Setup Steps:

1. **Sign up:**
   - Go to: https://www.pingdom.com
   - Start free trial (14 days)
   - After trial: $10-15/month

2. **Create Uptime Check:**
   - Add New → Uptime Check
   - URL: `https://your-app/_stcore/health`
   - Check interval: 1 minute
   - Check from multiple locations

3. **Benefits:**
   - More detailed metrics
   - Multiple geographic locations
   - Advanced alerting
   - Real-user monitoring

---

## Option 3: AWS CloudWatch (If Using AWS)

**Best for:** AWS deployments, integrated monitoring

### Setup Steps:

1. **Create CloudWatch Synthetics Canary:**

```bash
# Create canary script
cat > canary.py <<EOF
def handler(event, context):
    import requests
    response = requests.get('https://your-app/_stcore/health', timeout=10)
    assert response.status_code == 200
    return {'statusCode': 200}
EOF

# Create canary via CLI
aws synthetics create-canary \
  --name mlb-stats-health-check \
  --runtime-version syn-python-selenium-1.0 \
  --schedule Expression="rate(5 minutes)"
```

2. **Set up SNS alerts:**
   - Create SNS topic
   - Add email subscription
   - Configure CloudWatch alarm

### What You Get:

- Integrated with AWS services
- Custom health checks
- Detailed metrics in CloudWatch
- Cost: ~$0.001 per check

---

## Option 4: Better Uptime (Modern UI)

**Best for:** Team monitoring, modern interface

### Setup:

1. Sign up: https://betteruptime.com
2. Add monitor with URL: `https://your-app/_stcore/health`
3. Configure on-call schedules

### Free Tier:

- 10 monitors
- 3-minute intervals
- Unlimited team members
- Beautiful status pages

---

## Option 5: Healthchecks.io (Developer-Friendly)

**Best for:** Developers, simple cron monitoring

### Setup:

1. Sign up: https://healthchecks.io
2. Create check
3. Ping URL from your app
4. Get alerts if pings stop

---

## What to Monitor

### Required:

- ✅ **Main App URL:** `https://your-app.streamlit.app`
  - Should return 200 OK
  - Check every 5 minutes

- ✅ **Health Endpoint:** `https://your-app.streamlit.app/_stcore/health`
  - Streamlit's built-in health check
  - Should return 200 OK
  - Faster than loading full page

### Optional:

- 📊 Response time tracking
- 🌍 Multi-location checks
- 📱 SSL certificate expiry
- 💾 Cache status (custom endpoint)

---

## Alert Configuration

### Recommended Settings:

**Down Alert:**
- Trigger after: 2 failed checks (reduces false positives)
- Alert via: Email + SMS
- Retry interval: 1 minute

**Up Alert:**
- Trigger after: 1 successful check
- Alert via: Email only

**Weekly Report:**
- Send every: Monday 9 AM
- Include: Uptime %, response times, incidents

---

## Custom Health Endpoint (Advanced)

Add to `streamlit_app.py` for more detailed health checks:

```python
# Add health check endpoint with detailed status
def health_check():
    """Custom health check with detailed status"""
    try:
        # Test cache
        cache_ok = st.session_state.fetcher.cache is not None
        
        # Test AI
        ai_ok = st.session_state.ai_handler.is_available()
        
        # Overall status
        status = "healthy" if (cache_ok and ai_ok) else "degraded"
        
        return {
            'status': status,
            'cache': 'ok' if cache_ok else 'error',
            'ai': 'ok' if ai_ok else 'error',
            'version': __version__
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }
```

---

## Response Time Targets

### Good Performance:

- ✅ < 200ms: Excellent
- ✅ < 500ms: Good
- ⚠️ < 1s: Acceptable
- ❌ > 1s: Needs investigation

### If Response Time Is Slow:

1. Check cache hit rate
2. Review API call frequency
3. Optimize database queries
4. Consider CDN for static assets
5. Increase server resources

---

## Setting Up Status Page (Optional)

### UptimeRobot Status Page:

1. Go to "My Settings" → "Status Pages"
2. Click "Add Status Page"
3. Select monitors to display
4. Customize branding
5. Get public URL: `https://stats.uptimerobot.com/your-id`

### Example Status Page Content:

```markdown
# MLB Statistics App Status

Current Status: ✅ All Systems Operational

## Monitored Services:
- Web Application
- API Endpoints
- Cache System
- AI Query Service

Last Updated: [Auto-updated]
Uptime (30 days): 99.9%
```

---

## Troubleshooting

### Monitor Shows "Down" But App Works:

1. Check timeout settings (increase to 30s)
2. Verify health endpoint URL
3. Check SSL certificate validity
4. Review firewall rules

### Too Many False Alerts:

1. Increase "Down after X failed checks" to 2-3
2. Increase timeout from 10s → 30s
3. Check from multiple locations

### Slow Response Time:

1. Clear cache: Force refresh in browser
2. Check database performance
3. Review API call logs
4. Monitor server CPU/memory

---

## Quick Start Checklist

### For Serverless (Streamlit Cloud, Lambda, Cloud Run):

- [ ] ✅ **Use Sentry** (Real User Monitoring)
  - [ ] Install: `pip install sentry-sdk`
  - [ ] Run: `python setup_production_env.py`
  - [ ] Add Sentry DSN to `.env`
  - [ ] Deploy and verify errors captured
- [ ] ✅ **Check Platform Logs**
  - [ ] Streamlit Cloud: View logs in dashboard
  - [ ] AWS: CloudWatch logs
  - [ ] GCP: Cloud Logging
## Next Steps

### For Serverless:

1. ✅ **Install Sentry** (5 minutes)
   ```bash
   pip install sentry-sdk
   python setup_production_env.py
   ```

2. 📊 **Monitor real user errors** in Sentry dashboard
3. 🔍 **Check platform logs** for deployment issues
4. 📈 **Track performance** via Sentry RUM
5. 😴 **Let app sleep** when not in use (cost savings!)

### For Always-On:

1. ✅ **Set up UptimeRobot** (5 minutes)
2. ✅ **Add Sentry** for error tracking
3. 📊 **Review weekly uptime reports**
4. 🔍 **Investigate any downtime** immediately
5. 📈 **Track response times** for performance
6. 🎯 **Aim for 99.9% uptime** (< 45 min downtime/month)

--- ] Add health endpoint: `/_stcore/health`
- [ ] Configure email alerts (5-minute interval OK)
- [ ] Test by triggering alert (stop app temporarily)
- [ ] Verify alert received
## Cost Summary

| Service | Free Tier | Paid Plans | Best For |
|---------|-----------|------------|----------|
| **Sentry** | 5K errors/mo | $26/mo | **Serverless** (Recommended) |
| **Platform Logs** | Included | Included | **Serverless** (Built-in) |
| **UptimeRobot** | 50 monitors, 5min | $7/mo | **Always-On** |
| **Pingdom** | 14-day trial | $10/mo | **Always-On** |
| **Better Uptime** | 10 monitors, 3min | $25/mo | **Always-On** |
| **Healthchecks.io** | 20 checks | $5/mo | **Always-On** |
| **AWS CloudWatch** | Limited free tier | ~$0.10/mo | **AWS Lambda** |

**Serverless Recommendation:** Sentry FREE tier + Platform logs  
**Always-On Recommendation:** UptimeRobot FREE + Sentry
4. 📈 **Track response times** for performance
5. 🎯 **Aim for 99.9% uptime** (< 45 min downtime/month)

---

## Cost Summary

| Service | Free Tier | Paid Plans |
|---------|-----------|------------|
| **UptimeRobot** | 50 monitors, 5min interval | $7/mo (1min interval) |
| **Pingdom** | 14-day trial | $10/mo |
| **Better Uptime** | 10 monitors, 3min interval | $25/mo |
| **Healthchecks.io** | 20 checks | $5/mo |
| **AWS CloudWatch** | Limited free tier | ~$0.10/mo |

**Recommendation:** Start with UptimeRobot FREE tier - it's perfect for most use cases!

---

**Questions?** See `docs/PRODUCTION_DEPLOYMENT.md` for more monitoring options.
