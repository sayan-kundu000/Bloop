import { apiClient, ttsApi } from '../../../api/client';
import { sanitizeFilename } from '../utils/audioUtils';

/**
 * Service handling authenticated audio resource resolution and memory-safe download.
 * Respects backend authorization boundaries and cleans up object URLs after download.
 */
export const audioService = {
  /**
   * Resolves a relative or absolute audio URL into a complete playable URL.
   */
  resolveUrl(urlOrPath: string): string {
    if (!urlOrPath) return '';
    return ttsApi.getAudioUrl(urlOrPath);
  },

  /**
   * Downloads an audio file by fetching it via the authenticated API client
   * (transmitting session cookies and Authorization bearer header), converting
   * to a Blob, creating an object URL, and triggering a download.
   *
   * Cleans up the object URL safely to prevent browser memory leaks.
   */
  async downloadAudio(
    downloadUrl: string,
    suggestedFilename?: string,
    fallbackName = 'bloop-speech',
    extension = 'mp3'
  ): Promise<void> {
    const filename = sanitizeFilename(suggestedFilename, fallbackName, extension);

    try {
      // Ensure we hit the API client with credentials
      const response = await apiClient.get(downloadUrl, {
        responseType: 'blob',
      });

      const blob = new Blob([response.data], {
        type: response.headers['content-type'] || 'audio/mpeg',
      });

      const objectUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = objectUrl;
      link.download = filename;
      link.style.display = 'none';
      document.body.appendChild(link);
      link.click();

      // Clean up DOM and revoke object URL
      document.body.removeChild(link);
      setTimeout(() => {
        window.URL.revokeObjectURL(objectUrl);
      }, 1000);
    } catch (err: unknown) {
      // If fetching the blob via apiClient fails (e.g. CORS or streaming restriction),
      // fallback to direct link trigger if it's an absolute or relative link
      try {
        const fullUrl = this.resolveUrl(downloadUrl);
        const fallbackLink = document.createElement('a');
        fallbackLink.href = fullUrl;
        fallbackLink.download = filename;
        fallbackLink.target = '_blank';
        fallbackLink.rel = 'noopener noreferrer';
        fallbackLink.style.display = 'none';
        document.body.appendChild(fallbackLink);
        fallbackLink.click();
        document.body.removeChild(fallbackLink);
      } catch (fallbackErr) {
        throw new Error('Audio download failed. Please check your network or try again.');
      }
    }
  },
};
