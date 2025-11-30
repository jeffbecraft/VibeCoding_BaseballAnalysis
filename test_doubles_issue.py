"""
Test to verify doubles data for Aaron Judge vs Gunnar Henderson in 2024.
"""
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from src.data_fetcher import MLBDataFetcher
from src.data_processor import MLBDataProcessor

def main():
    """Check doubles for both players in 2024."""
    print("\n" + "="*70)
    print("Investigating Doubles Data Issue (2024)")
    print("="*70)
    
    fetcher = MLBDataFetcher()
    processor = MLBDataProcessor()
    
    # Get doubles leaders for 2024
    print("\n1. Getting doubles leaders for 2024...")
    leaders_data = fetcher.get_stats_leaders('doubles', 2024, 100, 'hitting', include_all=True)
    
    if not leaders_data:
        print("❌ No leaders data returned")
        return False
    
    leaders_df = processor.extract_stats_leaders(leaders_data)
    
    print(f"✓ Retrieved {len(leaders_df)} players")
    
    # Find both players
    print("\n2. Finding Aaron Judge and Gunnar Henderson...")
    judge_row = leaders_df[leaders_df['playerName'].str.contains('Judge', case=False, na=False)]
    henderson_row = leaders_df[leaders_df['playerName'].str.contains('Henderson', case=False, na=False)]
    
    if judge_row.empty:
        print("❌ Aaron Judge not found in doubles leaders")
    else:
        judge_data = judge_row.iloc[0]
        print(f"\n✓ Aaron Judge:")
        print(f"  Rank: #{judge_data['rank']}")
        print(f"  Doubles: {judge_data['value']}")
        print(f"  Player ID: {judge_data.get('playerId', 'N/A')}")
    
    if henderson_row.empty:
        print("❌ Gunnar Henderson not found in doubles leaders")
    else:
        henderson_data = henderson_row.iloc[0]
        print(f"\n✓ Gunnar Henderson:")
        print(f"  Rank: #{henderson_data['rank']}")
        print(f"  Doubles: {henderson_data['value']}")
        print(f"  Player ID: {henderson_data.get('playerId', 'N/A')}")
    
    # Compare
    if not judge_row.empty and not henderson_row.empty:
        judge_doubles = judge_data['value']
        henderson_doubles = henderson_data['value']
        
        print("\n" + "="*70)
        print("COMPARISON RESULT:")
        print("="*70)
        
        if judge_doubles > henderson_doubles:
            print(f"✓ Aaron Judge had MORE doubles: {judge_doubles} > {henderson_doubles}")
            print(f"  Judge was ranked #{judge_data['rank']}")
            print(f"  Henderson was ranked #{henderson_data['rank']}")
            print(f"\n⚠️  The application returned INCORRECT information!")
        elif henderson_doubles > judge_doubles:
            print(f"✓ Gunnar Henderson had MORE doubles: {henderson_doubles} > {judge_doubles}")
            print(f"  Henderson was ranked #{henderson_data['rank']}")
            print(f"  Judge was ranked #{judge_data['rank']}")
            print(f"\n✓ The application returned CORRECT information")
        else:
            print(f"= They had the SAME number of doubles: {judge_doubles}")
    
    # Show top 10 for context
    print("\n" + "="*70)
    print("Top 10 Doubles Leaders (2024):")
    print("="*70)
    top10 = leaders_df.head(10)
    for idx, row in top10.iterrows():
        marker = "  ← Judge" if 'Judge' in row['playerName'] else ("  ← Henderson" if 'Henderson' in row['playerName'] else "")
        print(f"  #{row['rank']:2}: {row['playerName']:30} {row['value']} doubles{marker}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
