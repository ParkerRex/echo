# 📊 Monitoring Guide

This guide provides instructions for monitoring the Video Processor application in production.

## 🔍 Monitoring Options

There are several ways to monitor the Video Processor application:

### 1. Google Cloud Console (Web UI)

The easiest way to monitor your Cloud Run services is through the Google Cloud Console:

```bash
# Open the Cloud Run services page in your browser
open "https://console.cloud.google.com/run?project=automations-457120"
```

This gives you a visual dashboard where you can:
- See all services across all regions
- Check their status
- View logs
- See metrics like request count and latency
- Check revision history

### 2. Command Line Monitoring

For command-line monitoring, you can use the following commands:

#### View Service Status

```bash
# List all Cloud Run services
gcloud run services list --project=automations-457120
```

#### View Logs

```bash
# View recent logs for the video-processor service
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=video-processor AND resource.labels.location=us-east1' \
  --limit=20 \
  --format='table(timestamp, severity, textPayload)'
```

#### View Eventarc Triggers

```bash
# List all Eventarc triggers
gcloud eventarc triggers list --project=automations-457120
```

#### View GCS Bucket Contents

```bash
# List files in the daily-raw directory
gsutil ls gs://automations-youtube-videos-2025/daily-raw/

# List files in the processed-daily directory
gsutil ls gs://automations-youtube-videos-2025/processed-daily/
```

### 3. Terminal-based Monitoring Script

We've created a custom monitoring script that provides an HTOP-like experience in your terminal. This script combines several gcloud commands to provide a comprehensive view of your services.

```bash
# Make the script executable (only needed once)
chmod +x monitor-services.sh

# Run the monitoring script
./monitor-services.sh
```

The script provides:
- Service status
- Recent logs
- Eventarc triggers
- Bucket contents
- Testing capabilities

### 4. Cloud Monitoring Dashboards

For more advanced monitoring, you can set up Cloud Monitoring dashboards:

```bash
# Open Cloud Monitoring
open "https://console.cloud.google.com/monitoring/dashboards?project=automations-457120"
```

You can create custom dashboards with:
- CPU and memory usage
- Request latency
- Error rates
- Custom metrics

## 🚨 Setting Up Alerts

You can set up alerts to be notified when there are issues with your services:

```bash
# Open Cloud Monitoring Alerting
open "https://console.cloud.google.com/monitoring/alerting?project=automations-457120"
```

We recommend setting up alerts for:
- Error rates exceeding thresholds (e.g., more than 5 errors in 5 minutes)
- High latency (e.g., p95 latency > 2000ms)
- Instance count (e.g., more than 10 instances running)
- Memory usage (e.g., memory usage > 80%)

## 🔄 Testing the Service

You can test the service by uploading a video to the GCS bucket:

```bash
# Upload a test video to the GCS bucket
gsutil cp test_data/test-video.mp4 gs://automations-youtube-videos-2025/daily-raw/test-$(date +%s).mp4
```

Then monitor the logs to see if the service processes the file:

```bash
# View logs for the video-processor service
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=video-processor AND resource.labels.location=us-east1 AND timestamp > "-5m"' \
  --limit=20 \
  --format='table(timestamp, severity, textPayload)'
```

## 🔍 Troubleshooting Common Issues

### 1. Service Not Processing Files

If the service is not processing files, check:
- The Eventarc trigger is correctly configured
- The service account has the necessary permissions
- The GCS bucket notification is properly set up

```bash
# Check the Eventarc trigger
gcloud eventarc triggers describe video-processor-trigger --location=us-east1

# Check the service account permissions
gcloud iam service-accounts get-iam-policy video-processor-sa@automations-457120.iam.gserviceaccount.com
```

### 2. Service Returning 500 Errors

If the service is returning 500 errors, check:
- The logs for error messages
- The service account has the necessary permissions
- The Gemini API is available

```bash
# Check for error logs
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=video-processor AND resource.labels.location=us-east1 AND severity=ERROR' \
  --limit=20 \
  --format='table(timestamp, severity, textPayload)'
```

### 3. Files Not Being Processed Correctly

If files are not being processed correctly, check:
- The file format is correct (MP4)
- The file is in the correct directory
- The ffmpeg command is working correctly

```bash
# Check the file format
gsutil cat gs://automations-youtube-videos-2025/daily-raw/your-file.mp4 | file -

# Check the ffmpeg logs
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=video-processor AND resource.labels.location=us-east1 AND textPayload=*ffmpeg*' \
  --limit=20 \
  --format='table(timestamp, severity, textPayload)'
```

## 📊 Monitoring Best Practices

1. **Regular Checks**: Set up a schedule to check the service status and logs regularly
2. **Automated Alerts**: Configure alerts for critical issues
3. **Log Analysis**: Analyze logs to identify patterns and potential issues
4. **Performance Monitoring**: Monitor performance metrics to identify bottlenecks
5. **Capacity Planning**: Monitor resource usage to plan for scaling

## 🔄 Updating the Service

When updating the service, make sure to:
1. Test the changes locally
2. Deploy to a staging environment if available
3. Monitor the service after deployment
4. Roll back if there are issues

```bash
# Deploy the service
./deploy.sh

# Monitor the service after deployment
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=video-processor AND resource.labels.location=us-east1 AND timestamp > "-5m"' \
  --limit=20 \
  --format='table(timestamp, severity, textPayload)'
```

## 📚 Additional Resources

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Google Cloud Monitoring Documentation](https://cloud.google.com/monitoring/docs)
- [Google Cloud Logging Documentation](https://cloud.google.com/logging/docs)
- [Eventarc Documentation](https://cloud.google.com/eventarc/docs)
- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
