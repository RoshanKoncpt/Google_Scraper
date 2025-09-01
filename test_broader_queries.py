#!/usr/bin/env python3
"""
Test with broader search queries to get more results
"""

from enhanced_google_maps_scraper import enhanced_scrape_google_maps as scrape_google_maps

def test_broader_queries():
    """Test different search query strategies"""
    
    test_queries = [
        # Broader queries that should return more results
        {"query": "restaurants in New York", "expected": "20+"},
        {"query": "coffee shops in Chicago", "expected": "15+"},
        {"query": "hotels in Miami", "expected": "15+"},
        {"query": "pizza New York", "expected": "10+"},  # Simpler query
        {"query": "restaurants Manhattan", "expected": "15+"},  # No "in"
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"🔍 TEST {i}: {test['query']}")
        print(f"🎯 Expected: {test['expected']} results")
        print(f"{'='*60}")
        
        try:
            results = scrape_google_maps(
                test['query'], 
                max_results=20,  # Reasonable target
                visit_websites=False
            )
            
            print(f"\n📊 RESULTS:")
            print(f"Found: {len(results)} businesses")
            print(f"Expected: {test['expected']}")
            
            if len(results) >= 10:
                print(f"✅ SUCCESS - Good result count!")
            elif len(results) >= 5:
                print(f"⚠️ MODERATE - Decent results but could be better")
            else:
                print(f"❌ POOR - Still limited results")
            
            # Show sample results
            print(f"\nSample businesses:")
            for j, business in enumerate(results[:3], 1):
                print(f"  {j}. {business['name']}")
                print(f"     📞 {business['mobile'] or 'No phone'}")
            
        except Exception as e:
            print(f"❌ TEST {i} FAILED: {e}")
    
    print(f"\n{'='*60}")
    print("🎯 RECOMMENDATIONS:")
    print("If broader queries still return few results:")
    print("1. Google Maps may be limiting automated access")
    print("2. Try different geographic locations")
    print("3. Use more generic terms (avoid 'pizza restaurants')")
    print("4. Test during different times of day")

if __name__ == "__main__":
    test_broader_queries()
