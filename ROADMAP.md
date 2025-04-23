# 🔜 Video Upload + AI Metadata Pipeline Roadmap

This document outlines the planned features and improvements for the Video Upload + AI Metadata Pipeline project. These features are ranked by impact vs. effort to help prioritize development.


## Beef up the youtube uploader module
[ ] Add support for custom thumbnails
[ ] Implement scheduling for video publishing
[ ] add better prompt for the chapter markers
[ ] add in a step to go and generate 10 title options using the vid IQ logic that send me a discord message to pick one from
[ ] add in a step to go and generate 4 thumbnails using a custom workflow with pillo outliend in prd.txt
[ ] Add support for video tags and cards



## Planned Features (Ranked by Impact vs Effort)

| Priority | Feature                       | Impact | Effort | Description                                       |
| -------- | ----------------------------- | ------ | ------ | ------------------------------------------------- |
| 1        | Skool Post Generator          | ⭐⭐⭐⭐   | ⭐⭐     | Auto-post insights to Skool based on video output |
| 2        | Daily AI News Video Generator | ⭐⭐⭐⭐   | ⭐⭐⭐    | Scrape top AI stories → script + upload           |
| 3        | YouTube Comment Q&A Generator | ⭐⭐⭐    | ⭐⭐     | Pull top comments, answer via Gemini              |
| 4        | AI Strategy Devlog Generator  | ⭐⭐⭐    | ⭐⭐⭐    | Summarize weekly building efforts as content      |
| 5        | 3-Part AI Agent Series        | ⭐⭐⭐⭐⭐  | ⭐⭐⭐⭐⭐  | Fully written/recorded video series on agents     |


add news pipeline with vertex

## Technical Improvements

### Video Processor Module

1. Add more robust error handling for different types of audio files and formats
2. Implement retry logic for API calls
3. Increase test coverage for edge cases and error conditions
4. Consider adding support for additional audio formats
5. Optimize audio extraction parameters for better quality
6. Add integration tests with actual GCS and Gemini API (using test credentials)

### YouTube Uploader

✅ Implement basic YouTube uploader functionality
✅ Support for both Daily and Main channels
✅ Add chapters to video descriptions
✅ Support for captions/subtitles
✅ Prevent duplicate uploads with marker files
✅ Set default privacy status to "unlisted" (configurable)

Future Improvements:
1. Add support for keywords/tags
2. Add support for custom thumbnails
3. Implement scheduling for video publishing
4. Add support for playlists
5. Implement analytics tracking for uploaded videos

### CI/CD Pipeline

1. Implement GitHub Actions workflow for automated testing
2. Set up continuous deployment to Cloud Run
3. Add performance tests to measure processing time for different file sizes
4. Create a test data generator for creating test audio/video files with known content

### Infrastructure

1. **Implement Cloud Monitoring for the entire pipeline (HIGH PRIORITY)**
   - Configure CPU, memory, and request latency monitoring for Cloud Run services
   - Create uptime checks to verify service availability
   - Set up custom log-based metrics to track processing success rates and times
   - Configure alerting policies for service outages and high error rates
   - Build custom dashboards for operational insights and debugging
   - Implement distributed tracing to identify bottlenecks in the processing pipeline
2. Add cost optimization measures
3. Implement better logging and error reporting
4. Set up disaster recovery procedures

## Long-term Vision

The long-term vision for this project is to create a fully automated content creation and distribution pipeline that can:

1. Generate ideas for content based on trending topics
2. Create scripts and outlines using AI
3. Record and edit videos with minimal human intervention
4. Process and upload videos with appropriate metadata
5. Promote content across multiple platforms
6. Analyze performance and adjust strategy accordingly

This roadmap will be updated regularly as features are implemented and new priorities emerge.
