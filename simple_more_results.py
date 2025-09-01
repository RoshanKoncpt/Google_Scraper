#!/usr/bin/env python3
"""
Simple approach to get more results using the existing working scraper
"""

from alternative_approach import AlternativeGoogleMapsScraper
import time

def get_more_results_strategy():
    """Strategy to get more results by combining multiple searches"""
    
    print("🔍 Testing strategy to get more Google Maps results...")
    
    # Strategy 1: Multiple location-based searches
    base_query = "restaurants"
    locations = [
        "New York Manhattan",
        "New York Brooklyn", 
        "New York Queens",
        "Chicago downtown",
        "Chicago north side",
        "Los Angeles downtown",
        "Miami beach"
    ]
    
    all_results = []
    
    print(f"\n📍 STRATEGY 1: Multiple Location Searches")
    print("=" * 50)
    
    for i, location in enumerate(locations[:3], 1):  # Test first 3 locations
        query = f"{base_query} {location}"
        print(f"\n🔍 Search {i}: {query}")
        
        try:
            scraper = AlternativeGoogleMapsScraper(query, max_results=15)
            results = scraper.scrape()
            print(f"Found: {len(results)} businesses")
            
            # Add location info to results
            for result in results:
                result['search_location'] = location
            
            all_results.extend(results)
            
            # Show sample
            if results:
                print(f"Sample: {results[0]['name']} - {results[0]['phone'] or 'No phone'}")
            
            time.sleep(2)  # Brief pause between searches
            
        except Exception as e:
            print(f"Error with {location}: {e}")
    
    print(f"\n📊 STRATEGY 1 RESULTS:")
    print(f"Total businesses collected: {len(all_results)}")
    
    # Remove duplicates based on name and address
    unique_results = []
    seen = set()
    
    for result in all_results:
        identifier = (result['name'], result['address'][:50])
        if identifier not in seen:
            seen.add(identifier)
            unique_results.append(result)
    
    print(f"Unique businesses after deduplication: {len(unique_results)}")
    
    # Strategy 2: Different business categories
    print(f"\n🏪 STRATEGY 2: Different Business Categories")
    print("=" * 50)
    
    categories = [
        "coffee shops New York",
        "hotels Miami", 
        "pizza Chicago"
    ]
    
    category_results = []
    
    for i, category in enumerate(categories, 1):
        print(f"\n🔍 Category {i}: {category}")
        
        try:
            scraper = AlternativeGoogleMapsScraper(category, max_results=15)
            results = scraper.scrape()
            print(f"Found: {len(results)} businesses")
            
            category_results.extend(results)
            
            if results:
                print(f"Sample: {results[0]['name']} - {results[0]['phone'] or 'No phone'}")
                
            time.sleep(2)
            
        except Exception as e:
            print(f"Error with {category}: {e}")
    
    print(f"\n📊 STRATEGY 2 RESULTS:")
    print(f"Category businesses collected: {len(category_results)}")
    
    # Combined results
    combined_results = unique_results + category_results
    
    # Final deduplication
    final_unique = []
    final_seen = set()
    
    for result in combined_results:
        identifier = (result['name'], result['address'][:50])
        if identifier not in final_seen:
            final_seen.add(identifier)
            final_unique.append(result)
    
    print(f"\n🎯 FINAL COMBINED RESULTS:")
    print(f"Total unique businesses: {len(final_unique)}")
    
    # Count businesses with phone numbers
    phone_count = sum(1 for r in final_unique if r.get('mobile'))
    phone_rate = phone_count / len(final_unique) * 100 if final_unique else 0
    
    print(f"Businesses with phone numbers: {phone_count}/{len(final_unique)} ({phone_rate:.1f}%)")
    
    # Show top results
    print(f"\n📋 TOP 10 RESULTS:")
    for i, business in enumerate(final_unique[:10], 1):
        print(f"{i:2d}. {business['name']}")
        print(f"    📍 {business['address'][:60]}...")
        print(f"    📞 {business['mobile'] or 'No phone'}")
        print(f"    ⭐ {business['rating'] or 'No rating'}")
        if 'search_location' in business:
            print(f"    🔍 Found via: {business['search_location']}")
        print()
    
    # Analysis
    print(f"💡 ANALYSIS:")
    if len(final_unique) >= 20:
        print("✅ EXCELLENT: Successfully collected 20+ businesses!")
        print("This multi-search strategy works well.")
    elif len(final_unique) >= 10:
        print("✅ GOOD: Collected 10+ businesses.")
        print("Strategy shows promise, could expand with more locations/categories.")
    else:
        print("⚠️ LIMITED: Still getting few results.")
        print("May indicate Google Maps blocking or regional limitations.")
    
    return final_unique

if __name__ == "__main__":
    results = get_more_results_strategy()
    print(f"\n🏁 COMPLETED: Collected {len(results)} total businesses")
