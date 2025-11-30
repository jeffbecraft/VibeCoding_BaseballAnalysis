"""
Production Environment Configuration Helper

Creates a production-ready .env file from the template.
Prompts for required settings and validates configuration.
"""

import os
import sys
from pathlib import Path

def create_production_env():
    """Create production .env file with guided setup."""
    
    print("⚙️  Production Environment Configuration\n")
    print("=" * 60)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        response = input("\n⚠️  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled. Keeping existing .env file.")
            return
    
    # Check for .env.example
    if not os.path.exists('.env.example'):
        print("❌ .env.example not found!")
        return
    
    print("\n📝 Setting up production environment variables...\n")
    
    # Read template
    with open('.env.example', 'r') as f:
        template = f.read()
    
    # Start with template
    env_content = template
    
    # Ask key questions
    print("\n1️⃣  Environment Configuration")
    print("-" * 60)
    
    environment = input("Environment (development/staging/production) [production]: ").strip()
    if not environment:
        environment = "production"
    env_content = env_content.replace('ENVIRONMENT=development', f'ENVIRONMENT={environment}')
    
    log_level = input("Log Level (DEBUG/INFO/WARNING/ERROR) [WARNING]: ").strip().upper()
    if not log_level:
        log_level = "WARNING"
    env_content = env_content.replace('LOG_LEVEL=INFO', f'LOG_LEVEL={log_level}')
    
    print("\n2️⃣  Error Monitoring (Optional - Recommended for Production)")
    print("-" * 60)
    print("📊 Sentry provides error tracking and performance monitoring")
    print("   Sign up FREE at: https://sentry.io\n")
    
    sentry_dsn = input("Sentry DSN (leave blank to skip): ").strip()
    if sentry_dsn:
        env_content = env_content.replace(
            '# SENTRY_DSN=https://your_sentry_dsn@sentry.io/project_id',
            f'SENTRY_DSN={sentry_dsn}'
        )
        print("✅ Sentry monitoring will be enabled")
    else:
        print("⚠️  Monitoring disabled (you can add later)")
    
    print("\n3️⃣  AI Configuration")
    print("-" * 60)
    
    ai_provider = input("AI Provider (auto/ollama/openai) [auto]: ").strip()
    if ai_provider and ai_provider != 'auto':
        env_content = env_content.replace('AI_PROVIDER=auto', f'AI_PROVIDER={ai_provider}')
    
    if ai_provider == 'openai':
        print("\n⚠️  OpenAI requires an API key (costs money)")
        print("   Get your key from: https://platform.openai.com/api-keys\n")
        openai_key = input("OpenAI API Key: ").strip()
        if openai_key:
            env_content = env_content.replace(
                'OPENAI_API_KEY=your_openai_api_key_here',
                f'OPENAI_API_KEY={openai_key}'
            )
    
    print("\n4️⃣  Cache Configuration")
    print("-" * 60)
    
    cache_hours = input("Cache TTL in hours (24-168 recommended for prod) [168]: ").strip()
    if cache_hours:
        env_content = env_content.replace('CACHE_TTL_HOURS=24', f'CACHE_TTL_HOURS={cache_hours}')
    
    # Write .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n" + "=" * 60)
    print("✅ Production .env file created successfully!")
    print("\n📁 Location: .env")
    print("🔒 This file is in .gitignore (not committed to git)")
    
    print("\n📋 Your Configuration:")
    print(f"   Environment: {environment}")
    print(f"   Log Level: {log_level}")
    print(f"   Monitoring: {'Enabled' if sentry_dsn else 'Disabled'}")
    print(f"   AI Provider: {ai_provider if ai_provider else 'auto'}")
    print(f"   Cache TTL: {cache_hours if cache_hours else '24'} hours")
    
    print("\n🚀 Next Steps:")
    print("   1. Review .env file and adjust if needed")
    print("   2. Test locally: python -m streamlit run streamlit_app.py")
    print("   3. Test Docker: docker-compose up -d")
    print("   4. Deploy to production (see docs/PRODUCTION_DEPLOYMENT.md)")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    try:
        create_production_env()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
