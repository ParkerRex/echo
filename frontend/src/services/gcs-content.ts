/**
 * Service to handle fetching content from Google Cloud Storage
 */

// Utility to fetch content from GCS using a publicly accessible URL
export async function fetchGCSContent(url: string): Promise<string> {
  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch content: ${response.status} ${response.statusText}`);
    }
    
    return await response.text();
  } catch (error) {
    console.error("Error fetching GCS content:", error);
    throw error;
  }
}

// Generate a publicly accessible URL for a GCS file (if permission allows)
export function getGCSPublicUrl(bucketName: string, filePath: string): string {
  return `https://storage.googleapis.com/${bucketName}/${filePath}`;
}

// Process the output_files paths from Firestore to generate usable URLs
export function getContentUrls(bucketName: string, outputFiles: Record<string, string> = {}) {
  const urls: Record<string, string> = {};
  
  Object.entries(outputFiles).forEach(([key, path]) => {
    if (path) {
      urls[key] = getGCSPublicUrl(bucketName, path);
    }
  });
  
  return urls;
}

// Try to fetch content, returns null if not available
export async function tryFetchContent(
  bucketName: string | undefined, 
  outputFiles: Record<string, string> = {}, 
  contentType: string
): Promise<string | null> {
  if (!bucketName || !outputFiles[contentType]) {
    return null;
  }
  
  try {
    const url = getGCSPublicUrl(bucketName, outputFiles[contentType]);
    const content = await fetchGCSContent(url);
    return content;
  } catch (error) {
    console.error(`Error fetching ${contentType}:`, error);
    return null;
  }
}