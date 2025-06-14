# MVP Priorities - What Matters Most

## Core Value Proposition
**Eliminate friction between idea and upload while providing intelligence on competition and monetization**

## Priority Matrix (Impact vs Effort)

### 🎯 High Impact, Low Effort (DO FIRST)
1. **Quick Capture System**
   - Cmd+enter submission
   - Paste detection (idea vs transcript)
   - Voice-to-text capture
   - Why: Core friction point, relatively simple to implement

2. **AI Content Generation**
   - Claude API integration
   - Basic prompt templates
   - Title/description/script generation
   - Why: Immediate value, uses existing APIs

3. **Basic Pipeline Flow**
   - Idea → Outline → Script → Package
   - Simple state management
   - Why: Core user journey, foundation for everything else

### 💪 High Impact, Medium Effort
4. **Competitor Intelligence (Simplified)**
   - Track 3-5 competitors
   - Basic performance metrics
   - Manual channel addition
   - Why: Unique differentiator, manageable scope

5. **YouTube Integration**
   - Upload automation
   - Basic analytics pull
   - Why: Core platform integration

### 🔄 Medium Impact, Low Effort
6. **Export Features**
   - Copy to clipboard
   - Download as markdown
   - Why: User convenience, easy win

### ⏳ Defer for Later
- Sponsor discovery engine
- Revenue tracking
- Trend detection
- iOS app
- Advanced analytics

## Technical Priorities

### Week 1-2: Foundation
1. Set up tRPC + Hono API structure
2. Basic auth with Supabase
3. Database schema (users, ideas, videos)
4. Quick capture UI

### Week 3-4: Core Features
1. Claude API integration
2. Content generation pipeline
3. Basic competitor tracking
4. YouTube OAuth + upload

### Week 5-6: Polish & Launch
1. Error handling
2. Loading states
3. Basic analytics
4. User feedback loop

## Key Decisions for MVP

### What to Build
- **Single-player first** (no teams/collaboration)
- **Web-only** (no mobile app)
- **Manual competitor entry** (no auto-discovery)
- **Basic templates** (3-5 video types max)
- **Simple UI** (function over form)

### What to Skip
- Complex monetization tracking
- Sponsor discovery
- Trend analysis
- Video editing features
- Advanced analytics

### Technical Choices
- **Supabase** for auth + DB (fast setup)
- **Vercel** for hosting (easy deploys)
- **Claude API** for AI (best quality)
- **YouTube Data API v3** (official integration)
- **Shadcn/ui** for components (rapid development)

## Success Metrics for MVP
1. User can go from idea to uploaded video in <10 minutes
2. AI generates usable content 80% of the time
3. Competitor tracking provides actionable insights
4. System handles 100 videos without performance issues

## Risk Mitigation
- **YouTube API limits**: Cache aggressively, batch requests
- **AI costs**: Set user limits, optimize prompts
- **Complexity creep**: Ruthlessly cut features
- **User adoption**: Focus on one specific creator type

## Next Steps
1. Validate tech stack choices
2. Create detailed user flow for MVP
3. Set up development environment
4. Build quick capture prototype
5. Test with 3-5 beta users

## Questions to Answer
- Which video types are most common? (tutorials, reviews, vlogs?)
- What's the #1 friction point for creators today?
- How much would creators pay for this?
- What competitor features do they actually use?