#!/usr/bin/env python3
"""
Integration example for Enhanced Google Maps Scraper
Shows how to integrate with your existing FastAPI application
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from enhanced_google_maps_scraper import enhanced_scrape_google_maps
import json
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/enhanced-google-maps")
async def enhanced_google_maps_search(
    query: str = Query(..., description="Search query for Google Maps"),
    max_results: int = Query(50, description="Maximum number of results to return"),
    visit_websites: bool = Query(False, description="Whether to visit business websites for additional contact info")
):
    """
    Enhanced Google Maps scraper endpoint that returns more results
    """
    try:
        print(f"🔍 Enhanced Google Maps search: {query}")
        print(f"🎯 Target results: {max_results}")
        
        # Use the enhanced scraper
        results = enhanced_scrape_google_maps(
            query=query,
            max_results=max_results,
            visit_websites=visit_websites
        )
        
        if not results:
            raise HTTPException(status_code=404, detail="No results found")
        
        # Filter and format results
        formatted_results = []
        contacts_found = 0
        
        for result in results:
            # Only include businesses with meaningful data
            if result.get('name') and result.get('name') != 'Unknown Business':
                formatted_result = {
                    "name": result.get('name', ''),
                    "address": result.get('address', ''),
                    "phone": result.get('mobile', ''),
                    "email": result.get('email', ''),
                    "website": result.get('website', ''),
                    "rating": result.get('rating'),
                    "review_count": result.get('review_count'),
                    "category": result.get('category', ''),
                    "google_maps_url": result.get('google_maps_url', ''),
                    "search_query": query
                }
                
                # Count contacts
                if formatted_result['phone'] or formatted_result['email']:
                    contacts_found += 1
                
                formatted_results.append(formatted_result)
        
        response = {
            "query": query,
            "total_results": len(formatted_results),
            "contacts_found": contacts_found,
            "timestamp": datetime.now().isoformat(),
            "results": formatted_results
        }
        
        print(f"✅ Enhanced search completed: {len(formatted_results)} results, {contacts_found} contacts")
        return response
        
    except Exception as e:
        print(f"❌ Enhanced search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/compare-scrapers")
async def compare_scrapers(
    query: str = Query(..., description="Search query to compare both scrapers"),
    max_results: int = Query(20, description="Maximum results for comparison")
):
    """
    Compare original vs enhanced scraper performance
    """
    try:
        from google_maps_scraper import scrape_google_maps
        
        print(f"🧪 Comparing scrapers for: {query}")
        
        # Test original scraper
        print("📊 Testing original scraper...")
        try:
            original_results = scrape_google_maps(query, max_results=max_results, visit_websites=False)
            original_count = len(original_results)
            original_contacts = sum(1 for r in original_results if r.get('mobile') or r.get('email'))
        except Exception as e:
            print(f"❌ Original scraper failed: {e}")
            original_count = 0
            original_contacts = 0
        
        # Test enhanced scraper
        print("🚀 Testing enhanced scraper...")
        try:
            enhanced_results = enhanced_scrape_google_maps(query, max_results=max_results, visit_websites=False)
            enhanced_count = len(enhanced_results)
            enhanced_contacts = sum(1 for r in enhanced_results if r.get('mobile') or r.get('email'))
        except Exception as e:
            print(f"❌ Enhanced scraper failed: {e}")
            enhanced_count = 0
            enhanced_contacts = 0
        
        # Calculate improvements
        result_improvement = ((enhanced_count - original_count) / max(original_count, 1)) * 100
        contact_improvement = ((enhanced_contacts - original_contacts) / max(original_contacts, 1)) * 100
        
        comparison = {
            "query": query,
            "original_scraper": {
                "results": original_count,
                "contacts": original_contacts
            },
            "enhanced_scraper": {
                "results": enhanced_count,
                "contacts": enhanced_contacts
            },
            "improvement": {
                "results_percent": round(result_improvement, 1),
                "contacts_percent": round(contact_improvement, 1),
                "additional_results": enhanced_count - original_count,
                "additional_contacts": enhanced_contacts - original_contacts
            },
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"📈 Comparison complete: {result_improvement:+.1f}% results, {contact_improvement:+.1f}% contacts")
        return comparison
        
    except Exception as e:
        print(f"❌ Comparison failed: {e}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Enhanced Google Maps Scraper API")
    print("📍 Endpoints:")
    print("   GET /enhanced-google-maps?query=restaurants+in+NYC&max_results=50")
    print("   GET /compare-scrapers?query=coffee+shops+in+SF&max_results=20")
    uvicorn.run(app, host="0.0.0.0", port=8000)
