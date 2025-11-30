"""
Player Image Module

Provides functionality to display MLB player headshot images.
MLB.com uses Cloudinary for image hosting with predictable URL patterns.
"""

from typing import Optional
import logging

# Initialize logger
logger = logging.getLogger(__name__)


def get_player_headshot_url(player_id: int, size: str = "small") -> str:
    """
    Generate MLB player headshot image URL.
    
    MLB uses Cloudinary CDN with a predictable URL pattern for player headshots.
    These images are publicly accessible and don't require authentication.
    
    Args:
        player_id: MLB player ID (e.g., 592450 for Aaron Judge)
        size: Image size - 'small' (70px), 'medium' (120px), or 'large' (213px)
    
    Returns:
        URL to player headshot image
    
    Example:
        >>> url = get_player_headshot_url(592450)  # Aaron Judge
        >>> # Returns: https://img.mlbstatic.com/mlb-photos/.../592450/headshot/67/current
    
    Notes:
        - Images are automatically updated by MLB
        - Generic placeholder shown if player photo unavailable
        - CDN cached for fast loading
        - Free to use (no API key needed)
    """
    # Size configuration
    sizes = {
        'small': 'w_70',    # 70px width (thumbnail)
        'medium': 'w_120',  # 120px width (default)
        'large': 'w_213'    # 213px width (high-res)
    }
    
    width = sizes.get(size, sizes['small'])
    
    # MLB Cloudinary URL pattern
    # - d_people:generic:headshot:67:current.png = default/placeholder image if player photo missing
    # - q_auto:best = automatic quality optimization
    # - v1 = version 1 of the transformation
    # - people/{player_id} = unique player identifier
    # - headshot/67/current = current headshot at aspect ratio 67 (2:3)
    base_url = "https://img.mlbstatic.com/mlb-photos/image/upload"
    default_image = "d_people:generic:headshot:67:current.png"
    transformation = f"{width},q_auto:best"
    path = f"v1/people/{player_id}/headshot/67/current"
    
    url = f"{base_url}/{default_image}/{transformation}/{path}"
    
    logger.debug(f"Generated headshot URL for player {player_id}: {url}")
    
    return url


def get_player_action_shot_url(player_id: int, size: str = "small") -> str:
    """
    Generate MLB player action shot image URL.
    
    Similar to headshots but returns action/hero images.
    
    Args:
        player_id: MLB player ID
        size: Image size - 'small', 'medium', or 'large'
    
    Returns:
        URL to player action shot image
    
    Notes:
        - Not all players have action shots
        - Falls back to generic placeholder if unavailable
    """
    sizes = {
        'small': 'w_120',
        'medium': 'w_213',
        'large': 'w_426'
    }
    
    width = sizes.get(size, sizes['small'])
    
    base_url = "https://img.mlbstatic.com/mlb-photos/image/upload"
    default_image = "d_people:generic:action:current.png"
    transformation = f"{width},q_auto:best"
    path = f"v1/people/{player_id}/action/current"
    
    url = f"{base_url}/{default_image}/{transformation}/{path}"
    
    logger.debug(f"Generated action shot URL for player {player_id}: {url}")
    
    return url


def display_player_card_streamlit(player_data: dict, size: str = "medium", 
                                   show_action_shot: bool = False) -> None:
    """
    Display player headshot with basic info in Streamlit.
    
    Args:
        player_data: Player dictionary from MLBDataFetcher (must have 'id' and 'fullName')
        size: Image size - 'small', 'medium', or 'large'
        show_action_shot: If True, show action shot instead of headshot
    
    Example:
        >>> from src.data_fetcher import MLBDataFetcher
        >>> from src.player_images import display_player_card_streamlit
        >>> 
        >>> fetcher = MLBDataFetcher()
        >>> players = fetcher.search_players("Aaron Judge")
        >>> if players:
        ...     display_player_card_streamlit(players[0])
    
    Raises:
        ImportError: If streamlit is not installed
        ValueError: If player_data missing required fields
    """
    try:
        import streamlit as st
    except ImportError:
        raise ImportError("Streamlit must be installed to use this function")
    
    # Validate player data
    if not player_data or 'id' not in player_data:
        raise ValueError("player_data must contain 'id' field")
    
    player_id = player_data['id']
    player_name = player_data.get('fullName', 'Unknown Player')
    
    # Get appropriate image URL
    if show_action_shot:
        image_url = get_player_action_shot_url(player_id, size)
    else:
        image_url = get_player_headshot_url(player_id, size)
    
    # Display in Streamlit
    st.image(image_url, caption=player_name, use_container_width=False)
    
    # Optionally show additional player info
    if 'primaryPosition' in player_data:
        position = player_data['primaryPosition'].get('abbreviation', '')
        st.caption(f"Position: {position}")
    
    if 'currentTeam' in player_data:
        team_id = player_data['currentTeam'].get('id')
        # Could add team name lookup here if needed
        st.caption(f"Team ID: {team_id}")
    
    logger.info(f"Displayed player card for {player_name} (ID: {player_id})")


def get_team_logo_url(team_id: int, style: str = "light") -> str:
    """
    Generate MLB team logo image URL.
    
    Args:
        team_id: MLB team ID (e.g., 147 for Yankees)
        style: 'light' (for dark backgrounds) or 'dark' (for light backgrounds)
    
    Returns:
        URL to team logo SVG image
    
    Example:
        >>> url = get_team_logo_url(147)  # Yankees logo
    """
    # MLB team logos are SVG files on their CDN
    # Style: 'light' = white/light version, 'dark' = dark version
    base_url = "https://www.mlbstatic.com/team-logos/team-cap-on-{style}"
    
    if style not in ['light', 'dark']:
        style = 'light'
    
    url = f"https://www.mlbstatic.com/team-logos/team-cap-on-{style}/{team_id}.svg"
    
    logger.debug(f"Generated team logo URL for team {team_id}: {url}")
    
    return url


# Additional utility: Check if image URL is accessible
def is_image_accessible(url: str, timeout: int = 3) -> bool:
    """
    Check if an image URL is accessible (returns 200 OK).
    
    Args:
        url: Image URL to check
        timeout: Request timeout in seconds
    
    Returns:
        True if image is accessible, False otherwise
    
    Example:
        >>> url = get_player_headshot_url(592450)
        >>> if is_image_accessible(url):
        ...     print("Image available!")
    """
    try:
        import requests
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code == 200
    except Exception as e:
        logger.warning(f"Failed to check image accessibility: {e}")
        return False


if __name__ == "__main__":
    # Example usage and testing
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Test URL generation
    player_id = 592450  # Aaron Judge
    
    print("Player Headshot URLs:")
    print(f"  Small:  {get_player_headshot_url(player_id, 'small')}")
    print(f"  Medium: {get_player_headshot_url(player_id, 'medium')}")
    print(f"  Large:  {get_player_headshot_url(player_id, 'large')}")
    
    print("\nPlayer Action Shot:")
    print(f"  {get_player_action_shot_url(player_id)}")
    
    print("\nTeam Logo:")
    team_id = 147  # Yankees
    print(f"  {get_team_logo_url(team_id)}")
    
    # Test accessibility
    headshot_url = get_player_headshot_url(player_id)
    print(f"\nTesting image accessibility...")
    if is_image_accessible(headshot_url):
        print(f"✓ Image is accessible!")
    else:
        print(f"✗ Image not accessible")
