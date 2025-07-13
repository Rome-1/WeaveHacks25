import { Stagehand } from "@browserbasehq/stagehand";
import StagehandConfig from "./stagehand.config.js";

/**
 * Scrapes the given URL and returns its title and meta description.
 *
 * This tool is for content owners to trial and select titles/metadescriptions for their pages, simulating how a browser agent would choose among search results.
 *
 * Parameters:
 *   url (string): The URL to scrape.
 *
 * Returns:
 *   An object with:
 *     - status ("success" or "error")
 *     - url (string): The URL that was scraped
 *     - title (string): The page title (if found)
 *     - metadescription (string): The meta description (if found)
 *     - error_message (string): Error message if status is "error"
 *
 * Example usage:
 *   const result = await scrape_url_metadata("https://example.com");
 */
export async function scrape_url_metadata(url: string): Promise<{
  status: string;
  url: string;
  title?: string;
  metadescription?: string;
  error_message?: string;
}> {
  const sh = new Stagehand(StagehandConfig);
  
  try {
    await sh.init();
    await sh.page.goto(url);
    
    // Extract title and meta description
    const metadata = await sh.page.evaluate(() => {
      const title = document.title || '';
      const metaDescription = document.querySelector('meta[name="description"]')?.getAttribute('content') || '';
      
      return {
        title,
        metadescription: metaDescription
      };
    });
    
    await sh.close();
    
    return {
      status: "success",
      url,
      title: metadata.title,
      metadescription: metadata.metadescription
    };
  } catch (error) {
    await sh.close();
    return {
      status: "error",
      url,
      error_message: error instanceof Error ? error.message : "Unknown error occurred"
    };
  }
} 