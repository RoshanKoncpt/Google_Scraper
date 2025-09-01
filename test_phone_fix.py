#!/usr/bin/env python3
"""
Test script to verify phone number extraction fixes
"""

from enhanced_google_maps_scraper import enhanced_scrape_google_maps as scrape_google_maps

def test_phone_extraction():
    """Test the updated phone extraction with a simple search"""
    print("🧪 Testing updated phone number extraction...")
    
    # Test with a simple search that should return businesses with phone numbers
    test_query = "restaurants in New York"
    max_results = 3  # Keep it small for testing
    
    print(f"🔍 Searching for: {test_query}")
    print(f"🎯 Max results: {max_results}")
    print("=" * 50)
    
    try:
        results = scrape_google_maps(test_query, max_results=max_results, visit_websites=False)
        
        print(f"\n📊 RESULTS SUMMARY:")
        print(f"Total businesses found: {len(results)}")
        
        phone_count = 0
        for i, business in enumerate(results, 1):
            print(f"\n{i}. {business['name']}")
            print(f"   Address: {business['address']}")
            print(f"   Phone: {business['mobile'] or 'Not found'}")
            print(f"   Rating: {business['rating'] or 'N/A'}")
            print(f"   Category: {business['category']}")
            
            if business['mobile']:
                phone_count += 1
        
        print(f"\n📞 Phone numbers found: {phone_count}/{len(results)}")
        
        if phone_count > 0:
            print("✅ Phone extraction is working!")
        else:
            print("❌ No phone numbers extracted - may need further debugging")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_phone_extraction()
