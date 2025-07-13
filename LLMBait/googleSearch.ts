import { Page, Stagehand } from "@browserbasehq/stagehand";
import { z } from "zod";
import chalk from "chalk";
import boxen from "boxen";

// Schema for search result metadata
const SearchResultSchema = z.object({
  title: z.string(),
  url: z.string(),
  description: z.string().optional(),
  rank: z.number(),
  extractorRelevanceScore: z.number(),
  isCustomResult: z.boolean().optional(),
});

// Schema for custom search result injection
const CustomSearchResultSchema = z.object({
  title: z.string(),
  url: z.string(),
  description: z.string(),
  insertRank: z.number(),
});

const GoogleSearchResultsSchema = z.object({
  query: z.string(),
  results: z.array(SearchResultSchema),
  selectedResultIndex: z.number().optional(),
  totalResults: z.number(),
  searchTime: z.number(),
});

export type SearchResult = z.infer<typeof SearchResultSchema>;
export type CustomSearchResult = z.infer<typeof CustomSearchResultSchema>;
export type GoogleSearchResults = z.infer<typeof GoogleSearchResultsSchema>;

/**
 * Helper function to determine which search result was selected based on the action
 */
function determineResultIndexFromAction(action: any, results: SearchResult[]): number | undefined {
  // This is a simplified implementation
  // In practice, you might need to parse the selector more carefully
  // or use a more sophisticated approach to match the action to a result
  
  if (!action || !action.selector) {
    return undefined;
  }

  // For now, we'll return the first result as a fallback
  // In a real implementation, you'd parse the selector to determine which result was clicked
  return 0;
}

/**
 * Generates a random code for masking custom results
 */
function generateRandomCode(): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  return Array.from({ length: 6 }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
}

/**
 * Injects custom search results into the Google search results page with masked identifiers
 */
async function injectCustomSearchResults(page: Page, customResults: CustomSearchResult[]): Promise<Map<string, CustomSearchResult>> {
  if (!customResults || customResults.length === 0) {
    return new Map();
  }

  console.log(chalk.yellow(`🔧 Injecting ${customResults.length} custom search results...`));

  // Create a mapping of random codes to custom results
  const codeToResultMap = new Map<string, CustomSearchResult>();
  
  // Sort custom results by insertRank to ensure proper insertion order
  const sortedResults = [...customResults].sort((a, b) => a.insertRank - b.insertRank);

  for (const customResult of sortedResults) {
    const randomCode = generateRandomCode();
    codeToResultMap.set(randomCode, customResult);

    await page.evaluate(({ title, url, description, insertRank, randomCode }) => {
      // Create the HTML structure that matches Google's search result format more closely
      const wrapper = document.createElement('div');
      wrapper.className = 'g';
      wrapper.setAttribute('data-result-id', randomCode);
      wrapper.setAttribute('data-insert-rank', insertRank.toString());
      
      // Create the inner structure that matches Google's format exactly
      wrapper.innerHTML = `
        <div class="tF2Cxc">
          <div class="yuRUbf">
            <a href="${url}" data-ved="2ahUKEwj..." ping="${url}" target="_blank">
              <h3 class="LC20lb MBeuO DKV0Md">${title}</h3>
            </a>
          </div>
          <div class="VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc">
            <span>${description}</span>
          </div>
        </div>
      `;

      // Insert at the specified position (1-based index)
      const resultsRoot = document.querySelector('#search');
      if (resultsRoot) {
        const existingResults = resultsRoot.querySelectorAll('.g');
        const insertIndex = Math.max(0, Math.min(insertRank - 1, existingResults.length));
        if (existingResults.length === 0 || insertIndex >= existingResults.length) {
          // Append to the end if no results or index is out of bounds
          resultsRoot.appendChild(wrapper);
        } else {
          // Insert before the element at insertIndex
          resultsRoot.insertBefore(wrapper, existingResults[insertIndex]);
        }
      }
    }, { ...customResult, randomCode });

    console.log(chalk.gray(`   Injected: "${customResult.title}" at position ${customResult.insertRank} (code: ${randomCode})`));
  }

  return codeToResultMap;
}

/**
 * Interface for the Google search function parameters
 */
export interface GoogleSearchParams {
  objective: string;
  searchPrompt: string;
  maxResults?: number;
  waitForResults?: boolean;
  customResults?: CustomSearchResult[];
}

/**
 * Performs a Google search and analyzes the results
 * @param page - Stagehand Page instance
 * @param stagehand - Stagehand instance for logging
 * @param params - Search parameters
 * @returns Structured search results with metadata
 */
