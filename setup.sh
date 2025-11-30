mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"your-email@example.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
[theme]\n\
primaryColor = \"#1f77b4\"\n\
backgroundColor = \"#ffffff\"\n\
secondaryBackgroundColor = \"#f0f2f6\"\n\
textColor = \"#262730\"\n\
" > ~/.streamlit/config.toml
