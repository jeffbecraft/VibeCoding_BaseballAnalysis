# 📊 Uptime Monitoring Setup Guide

Simple guide to set up FREE uptime monitoring for your MLB Statistics application.

## Why Uptime Monitoring?

- Get alerts when your app goes down
- Track uptime percentage (99.9% goal)
- Response time tracking
- FREE tier available for most services

---

## Option 1: UptimeRobot (Recommended - FREE)

**Best for:** Simple, free, easy setup

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

- [ ] Sign up for UptimeRobot (or preferred service)
- [ ] Add monitor for your app URL
- [ ] Add health endpoint: `/_stcore/health`
- [ ] Configure email alerts
- [ ] Test by triggering alert (stop app temporarily)
- [ ] Verify alert received
- [ ] Set up weekly reports
- [ ] Share status page with team (optional)

---

## Next Steps

1. ✅ **Complete this setup** (5 minutes)
2. 📊 **Review weekly reports** to track uptime
3. 🔍 **Investigate any downtime** immediately
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
