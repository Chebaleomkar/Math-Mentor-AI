// API Client for Math Mentor AI Backend

import {
  SolveRequest,
  SolveResponse,
  ExtractionResponse,
  TranscriptionResponse,
  HITLResponse,
  FeedbackRequest,
  MemorySummary,
  MemoryRecord,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Helper for API calls
async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

// Solve API
export async function solveProblem(request: SolveRequest): Promise<SolveResponse> {
  return fetchApi<SolveResponse>('/solve', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

// Image Extraction API
export async function extractImage(file: File): Promise<ExtractionResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/extract/image`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to extract image' }));
    throw new Error(error.detail || 'Failed to extract image');
  }

  return response.json();
}

export async function extractImageBase64(
  base64Data: string,
  mimeType: string = 'image/jpeg'
): Promise<ExtractionResponse> {
  return fetchApi<ExtractionResponse>('/extract/image/base64', {
    method: 'POST',
    body: JSON.stringify({
      image_data: base64Data,
      mime_type: mimeType,
    }),
  });
}

// Audio Extraction API
export async function extractAudio(
  file: File,
  language: string = 'en'
): Promise<TranscriptionResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('language', language);

  const response = await fetch(`${API_BASE_URL}/extract/audio`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to transcribe audio' }));
    throw new Error(error.detail || 'Failed to transcribe audio');
  }

  return response.json();
}

export async function extractAudioBase64(
  base64Data: string,
  filename: string = 'audio.wav',
  language: string = 'en'
): Promise<TranscriptionResponse> {
  return fetchApi<TranscriptionResponse>('/extract/audio/base64', {
    method: 'POST',
    body: JSON.stringify({
      audio_data: base64Data,
      filename,
      language,
    }),
  });
}

// HITL API
export async function submitHITL(
  memoryId: string,
  response: HITLResponse
): Promise<{ memory_id: string; final_answer: string }> {
  return fetchApi<{ memory_id: string; final_answer: string }>(`/hitl/${memoryId}`, {
    method: 'POST',
    body: JSON.stringify(response),
  });
}

// Feedback API
export async function submitFeedback(
  memoryId: string,
  feedback: FeedbackRequest
): Promise<{ status: string }> {
  return fetchApi<{ status: string }>(`/feedback/${memoryId}`, {
    method: 'POST',
    body: JSON.stringify(feedback),
  });
}

// Memory API
export async function listMemory(limit: number = 20): Promise<MemorySummary[]> {
  return fetchApi<MemorySummary[]>(`/memory?limit=${limit}`);
}

export async function getMemoryRecord(memoryId: string): Promise<MemoryRecord> {
  return fetchApi<MemoryRecord>(`/memory/${memoryId}`);
}

// Health Check
export async function checkHealth(): Promise<{
  status: string;
  knowledge_base_ready: boolean;
}> {
  return fetchApi<{ status: string; knowledge_base_ready: boolean }>('/health');
}

// File to Base64 helper
export function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result as string;
      // Remove data URL prefix if present
      const base64Data = base64.split(',')[1] || base64;
      resolve(base64Data);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}
