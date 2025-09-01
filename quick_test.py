#!/usr/bin/env python3
"""
Quick test of enhanced Google Maps scraper to verify lead count
"""

from enhanced_google_maps_scraper import enhanced_scrape_google_maps
import json
from datetime import datetime

def quick_test():
    """Test enhanced scraper with a simple query"""
    
    query = "restaurants in New York"
    max_results = 30
    
    print(f"🧪 QUICK TEST - Enhanced Google Maps Scraper")
    print(f"🔍 Query: {query}")
    print(f"🎯 Target: {max_results} results")
    print("=" * 60)
    
    try:
        results = enhanced_scrape_google_maps(query, max_results=max_results, visit_websites=False)
        
        # Analyze results
        total_found = len(results)
        contacts_found = sum(1 for r in results if r.get('mobile') or r.get('email'))
        phones_found = sum(1 for r in results if r.get('mobile'))
        emails_found = sum(1 for r in results if r.get('email'))
        websites_found = sum(1 for r in results if r.get('website'))
        
        print(f"\n📊 RESULTS")
        print("=" * 40)
        print(f"✅ Total businesses: {total_found}")
        print(f"📞 With phone: {phones_found}")
        print(f"📧 With email: {emails_found}")
        print(f"🌐 With website: {websites_found}")
        print(f"📋 Total contacts: {contacts_found}")
        
        # Success check
        if total_found >= 20:
            print(f"\n🎉 SUCCESS! Found {total_found} leads (target: 20+)")
        else:
            print(f"\n⚠️ NEEDS IMPROVEMENT! Only found {total_found} leads (target: 20+)")
        
        # Show first 5 results
        print(f"\n📝 Sample Results:")
        for i, result in enumerate(results[:5], 1):
            print(f"{i}. {result['name']}")
            if result.get('mobile'):
                print(f"   📞 {result['mobile']}")
            if result.get('address'):
                print(f"   📍 {result['address'][:50]}...")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quick_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        return results
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return []

if __name__ == "__main__":
    quick_test()
