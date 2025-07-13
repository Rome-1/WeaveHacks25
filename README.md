# LLMBait

Access demo at: 
https://weavehacks2025.romethorstenson.com


## Inspiration
I've been building sites and doing SEO since elementary school. I've seen the highs and the lows. SEO has been dead for years, but with massive amounts of content comes boons too—we can automate testing like we could never do with people.

The future of search is agentic. Browser and computer use agents are already here. But will they click on your site? In other words, what's clickbait for Agents?

## What it does
LLMBait is a revolutionary tool that simulates how AI agents interact with search results. Unlike traditional SEO tools that just analyze keywords, we run your experiments on agentic protocols on top of your content.

**Critically**: we aren't just asking agents which search result wins. We're running browser agents and following what they do.

Our platform allows content owners to:
- Test how AI agents perceive their search result titles and meta descriptions
- Inject custom search results into Google searches to see if agents would click on them
- Optimize content specifically for AI agent interactions, not just human users
- Monitor agent behavior in real-time using browser automation (locally, production coming soon)

## How we built it
- **Google Cloud ADK**: Powers our intelligent agents with state-of-the-art AI models
- **Weave**: Provides comprehensive monitoring and analytics for agent behavior
- **BrowserBase / Stagehand**: Core browser automation functionality that simulates real agent interactions

The system combines TypeScript backend for browser automation with Python agents for intelligent decision-making, creating a seamless bridge between AI agents and web content testing.

## Challenges we ran into
- Integrating multiple AI agent frameworks (Google ADK, Stagehand) into a cohesive system
- Ensuring realistic agent behavior that mirrors actual AI assistant interactions (injection scripts will have more features soon!)
- Balancing speed and accuracy in agent decision-making processes (plans to offload to Fly.io for rapid concurrent runs)
- Managing concurrent browser sessions for parallel agent testing (work in progress)

## Accomplishments that I'm proud of
- Successfully created a working prototype that can simulate AI agent interactions with search results with custom result injections
- Built a modular system that can test different agent behaviors and decision-making patterns
- Implemented real-time monitoring of agent actions using Weave
- Developed a scalable architecture that can handle multiple concurrent agent sessions

## Key Takeaways
- AI agents have fundamentally different interaction patterns than human users
- Traditional SEO metrics don't translate well to agentic search behavior
- Real browser automation is crucial for authentic agent simulation
- The future of content optimization will require agent-specific strategies

## What I learned
- ADK — no prior experience
- BrowserBase, Stagehand, Playwright - no prior experience
- Weave - no prior experience

## What's next for LLMBait
- Expand agent types to include different AI assistant personalities
- Add support for testing across multiple search engines beyond Google
- Implement A/B testing frameworks specifically designed for agent interactions
- Develop predictive models for agent behavior based on content characteristics

## Bonus
This was a 1 day (4.5 hour) solo project! 