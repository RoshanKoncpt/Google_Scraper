#!/usr/bin/env python3
"""
Test current enhanced scraper performance
"""

from enhanced_google_maps_scraper import enhanced_scrape_google_maps
import json
from datetime import datetime

def test_performance():
    query = "restaurants in New York"
    max_results = 30
    
    print(f"🧪 Testing Enhanced Scraper Performance")
    print(f"🔍 Query: {query}")
    print(f"🎯 Target: {max_results} results")
    print("=" * 50)
    
    try:
        results = enhanced_scrape_google_maps(query, max_results=max_results, visit_websites=False)
        
        total_found = len(results)
        contacts_found = sum(1 for r in results if r.get('mobile') or r.get('email'))
        phones_found = sum(1 for r in results if r.get('mobile'))
        
        print(f"\n📊 RESULTS:")
        print(f"✅ Total businesses: {total_found}")
        print(f"📞 With phone: {phones_found}")
        print(f"📋 Total contacts: {contacts_found}")
        
        if total_found >= 20:
            print(f"\n🎉 SUCCESS! Found {total_found} leads (target: 20+)")
        else:
            print(f"\n⚠️ NEEDS IMPROVEMENT! Only {total_found} leads (target: 20+)")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_test_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        return results
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return []

if __name__ == "__main__":
    test_performance()
