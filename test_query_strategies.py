#!/usr/bin/env python3
"""
Test different query strategies to get more results
"""

from enhanced_google_maps_scraper import enhanced_scrape_google_maps as scrape_google_maps

def test_query_strategies():
    """Test queries that should return more results"""
    
    print("🧪 Testing different query strategies for more results...")
    
    # These queries should return many more results
    test_cases = [
        # Broader, simpler queries
        {"query": "restaurants New York", "max_results": 25},
        {"query": "coffee shops Chicago", "max_results": 20}, 
        {"query": "hotels Miami", "max_results": 15},
        {"query": "pizza NYC", "max_results": 20},
        {"query": "food Manhattan", "max_results": 30},
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"🔍 TEST {i}: '{test['query']}'")
        print(f"🎯 Target: {test['max_results']} results")
        print(f"{'='*50}")
        
        try:
            results = scrape_google_maps(
                test['query'], 
                max_results=test['max_results'],
                visit_websites=False
            )
            
            success_rate = len(results) / test['max_results'] * 100
            
            print(f"\n📊 RESULTS:")
            print(f"Found: {len(results)} businesses")
            print(f"Target: {test['max_results']}")
            print(f"Success rate: {success_rate:.1f}%")
            
            # Analyze results
            if len(results) >= test['max_results'] * 0.8:  # 80%+ success
                print("✅ EXCELLENT - Great result count!")
            elif len(results) >= test['max_results'] * 0.5:  # 50%+ success
                print("✅ GOOD - Decent result count")
            elif len(results) >= 10:
                print("⚠️ MODERATE - Some results but below target")
            else:
                print("❌ POOR - Still very limited results")
            
            # Show phone extraction success
            phone_count = sum(1 for b in results if b.get('mobile'))
            phone_rate = phone_count / len(results) * 100 if results else 0
            print(f"📞 Phone numbers: {phone_count}/{len(results)} ({phone_rate:.1f}%)")
            
        except Exception as e:
            print(f"❌ TEST {i} FAILED: {e}")
    
    print(f"\n{'='*50}")
    print("💡 RECOMMENDATIONS:")
    print("• Use broader terms: 'restaurants' vs 'pizza restaurants'")
    print("• Avoid 'in [city]' - use just 'city name'") 
    print("• Try generic categories: 'food', 'shopping', 'hotels'")
    print("• Test different cities/regions")
    print("• Consider that some areas genuinely have fewer businesses")

if __name__ == "__main__":
    test_query_strategies()
