"""
Google Cloud Secret Manager Integration

Provides utility functions to fetch secrets from GCP Secret Manager,
with graceful fallback to environment variables or Streamlit secrets.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def get_secret_from_gcp(secret_id: str, project_id: Optional[str] = None) -> Optional[str]:
    """
    Fetch a secret from Google Cloud Secret Manager.
    
    Args:
        secret_id: The ID of the secret (e.g., "gemini-api-key")
        project_id: GCP project ID (optional, will auto-detect if not provided)
    
    Returns:
        The secret value as a string, or None if not found/accessible
    
    Example:
        >>> api_key = get_secret_from_gcp("gemini-api-key")
        >>> if api_key:
        ...     print("Got API key from Secret Manager")
    """
    try:
        from google.cloud import secretmanager
        
        # Create the Secret Manager client
        client = secretmanager.SecretManagerServiceClient()
        
        # Auto-detect project ID if not provided
        if not project_id:
            # Try to get from environment
            project_id = os.environ.get('GCP_PROJECT') or os.environ.get('GOOGLE_CLOUD_PROJECT')
            
            if not project_id:
                # Try to auto-detect from metadata server (works on GCP)
                try:
                    import requests
                    metadata_server = "http://metadata.google.internal/computeMetadata/v1/"
                    metadata_flavor = {'Metadata-Flavor': 'Google'}
                    response = requests.get(
                        metadata_server + 'project/project-id',
                        headers=metadata_flavor,
                        timeout=2
                    )
                    if response.status_code == 200:
                        project_id = response.text
                except Exception:
                    pass
        
        if not project_id:
            logger.debug("No GCP project ID found, skipping Secret Manager lookup")
            return None
        
        # Build the resource name of the secret version
        # Using "latest" version
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        
        # Access the secret version
        response = client.access_secret_version(request={"name": name})
        
        # Return the secret payload as a string
        secret_value = response.payload.data.decode('UTF-8')
        logger.info(f"Successfully retrieved secret '{secret_id}' from GCP Secret Manager")
        return secret_value
        
    except ImportError:
        logger.debug("google-cloud-secret-manager not installed, skipping GCP Secret Manager")
        return None
    except Exception as e:
        logger.debug(f"Could not fetch secret from GCP Secret Manager: {e}")
        return None


def get_secret(
    secret_id: str,
    streamlit_secrets: Optional[dict] = None,
    env_var: Optional[str] = None,
    project_id: Optional[str] = None
) -> Optional[str]:
    """
    Get a secret with fallback chain: GCP Secret Manager → Streamlit secrets → Environment variable.
    
    Args:
        secret_id: The ID of the secret in GCP Secret Manager
        streamlit_secrets: Streamlit secrets dict (optional)
        env_var: Environment variable name to check (optional)
        project_id: GCP project ID (optional, will auto-detect)
    
    Returns:
        The secret value, or None if not found anywhere
    
    Example:
        >>> import streamlit as st
        >>> api_key = get_secret(
        ...     secret_id="gemini-api-key",
        ...     streamlit_secrets=st.secrets,
        ...     env_var="GEMINI_API_KEY"
        ... )
    """
    # Try GCP Secret Manager first
    secret = get_secret_from_gcp(secret_id, project_id)
    if secret:
        logger.info(f"Using secret from GCP Secret Manager: {secret_id}")
        return secret
    
    # Try Streamlit secrets
    if streamlit_secrets:
        # Handle nested keys like "ai.gemini_api_key"
        if '.' in secret_id:
            parts = secret_id.split('.')
            value = streamlit_secrets
            for part in parts:
                value = value.get(part)
                if value is None:
                    break
            if value:
                logger.info(f"Using secret from Streamlit secrets: {secret_id}")
                return value
        else:
            # Try direct key lookup
            value = streamlit_secrets.get(secret_id.upper()) or streamlit_secrets.get(secret_id)
            if value:
                logger.info(f"Using secret from Streamlit secrets: {secret_id}")
                return value
    
    # Try environment variable
    if env_var:
        value = os.environ.get(env_var)
        if value:
            logger.info(f"Using secret from environment variable: {env_var}")
            return value
    
    logger.debug(f"Secret '{secret_id}' not found in any source")
    return None


if __name__ == "__main__":
    # Test the secret manager
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    test_secret = get_secret(
        secret_id="gemini-api-key",
        env_var="GEMINI_API_KEY"
    )
    
    if test_secret:
        print(f"✓ Successfully retrieved secret (length: {len(test_secret)})")
    else:
        print("✗ No secret found")
