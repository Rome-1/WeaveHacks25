import fetch from "node-fetch";
import { JSDOM } from "jsdom";

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
  status: "success" | "error";
  url: string;
  title?: string;
  metadescription?: string;
  error_message?: string;
}> {
  try {
    const response = await fetch(url, { headers: { "User-Agent": "Mozilla/5.0" } });
    if (!response.ok) {
      return {
        status: "error",
        url,
        error_message: `Failed to fetch URL: ${response.status} ${response.statusText}`,
      };
    }
    const html = await response.text();
    const dom = new JSDOM(html);
    const doc = dom.window.document;
    const title = doc.querySelector("title")?.textContent || "";
    const metadescription = doc.querySelector('meta[name="description"]')?.getAttribute("content") || "";
    return {
      status: "success",
      url,
      title,
      metadescription,
    };
  } catch (error: any) {
    return {
      status: "error",
      url,
      error_message: error.message || String(error),
    };
  }
} 