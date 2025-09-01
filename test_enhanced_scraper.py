#!/usr/bin/env python3
"""
Test script for Enhanced Google Maps Scraper
Compares original vs enhanced scraper performance
"""

import json
import time
from datetime import datetime
from enhanced_google_maps_scraper import enhanced_scrape_google_maps
from google_maps_scraper import scrape_google_maps

def test_scraper_comparison():
    """Test both scrapers and compare results"""
    
    test_queries = [
        "restaurants in San Francisco",
        "coffee shops in New York", 
        "dentists in Los Angeles",
        "gyms in Chicago",
        "hotels in Miami"
    ]
    
    results_comparison = []
    
    print("🧪 SCRAPER COMPARISON TEST")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}/{len(test_queries)}: {query}")
        print("-" * 50)
        
        # Test original scraper
        print("📊 Testing ORIGINAL scraper...")
        start_time = time.time()
        try:
            original_results = scrape_google_maps(query, max_results=20, visit_websites=False)
            original_count = len(original_results)
            original_time = time.time() - start_time
            original_contacts = sum(1 for r in original_results if r.get('mobile') or r.get('email'))
        except Exception as e:
            print(f"❌ Original scraper failed: {e}")
            original_count = 0
            original_time = 0
            original_contacts = 0
        
        print(f"   Results: {original_count}, Contacts: {original_contacts}, Time: {original_time:.1f}s")
        
        # Wait between tests
        time.sleep(5)
        
        # Test enhanced scraper
        print("🚀 Testing ENHANCED scraper...")
        start_time = time.time()
        try:
            enhanced_results = enhanced_scrape_google_maps(query, max_results=20, visit_websites=False)
            enhanced_count = len(enhanced_results)
            enhanced_time = time.time() - start_time
            enhanced_contacts = sum(1 for r in enhanced_results if r.get('mobile') or r.get('email'))
        except Exception as e:
            print(f"❌ Enhanced scraper failed: {e}")
            enhanced_count = 0
            enhanced_time = 0
            enhanced_contacts = 0
        
        print(f"   Results: {enhanced_count}, Contacts: {enhanced_contacts}, Time: {enhanced_time:.1f}s")
        
        # Calculate improvement
        improvement = ((enhanced_count - original_count) / max(original_count, 1)) * 100
        contact_improvement = ((enhanced_contacts - original_contacts) / max(original_contacts, 1)) * 100
        
        result = {
            'query': query,
            'original': {
                'count': original_count,
                'contacts': original_contacts,
                'time': original_time
            },
            'enhanced': {
                'count': enhanced_count,
                'contacts': enhanced_contacts,
                'time': enhanced_time
            },
            'improvement': {
                'results': improvement,
                'contacts': contact_improvement
            }
        }
        
        results_comparison.append(result)
        
        print(f"📈 Improvement: {improvement:+.1f}% results, {contact_improvement:+.1f}% contacts")
        
        # Wait between queries to avoid being blocked
        if i < len(test_queries):
            print("⏳ Waiting 10 seconds before next test...")
            time.sleep(10)
    
    # Final summary
    print(f"\n" + "=" * 60)
    print("🎉 COMPARISON SUMMARY")
    print("=" * 60)
    
    total_original = sum(r['original']['count'] for r in results_comparison)
    total_enhanced = sum(r['enhanced']['count'] for r in results_comparison)
    total_original_contacts = sum(r['original']['contacts'] for r in results_comparison)
    total_enhanced_contacts = sum(r['enhanced']['contacts'] for r in results_comparison)
    
    overall_improvement = ((total_enhanced - total_original) / max(total_original, 1)) * 100
    contact_improvement = ((total_enhanced_contacts - total_original_contacts) / max(total_original_contacts, 1)) * 100
    
    print(f"📊 Total Results:")
    print(f"   Original: {total_original}")
    print(f"   Enhanced: {total_enhanced}")
    print(f"   Improvement: {overall_improvement:+.1f}%")
    print(f"")
    print(f"📞 Total Contacts:")
    print(f"   Original: {total_original_contacts}")
    print(f"   Enhanced: {total_enhanced_contacts}")
    print(f"   Improvement: {contact_improvement:+.1f}%")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scraper_comparison_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results_comparison, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {filename}")
    
    return results_comparison

def test_single_enhanced_scraper():
    """Test just the enhanced scraper with a single query"""
    
    query = "restaurants in San Francisco"
    max_results = 50
    
    print(f"🧪 SINGLE ENHANCED SCRAPER TEST")
    print(f"🔍 Query: {query}")
    print(f"🎯 Target: {max_results} results")
    print("=" * 60)
    
    start_time = time.time()
    results = enhanced_scrape_google_maps(query, max_results=max_results, visit_websites=False)
    total_time = time.time() - start_time
    
    # Analyze results
    contacts_found = sum(1 for r in results if r.get('mobile') or r.get('email'))
    phones_found = sum(1 for r in results if r.get('mobile'))
    emails_found = sum(1 for r in results if r.get('email'))
    websites_found = sum(1 for r in results if r.get('website'))
    
    print(f"\n📊 RESULTS ANALYSIS")
    print("=" * 60)
    print(f"✅ Total businesses found: {len(results)}")
    print(f"📞 Businesses with phone: {phones_found}")
    print(f"📧 Businesses with email: {emails_found}")
    print(f"🌐 Businesses with website: {websites_found}")
    print(f"📋 Total contacts: {contacts_found}")
    print(f"⏱️ Total time: {total_time:.1f} seconds")
    print(f"⚡ Rate: {len(results)/total_time*60:.1f} businesses/minute")
    
    # Show sample results
    print(f"\n📝 SAMPLE RESULTS (first 10)")
    print("=" * 60)
    for i, result in enumerate(results[:10], 1):
        contact_info = []
        if result.get('mobile'):
            contact_info.append(f"📞 {result['mobile']}")
        if result.get('email'):
            contact_info.append(f"📧 {result['email']}")
        if result.get('website'):
            contact_info.append("🌐")
        
        contact_str = " | ".join(contact_info) if contact_info else "No contacts"
        
        print(f"{i:2d}. {result['name']}")
        print(f"    📍 {result['address'][:60]}...")
        print(f"    {contact_str}")
        if result.get('rating'):
            print(f"    ⭐ {result['rating']} ({result.get('review_count', 0)} reviews)")
        print()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"enhanced_scraper_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Full results saved to: {filename}")
    
    return results

if __name__ == "__main__":
    print("🚀 Enhanced Google Maps Scraper Test Suite")
    print("=" * 60)
    
    choice = input("Choose test:\n1. Single enhanced scraper test\n2. Comparison test (original vs enhanced)\nEnter choice (1 or 2): ")
    
    if choice == "1":
        test_single_enhanced_scraper()
    elif choice == "2":
        test_scraper_comparison()
    else:
        print("Invalid choice. Running single enhanced scraper test...")
        test_single_enhanced_scraper()
