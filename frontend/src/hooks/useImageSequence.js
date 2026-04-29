import { useState, useEffect, useRef, useCallback } from 'react'

/**
 * Custom hook for managing an image sequence animation.
 * Pre-loads all frames, tracks progress, handles errors with fallbacks.
 *
 * @param {string} basePath - Base path to frame directory (e.g., '/compass-sequence/')
 * @param {number} totalFrames - Total number of frames in the sequence
 * @param {string} prefix - Filename prefix (default: 'frame_')
 * @param {string} extension - File extension (default: '.jpg')
 */
export function useImageSequence(
  basePath = '/compass-sequence/',
  totalFrames = 240,
  prefix = 'frame_',
  extension = '.jpg'
) {
  const [progress, setProgress] = useState(0)
  const [isLoaded, setIsLoaded] = useState(false)
  const [error, setError] = useState(null)
  const imagesRef = useRef([])
  const loadedCountRef = useRef(0)
  const failedFramesRef = useRef(new Set())

  // Generate the filename for a given frame index (1-indexed)
  const getFramePath = useCallback(
    (index) => {
      const padded = String(index).padStart(4, '0')
      return `${basePath}${prefix}${padded}${extension}`
    },
    [basePath, prefix, extension]
  )

  // Load all images
  useEffect(() => {
    let cancelled = false
    const images = new Array(totalFrames)
    imagesRef.current = images
    loadedCountRef.current = 0

    // Load in batches to avoid overwhelming the browser
    const BATCH_SIZE = 20
    let currentBatch = 0

    const loadBatch = () => {
      if (cancelled) return

      const start = currentBatch * BATCH_SIZE
      const end = Math.min(start + BATCH_SIZE, totalFrames)

      const batchPromises = []

      for (let i = start; i < end; i++) {
        const frameIndex = i + 1 // 1-indexed filenames
        const promise = new Promise((resolve) => {
          const img = new Image()
          img.onload = () => {
            if (!cancelled) {
              images[i] = img
              loadedCountRef.current++
              setProgress(Math.round((loadedCountRef.current / totalFrames) * 100))
            }
            resolve()
          }
          img.onerror = () => {
            if (!cancelled) {
              failedFramesRef.current.add(i)
              loadedCountRef.current++
              setProgress(Math.round((loadedCountRef.current / totalFrames) * 100))
            }
            resolve()
          }
          img.src = getFramePath(frameIndex)
        })
        batchPromises.push(promise)
      }

      Promise.all(batchPromises).then(() => {
        if (cancelled) return
        currentBatch++
        if (currentBatch * BATCH_SIZE < totalFrames) {
          // Small delay between batches to let the browser breathe
          requestAnimationFrame(loadBatch)
        } else {
          // All batches complete
          const failedCount = failedFramesRef.current.size
          if (failedCount > totalFrames * 0.5) {
            setError(`Too many frames failed to load (${failedCount}/${totalFrames})`)
          }
          setIsLoaded(true)
        }
      })
    }

    loadBatch()

    return () => {
      cancelled = true
    }
  }, [totalFrames, getFramePath])

  /**
   * Get the image element for a given frame index (0-indexed).
   * Falls back to nearest loaded neighbor if the requested frame failed.
   */
  const getFrame = useCallback(
    (index) => {
      const clampedIndex = Math.max(0, Math.min(totalFrames - 1, Math.round(index)))

      // Direct hit
      if (imagesRef.current[clampedIndex]) {
        return imagesRef.current[clampedIndex]
      }

      // Fallback: find nearest loaded frame
      for (let offset = 1; offset < totalFrames; offset++) {
        const before = clampedIndex - offset
        const after = clampedIndex + offset
        if (before >= 0 && imagesRef.current[before]) return imagesRef.current[before]
        if (after < totalFrames && imagesRef.current[after]) return imagesRef.current[after]
      }

      return null
    },
    [totalFrames]
  )

  return {
    getFrame,
    progress,
    isLoaded,
    error,
    totalFrames,
    failedCount: failedFramesRef.current.size,
  }
}
