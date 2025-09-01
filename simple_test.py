#!/usr/bin/env python3
"""
Simple test to identify the root cause of limited results
"""

from enhanced_google_maps_scraper import enhanced_scrape_google_maps as scrape_google_maps

def simple_test():
    """Run a simple test with detailed output"""
    print("🧪 Simple test to diagnose limited results issue...")
    
    # Test with a very specific, high-density search
    query = "pizza restaurants in Manhattan New York"
    max_results = 15
    
    print(f"🔍 Query: {query}")
    print(f"🎯 Target: {max_results} results")
    print("=" * 50)
    
    try:
        results = scrape_google_maps(query, max_results=max_results, visit_websites=False)
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"Found: {len(results)} businesses")
        print(f"Target: {max_results} businesses")
        print(f"Success rate: {len(results)/max_results*100:.1f}%")
        
        if len(results) < 10:
            print(f"\n❌ ISSUE CONFIRMED: Only {len(results)} results found")
            print("This suggests one of these problems:")
            print("1. Google Maps is rate limiting/blocking")
            print("2. Scrolling mechanism isn't working properly")
            print("3. Link selectors are outdated")
            print("4. Geographic search returns limited results")
            
            print(f"\n🔍 Analyzing the {len(results)} results we did get:")
            for i, business in enumerate(results, 1):
                print(f"{i}. {business['name']}")
                print(f"   📍 {business['address'][:60]}...")
                print(f"   📞 {business['mobile'] or 'No phone'}")
        else:
            print(f"✅ Good results! Found {len(results)} businesses")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()
