# MLB Statistics Query - Deployment Guide

This guide shows you how to deploy the MLB Statistics web application to Streamlit Cloud (free hosting).

## Option 1: Streamlit Cloud (Recommended - FREE)

### Prerequisites
- GitHub account
- Your code pushed to GitHub

### Steps to Deploy

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Add Streamlit web application"
   git push origin master
   ```

2. **Go to Streamlit Cloud**:
   - Visit https://share.streamlit.io/
   - Click "Sign up" and use your GitHub account
   
3. **Deploy your app**:
   - Click "New app"
   - Select your repository: `jeffbecraft/VibeCoding_BaseballAnalysis`
   - Branch: `master`
   - Main file path: `streamlit_app.py`
   - Click "Deploy"

4. **Share the URL**:
   - Your app will be available at: `https://[your-app-name].streamlit.app`
   - Share this URL with your brother and son!

### Configuration
- The app uses caching to minimize API calls
- Cache files will be stored temporarily on the server
- The app will automatically restart if inactive for a while

## Option 2: Heroku (Also FREE)

### Prerequisites
- Heroku account (free tier available)
- Heroku CLI installed

### Steps to Deploy

1. **Create additional files for Heroku**:
   
   Create `Procfile`:
   ```
   web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
   ```
   
   Create `setup.sh`:
   ```bash
   mkdir -p ~/.streamlit/
   echo "[server]
   headless = true
   port = $PORT
   enableCORS = false
   [theme]
   base = 'light'
   " > ~/.streamlit/config.toml
   ```

2. **Deploy to Heroku**:
   ```bash
   # Login to Heroku
   heroku login
   
   # Create new Heroku app
   heroku create your-mlb-stats-app
   
   # Set buildpack
   heroku buildpacks:set heroku/python
   
   # Deploy
   git push heroku master
   
   # Open the app
   heroku open
   ```

3. **Share the URL**:
   - Your app will be at: `https://your-mlb-stats-app.herokuapp.com`

## Testing Locally

Before deploying, test the Streamlit app locally:

```bash
# Install Streamlit
pip install streamlit

# Run the app
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage Tips for Your Family

Share these tips with your brother and son:

1. **Sample Queries**:
   - "Top 10 home runs in 2024"
   - "What was Aaron Judge's batting average in 2024?"
   - "Rank Shohei Ohtani's home runs"
   - "Yankees ERA leaders"
   - "Which team had the best ERA in 2024?"

2. **Features**:
   - Recent queries appear in the sidebar for quick re-run
   - Results can be downloaded as CSV
   - Cache management to refresh data

3. **Performance**:
   - First query may be slower (fetching from MLB API)
   - Subsequent queries use cached data for speed
   - Cache expires after 24 hours for fresh data

## Updating the Deployment

When you make changes:

**Streamlit Cloud**:
- Just push to GitHub: `git push origin master`
- Streamlit Cloud will auto-deploy the changes

**Heroku**:
```bash
git add .
git commit -m "Update app"
git push heroku master
```

## Monitoring

**Streamlit Cloud**:
- View app analytics in the Streamlit Cloud dashboard
- See number of visitors and usage patterns
- Check logs for any errors

**Heroku**:
```bash
# View logs
heroku logs --tail

# Check app status
heroku ps
```

## Cost

- **Streamlit Cloud**: Completely FREE for public apps
- **Heroku**: FREE tier available (sleeps after 30 min of inactivity)

## Troubleshooting

If the app doesn't work:

1. **Check logs** (Streamlit Cloud dashboard or `heroku logs --tail`)
2. **Verify requirements** are in `requirements_web.txt`
3. **Test locally** first with `streamlit run streamlit_app.py`
4. **Check API limits** - MLB Stats API is free but may have rate limits

## Privacy Note

- The app is publicly accessible (anyone with the URL can use it)
- No authentication is required
- No personal data is collected
- Query history is session-based only (not saved permanently)

## Next Steps

After deployment:
1. Test all query types
2. Share the URL with family
3. Monitor usage in the first few days
4. Gather feedback and improve based on their needs

Enjoy your deployed MLB Stats app! ⚾
