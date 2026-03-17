import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Generate unique ID
export function generateId(): string {
  return Math.random().toString(36).substring(2, 15);
}

// Format timestamp
export function formatTimestamp(date: Date): string {
  return new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: 'numeric',
    hour12: true,
  }).format(date);
}

// Format date for history
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (days === 0) {
    return 'Today';
  } else if (days === 1) {
    return 'Yesterday';
  } else if (days < 7) {
    return `${days} days ago`;
  } else {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  }
}

// Confidence badge helpers
export function getConfidenceLevel(confidence: number): 'high' | 'medium' | 'low' {
  if (confidence >= 0.85) return 'high';
  if (confidence >= 0.65) return 'medium';
  return 'low';
}

export function getConfidenceColor(confidence: number): string {
  const level = getConfidenceLevel(confidence);
  switch (level) {
    case 'high':
      return 'text-green-400 bg-green-400/10 border-green-400/20';
    case 'medium':
      return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
    case 'low':
      return 'text-red-400 bg-red-400/10 border-red-400/20';
    default:
      return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
  }
}

export function getConfidenceIcon(confidence: number): string {
  const level = getConfidenceLevel(confidence);
  switch (level) {
    case 'high':
      return '🟢';
    case 'medium':
      return '🟡';
    case 'low':
      return '🔴';
    default:
      return '⚪';
  }
}

// Topic badge colors
export function getTopicColor(topic: string): string {
  const colors: Record<string, string> = {
    algebra: 'text-blue-400 bg-blue-400/10 border-blue-400/20',
    calculus: 'text-purple-400 bg-purple-400/10 border-purple-400/20',
    probability: 'text-pink-400 bg-pink-400/10 border-pink-400/20',
    'linear_algebra': 'text-cyan-400 bg-cyan-400/10 border-cyan-400/20',
    other: 'text-gray-400 bg-gray-400/10 border-gray-400/20',
  };
  return colors[topic.toLowerCase()] || colors.other;
}

// Truncate text
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

// Debounce function
export function debounce<T extends (...args: unknown[]) => void>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

// Check if text contains LaTeX
export function containsLatex(text: string): boolean {
  return /\$[^$]+\$/.test(text);
}