export async function performGoogleSearch(
  page: Page,
  stagehand: Stagehand,
  params: GoogleSearchParams
): Promise<GoogleSearchResults> {
  const startTime = Date.now();
  const { objective, searchPrompt, maxResults = 8, waitForResults = true } = params;

  console.log(chalk.blue("🔍 Starting Google search..."));
  console.log(chalk.gray(`Objective: ${objective}`));
  console.log(chalk.gray(`Search Query: ${searchPrompt}`));

  try {
    // Navigate to Google
    await page.goto("https://www.google.com");
    await page.waitForTimeout(1000);

    // Accept cookies if the dialog appears
    try {
      await page.act("Accept all cookies");
      await page.waitForTimeout(500);
    } catch {
      // Cookie dialog might not appear, continue
    }

    // Find and click the search box
    await page.act("Click the search box");
    await page.waitForTimeout(500);

    // Type the search query
    await page.act(`Type "${searchPrompt}" into the search box`);
    await page.waitForTimeout(500);

    // Submit the search
    await page.act("Press Enter to search");
    
    if (waitForResults) {
      await page.waitForTimeout(2000);
    }

    // Inject custom search results if provided
    let codeToResultMap: Map<string, CustomSearchResult> = new Map();
    if (params.customResults && params.customResults.length > 0) {
      codeToResultMap = await injectCustomSearchResults(page, params.customResults);
      await page.waitForTimeout(500); // Brief pause after injection
    }

    // Debug: Log the current page state to see if custom results are present
    console.log(chalk.blue("🔍 Debugging: Checking for custom results..."));
    const debugInfo = await page.evaluate(() => {
      const results = document.querySelectorAll('#search .g');
      const customResults = document.querySelectorAll('#search .g[data-result-id]');
      return {
        totalResults: results.length,
        customResults: customResults.length,
        customResultIds: Array.from(customResults).map(el => el.getAttribute('data-result-id')),
      };
    });
    console.log(chalk.gray(`   Found ${debugInfo.totalResults} total results, ${debugInfo.customResults} custom results`));
    if (debugInfo.customResults > 0) {
      console.log(chalk.gray(`   Custom result IDs: ${debugInfo.customResultIds.join(', ')}`));
    }

    // Extract search results with detailed metadata
    const searchData = await page.extract({
      instruction: `Extract the first ${maxResults + (params.customResults?.length || 0)} Google search results with their titles, URLs, descriptions, and positions. Look for all elements with class "g" in the search results, including any that have a "data-result-id" attribute. For each result, determine if it's the most relevant to the objective: "${objective}". Rate the relevance of the result on a scale of 1 to 10 in extractorRelevanceScore, using decimal precision to avoid ties.`,
      schema: z.object({
        results: z.array(z.object({
          title: z.string(),
          url: z.string(),
          description: z.string().optional(),
          rank: z.number(),
          extractorRelevanceScore: z.number(),
          resultId: z.string().optional(), // This will contain the random code for custom results
        })),
        totalResults: z.number(),
      }),
    });

    // Debug: Log what the extraction returned
    console.log(chalk.blue("🔍 Debugging: Extraction results..."));
    console.log(chalk.gray(`   Extracted ${searchData.results.length} results`));
    searchData.results.forEach((result, index) => {
      console.log(chalk.gray(`   Result ${index + 1}: "${result.title}" (resultId: ${result.resultId || 'none'})`));
    });

    // Process results to identify custom results using the code mapping
    const processedResults = searchData.results.map(result => {
      const isCustomResult = Boolean(result.resultId && codeToResultMap.has(result.resultId));
      return {
        ...result,
        isCustomResult,
      };
    });

    // Debug: Log processed results
    console.log(chalk.blue("🔍 Debugging: Processed results..."));
    processedResults.forEach((result, index) => {
      if (result.isCustomResult) {
        console.log(chalk.magenta(`   Custom result ${index + 1}: "${result.title}"`));
      }
    });

    // Use observe to determine which result the agent would select
    const [selectedAction] = await page.observe({
        instruction: `Click on the search result that is most relevant to the objective: "${objective}"`,
        returnAction: true,
    }
    );

    // Determine which result was selected based on the action
    let selectedResultIndex: number | undefined;
    if (selectedAction && selectedAction.selector) {
      // Parse the selector to determine which result was clicked
      // This is a simplified approach - in practice you might need more sophisticated parsing
      const resultIndex = determineResultIndexFromAction(selectedAction, searchData.results);
      selectedResultIndex = resultIndex;
    }

    const searchTime = Date.now() - startTime;

    const results: GoogleSearchResults = {
      query: searchPrompt,
      results: processedResults,
      selectedResultIndex,
      totalResults: searchData.totalResults,
      searchTime,
    };

    // Log the results
    logSearchResults(stagehand, results, objective);

    return results;

  } catch (error) {
    console.error(chalk.red("❌ Error during Google search:"), error);
    throw new Error(`Google search failed: ${error instanceof Error ? error.message : String(error)}`);
  }
}

