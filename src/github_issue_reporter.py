"""
GitHub Issue Reporter
Automatically create GitHub issues from user feedback in the Streamlit app.
"""

import os
import requests
from typing import Dict, Optional
from logger import get_logger

logger = get_logger(__name__)


class GitHubIssueReporter:
    """
    Reports issues to GitHub repository automatically.
    """
    
    def __init__(self):
        """Initialize GitHub issue reporter."""
        self.token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = os.getenv('GITHUB_REPO_OWNER', 'jeffbecraft')
        self.repo_name = os.getenv('GITHUB_REPO_NAME', 'VibeCoding_BaseballAnalysis')
        self.api_url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues'
        self.enabled = bool(self.token)
        
        if self.enabled:
            logger.info(f"GitHub issue reporting enabled for {self.repo_owner}/{self.repo_name}")
        else:
            logger.info("GitHub issue reporting disabled (no token configured)")
    
    def is_available(self) -> bool:
        """
        Check if GitHub issue reporting is available.
        
        Returns:
            True if GitHub token is configured
        """
        return self.enabled
    
    def create_issue(
        self,
        title: str,
        description: str,
        issue_type: str = 'bug',
        user_info: Optional[Dict] = None,
        query_context: Optional[str] = None,
        error_details: Optional[str] = None
    ) -> Dict:
        """
        Create a GitHub issue from user feedback.
        
        Args:
            title: Issue title
            description: Detailed description from user
            issue_type: Type of issue ('bug', 'feature', 'question', 'feedback')
            user_info: Optional user information (email, name, etc.)
            query_context: The query that caused the issue (if applicable)
            error_details: Error message/traceback (if applicable)
            
        Returns:
            Dict with 'success' and 'message' or 'url' keys
        """
        if not self.enabled:
            return {
                'success': False,
                'message': 'GitHub issue reporting not configured'
            }
        
        try:
            # Build issue body
            body_parts = [description]
            
            # Add context sections
            if query_context:
                body_parts.append(f"\n\n### Query Context\n```\n{query_context}\n```")
            
            if error_details:
                body_parts.append(f"\n\n### Error Details\n```\n{error_details}\n```")
            
            # Add user info if provided
            if user_info:
                user_section = "\n\n### Reporter Information\n"
                if user_info.get('email'):
                    user_section += f"- Email: {user_info['email']}\n"
                if user_info.get('name'):
                    user_section += f"- Name: {user_info['name']}\n"
                body_parts.append(user_section)
            
            # Add metadata
            body_parts.append("\n\n---\n*Reported via Streamlit Cloud application*")
            
            body = "\n".join(body_parts)
            
            # Determine labels based on issue type
            labels = [issue_type]
            if issue_type == 'bug':
                labels.append('user-reported')
            elif issue_type == 'feature':
                labels.append('enhancement')
            
            # Create issue via GitHub API
            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            data = {
                'title': title,
                'body': body,
                'labels': labels
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 201:
                issue_data = response.json()
                logger.info(f"Created GitHub issue #{issue_data['number']}: {title}")
                return {
                    'success': True,
                    'message': f"Issue created successfully (#{issue_data['number']})",
                    'url': issue_data['html_url'],
                    'issue_number': issue_data['number']
                }
            else:
                error_msg = f"GitHub API error: {response.status_code}"
                logger.error(f"{error_msg} - {response.text}")
                return {
                    'success': False,
                    'message': error_msg
                }
                
        except requests.exceptions.Timeout:
            logger.error("GitHub API timeout")
            return {
                'success': False,
                'message': 'Request timeout - please try again'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed: {e}")
            return {
                'success': False,
                'message': 'Network error - please try again later'
            }
        except Exception as e:
            logger.error(f"Unexpected error creating GitHub issue: {e}")
            return {
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            }
    
    def create_bug_report(
        self,
        description: str,
        query: Optional[str] = None,
        error: Optional[str] = None,
        user_email: Optional[str] = None
    ) -> Dict:
        """
        Convenience method for creating bug reports.
        
        Args:
            description: What went wrong
            query: The query that caused the bug
            error: Error message
            user_email: Reporter's email for follow-up
            
        Returns:
            Result from create_issue()
        """
        title = f"Bug Report: {description[:50]}..."
        
        user_info = {'email': user_email} if user_email else None
        
        return self.create_issue(
            title=title,
            description=description,
            issue_type='bug',
            user_info=user_info,
            query_context=query,
            error_details=error
        )
    
    def create_feature_request(
        self,
        title: str,
        description: str,
        user_email: Optional[str] = None
    ) -> Dict:
        """
        Convenience method for feature requests.
        
        Args:
            title: Feature title
            description: Feature description
            user_email: Reporter's email
            
        Returns:
            Result from create_issue()
        """
        user_info = {'email': user_email} if user_email else None
        
        return self.create_issue(
            title=f"Feature Request: {title}",
            description=description,
            issue_type='feature',
            user_info=user_info
        )
    
    def create_general_feedback(
        self,
        feedback: str,
        user_email: Optional[str] = None
    ) -> Dict:
        """
        Convenience method for general feedback.
        
        Args:
            feedback: User's feedback
            user_email: Reporter's email
            
        Returns:
            Result from create_issue()
        """
        title = f"User Feedback: {feedback[:50]}..."
        
        user_info = {'email': user_email} if user_email else None
        
        return self.create_issue(
            title=title,
            description=feedback,
            issue_type='feedback',
            user_info=user_info
        )
