import asyncio
import urllib.parse
from typing import List, Dict, Optional
from crawl4ai import AsyncWebCrawler

from crawl4ai import AsyncWebCrawler, BrowserConfig, UndetectedAdapter
# from crawl4ai.async_crawler_strategy import AsyncPlaywrightCrawlerStrategy

# # Use both stealth and undetected modes
# browser_config = BrowserConfig(
#     enable_stealth=True,
#     headless=True
# )
# adapter = UndetectedAdapter()
# strategy = AsyncPlaywrightCrawlerStrategy(
#     browser_config=browser_config,
#     browser_adapter=adapter
# )

# --------- BASE CRAWLER CLASS ----------
class GoogleSearchCrawler:
    """A class to perform Google search and extract top K links using Crawl4AI"""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    async def google_search_top_k(
        self,
        query: str,
        k: int = 5,
        exclude_sites: Optional[List[str]] = None,
        filetype: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Perform Google search and return top K search result links.
        Optionally exclude certain sites or restrict to a file type.

        Args:
            query (str): Search query
            k (int): Number of top links to fetch (default: 5)
            exclude_sites (List[str], optional): Domains to exclude
            filetype (str, optional): Filter by filetype (e.g., 'pdf')

        Returns:
            List[Dict[str, str]]: List of dictionaries containing URL info
        """
        # Add filetype and site exclusions to query
        filtered_query = query
        if exclude_sites:
            for site in exclude_sites:
                filtered_query += f" -site:{site}"
        if filetype:
            filtered_query += f" filetype:{filetype}"

        encoded_query = urllib.parse.quote_plus(filtered_query)
        search_url = f"https://www.google.com/search?q={encoded_query}&num={k}&hl=en"
        # search_url = f"https://duckduckgo.com/html/?q={encoded_query}"


        async with AsyncWebCrawler(verbose=self.verbose) as crawler:
            try:
                result = await crawler.arun(url=search_url)
                if result.success:
                    external_links = result.links.get('external', [])
                    google_domains = ['google.com', 'google.co', 'gstatic.com', 'googleusercontent.com']
                    search_results = []

                    for link in external_links:
                        href = link.get('href', '')
                        text = link.get('text', '').strip()
                        base_domain = link.get('base_domain', '')

                        if (href and
                            not any(domain in base_domain for domain in google_domains) and
                            not href.startswith('javascript:') and
                            not href.startswith('mailto:')):
                            search_results.append({
                                'url': href,
                                'title': text,
                                'domain': base_domain
                            })
                    return search_results[:k]
                else:
                    print(f"Failed to crawl search results: {result.error_message}")
                    return []

            except Exception as e:
                print(f"Error during crawling: {str(e)}")
                return []

    def search_sync(
        self,
        query: str,
        k: int = 5,
        exclude_sites: Optional[List[str]] = None,
        filetype: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """Synchronous wrapper for the async search function"""
        return asyncio.run(self.google_search_top_k(query, k, exclude_sites, filetype))


# --------- EXAMPLE USAGE HELPERS ----------
def simple_google_search(
    query: str,
    k: int = 5,
    exclude_sites: Optional[List[str]] = None,
    filetype: Optional[str] = None
) -> List[Dict[str, str]]:
    """Simple function to perform Google search and return top K links"""
    crawler = GoogleSearchCrawler()
    return crawler.search_sync(query, k, exclude_sites, filetype)



# --------- MAIN EXECUTION EXAMPLES ----------
if __name__ == "__main__":
    # Example 1: Simple Google search, PDF filter and exclude youtube
    print("=== Simple Google Search ===")
    # query = "filetype:pdf site:http://nestle.com 2025 Q2 press release"
    query = "filetype:pdf Zomato FY 2025 Annual Report"

    results = simple_google_search(query, k=5)#, exclude_sites=["youtube.com"], filetype="pdf")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Domain: {result['domain']}\n")
