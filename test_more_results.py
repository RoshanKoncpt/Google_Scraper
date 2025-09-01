#!/usr/bin/env python3
"""
Test script to verify improved result extraction gets more businesses
"""

from enhanced_google_maps_scraper import enhanced_scrape_google_maps as scrape_google_maps

def test_more_results():
    """Test the improved scraper to get more results"""
    print("🧪 Testing improved Google Maps scraper for more results...")
    
    # Test with different max_results values
    test_cases = [
        {"query": "restaurants in Chicago", "max_results": 10},
        {"query": "coffee shops in Seattle", "max_results": 15},
        {"query": "hotels in Miami", "max_results": 20}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"🔍 TEST {i}: {test_case['query']}")
        print(f"🎯 Target: {test_case['max_results']} results")
        print(f"{'='*60}")
        
        try:
            results = scrape_google_maps(
                test_case['query'], 
                max_results=test_case['max_results'], 
                visit_websites=False
            )
            
            print(f"\n📊 RESULTS FOR TEST {i}:")
            print(f"✅ Total businesses found: {len(results)}")
            print(f"🎯 Target was: {test_case['max_results']}")
            print(f"📈 Success rate: {len(results)}/{test_case['max_results']} ({len(results)/test_case['max_results']*100:.1f}%)")
            
            # Count businesses with phone numbers
            phone_count = sum(1 for business in results if business.get('mobile'))
            print(f"📞 Businesses with phone numbers: {phone_count}/{len(results)} ({phone_count/len(results)*100:.1f}%)")
            
            # Show sample results
            print(f"\n📝 Sample results:")
            for j, business in enumerate(results[:3], 1):
                print(f"  {j}. {business['name']}")
                print(f"     📍 {business['address'][:50]}...")
                print(f"     📞 {business['mobile'] or 'No phone'}")
                print(f"     ⭐ {business['rating'] or 'No rating'}")
            
            if len(results) >= test_case['max_results'] * 0.7:  # 70% success rate
                print(f"✅ TEST {i} PASSED - Good result count!")
            else:
                print(f"⚠️ TEST {i} NEEDS IMPROVEMENT - Low result count")
                
        except Exception as e:
            print(f"❌ TEST {i} FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("🏁 All tests completed!")
    print("If you're still getting limited results, try:")
    print("1. Using more specific search queries")
    print("2. Different geographic locations")
    print("3. Adjusting max_results parameter")
    print("4. Running during different times of day")

if __name__ == "__main__":
    test_more_results()
