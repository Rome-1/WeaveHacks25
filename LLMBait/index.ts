import { Stagehand, Page, BrowserContext } from "@browserbasehq/stagehand";
import StagehandConfig from "./stagehand.config.js";
import chalk from "chalk";
import boxen from "boxen";
import { drawObserveOverlay, clearOverlays, actWithCache } from "./utils.js";
import { z } from "zod";
import { performGoogleSearch } from "./googleSearch.js";

/**
 * 🤘 Welcome to Stagehand! Thanks so much for trying us out!
 * 🛠️ CONFIGURATION: stagehand.config.ts will help you configure Stagehand
 *
 * 📝 Check out our docs for more fun use cases, like building agents
 * https://docs.stagehand.dev/
 *
 * 💬 If you have any feedback, reach out to us on Slack!
 * https://stagehand.dev/slack
 *
 * 📚 You might also benefit from the docs for Zod, Browserbase, and Playwright:
 * - https://zod.dev/
 * - https://docs.browserbase.com/
 * - https://playwright.dev/docs/intro
 */
async function main({
  page,
  context,
  stagehand,
}: {
  page: Page; // Playwright Page with act, extract, and observe methods
  context: BrowserContext; // Playwright BrowserContext
  stagehand: Stagehand; // Stagehand instance
}) {
  // Run Google search for the finest fedora
  const searchResults = await performGoogleSearch(page, stagehand, {
    objective: "Find information about high-quality fedora hats",
    searchPrompt: "find the finest fedora",
    maxResults: 8,
    waitForResults: true,
  });

  console.log(chalk.green("\n🎩 Fedora Search Complete!"));
  console.log(boxen(
    `Found ${searchResults.totalResults} results in ${searchResults.searchTime}ms\n` +
    `Agent selected result #${searchResults.selectedResultIndex !== undefined ? searchResults.selectedResultIndex + 1 : 'none'}\n` +
    `Highest relevance score: ${Math.max(...searchResults.results.map(r => r.extractorRelevanceScore))}/10`,
    {
      title: "Search Summary",
      padding: 1,
      margin: 1,
      borderColor: "green",
    }
  ));

  // Log final metrics
  stagehand.log({
    category: "fedora-search",
    message: `Completed fedora search with ${searchResults.totalResults} results`,
    auxiliary: {
      searchTime: {
        value: searchResults.searchTime.toString(),
        type: "string",
      },
      selectedResultIndex: {
        value: searchResults.selectedResultIndex !== undefined ? searchResults.selectedResultIndex.toString() : "null",
        type: "string",
      },
      maxRelevanceScore: {
        value: Math.max(...searchResults.results.map(r => r.extractorRelevanceScore)).toString(),
        type: "string",
      },
    },
  });
}

/**
 * This is the main function that runs when you do npm run start
 *
 * YOU PROBABLY DON'T NEED TO MODIFY ANYTHING BELOW THIS POINT!
 *
 */
async function run() {
  const stagehand = new Stagehand({
    ...StagehandConfig,
  });
  await stagehand.init();

  if (StagehandConfig.env === "BROWSERBASE" && stagehand.browserbaseSessionID) {
    console.log(
      boxen(
        `View this session live in your browser: \n${chalk.blue(
          `https://browserbase.com/sessions/${stagehand.browserbaseSessionID}`,
        )}`,
        {
          title: "Browserbase",
          padding: 1,
          margin: 3,
        },
      ),
    );
  }

  const page = stagehand.page;
  const context = stagehand.context;
  await main({
    page,
    context,
    stagehand,
  });
  await stagehand.close();
  console.log(
    `\n🤘 Thanks so much for using Stagehand! Reach out to us on Slack if you have any feedback: ${chalk.blue(
      "https://stagehand.dev/slack",
    )}\n`,
  );
}

run();