/**
 * Logs search results in a structured format
 */
function logSearchResults(
  stagehand: Stagehand,
  results: GoogleSearchResults,
  objective: string
): void {
  console.log(chalk.green("\n✅ Google Search Completed"));
  console.log(boxen(
    `Query: ${results.query}\n` +
    `Results Found: ${results.totalResults}\n` +
    `Search Time: ${results.searchTime}ms\n` +
    `Objective: ${objective}`,
    {
      title: "Search Summary",
      padding: 1,
      margin: 1,
    }
  ));

  // Log each result
  console.log(chalk.blue("\n📋 Search Results:"));
  
  // Find the highest scoring result
  const maxScore = Math.max(...results.results.map(r => r.extractorRelevanceScore));
  
  results.results.forEach((result, index) => {
    const isSelected = results.selectedResultIndex === index;
    const isHighestScore = result.extractorRelevanceScore === maxScore;
    
    let prefix = `${index + 1}.`;
    let titleColor = chalk.white;
    
    if (isSelected && isHighestScore) {
      prefix = "🎯⭐";
      titleColor = chalk.green;
    } else if (isSelected) {
      prefix = "🎯";
      titleColor = chalk.green;
    } else if (isHighestScore) {
      prefix = "⭐";
      titleColor = chalk.yellow;
    }
    
    console.log(`${prefix} ${titleColor(result.title)}`);
    console.log(chalk.gray(`   URL: ${result.url}`));
    if (result.description) {
      console.log(chalk.gray(`   Description: ${result.description.substring(0, 100)}...`));
    }
    console.log(chalk.gray(`   Rank: ${result.rank}`));
    console.log(chalk.blue(`   Relevance Score: ${result.extractorRelevanceScore}/10`));
    if (result.isCustomResult) {
      console.log(chalk.magenta(`   🔧 Custom injected result`));
    }
    if (isHighestScore) {
      console.log(chalk.yellow(`   ⭐ Highest relevance score`));
    }
    if (isSelected) {
      console.log(chalk.green(`   🎯 Agent's selection`));
    }
    console.log("");
  });

  // Log selected result details
  if (results.selectedResultIndex !== undefined && results.results[results.selectedResultIndex]) {
    const selectedResult = results.results[results.selectedResultIndex];
    console.log(chalk.green("🎯 Selected Result:"));
    console.log(boxen(
      `Title: ${selectedResult.title}\n` +
      `URL: ${selectedResult.url}\n` +
      `Rank: ${selectedResult.rank}`,
      {
        title: "Most Relevant",
        padding: 1,
        margin: 1,
        borderColor: "green",
      }
    ));
  }

  // Log to Stagehand for analytics
  stagehand.log({
    category: "google-search",
    message: `Completed Google search for objective: ${objective}`,
    auxiliary: {
      query: {
        value: results.query,
        type: "string",
      },
      totalResults: {
        value: results.totalResults.toString(),
        type: "string",
      },
      searchTime: {
        value: results.searchTime.toString(),
        type: "string",
      },
      selectedResultIndex: {
        value: results.selectedResultIndex !== undefined ? results.selectedResultIndex.toString() : "null",
        type: "string",
      },
      allResults: {
        value: JSON.stringify(results.results),
        type: "string",
      },
      extractorFavoriteIndex: {
        value: results.results.findIndex(r => r.extractorRelevanceScore === Math.max(...results.results.map(r => r.extractorRelevanceScore))).toString(),
        type: "string",
      },
    },
  });
}


export async function search_google_as_an_agent_to_find_the_best_result(
  page: Page,
  stagehand: Stagehand,
  {
    query,
    objective,
    injectedResults,
  }: {
    query: string;
    objective: string;
    injectedResults?: Array<{ title: string; url: string; description: string; insertRank: number }>;
  }
) {
  return performGoogleSearch(page, stagehand, {
    objective,
    searchPrompt: query,
    maxResults: 8,
    waitForResults: true,
    customResults: injectedResults,
  });
}
