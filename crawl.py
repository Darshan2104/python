import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    # url = "https://www.haleon.com/investors/results-reports-presentations/results"
    # url = "https://investors.pepsico.com/investors/financial-information/quarterly-earnings/index.html"
    
    # url = "https://www.eternal.com/investor-relations/results/" 
    url = "https://indianexpress.com/"

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)
        if result.success:
            # Collect all links, internal and external
            links = []
            print(result.links)
            links.extend(result.links.get("internal", []))
            links.extend(result.links.get("external", []))
            # Filter and print only PDF links
            pdf_links = [link["href"] for link in links if ".pdf" in link["href"].lower()]
            for pdf in pdf_links:
                print(pdf)
        else:
            print("Crawl failed:", result.error_message)

if __name__ == "__main__":
    import time
    s = time.perf_counter()
    asyncio.run(main())
    e = time.perf_counter()
    print(f"Time taken: {e - s} seconds")