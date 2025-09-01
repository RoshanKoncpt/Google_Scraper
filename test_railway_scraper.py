#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from railway_optimized_scraper import RailwayOptimizedScraper

def test_railway_scraper():
    """Test the Railway-optimized scraper locally"""
    print("🧪 Testing Railway-optimized scraper locally...")
    print("=" * 60)
    
    try:
        # Test with a simple query
        scraper = RailwayOptimizedScraper(
            search_query="coffee shops in San Francisco", 
            max_results=5,
            visit_websites=False
        )
        
        print("✅ Scraper initialized")
        
        # Run extraction
        results = scraper.run_extraction()
        
        print(f"\n🎯 FINAL RESULTS:")
        print(f"📊 Total businesses found: {len(results)}")
        
        if results:
            print(f"✅ SUCCESS: Found {len(results)} businesses")
            for i, business in enumerate(results[:3], 1):
                print(f"  {i}. {business.get('name', 'Unknown')}")
                print(f"     Address: {business.get('address', 'N/A')}")
                print(f"     Phone: {business.get('mobile', 'N/A')}")
                print()
        else:
            print("❌ FAILED: No businesses found")
            print("This indicates Google Maps is blocking access")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_railway_scraper()
    
    if success:
        print("🎉 Railway scraper appears to work locally")
        print("💡 It should work on Railway too")
    else:
        print("⚠️ Railway scraper failed locally")
        print("💡 Google Maps blocking is the issue")
        print("💡 Consider alternative approaches:")
        print("   - Use residential proxies")
        print("   - Try different cloud providers")
        print("   - Use Google Places API instead")
