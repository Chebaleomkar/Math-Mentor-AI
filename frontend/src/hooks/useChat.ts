'use client';

import { useState, useCallback, useRef } from 'react';
import {
  Message,
  SolveRequest,
  SolveResponse,
  ExtractionResponse,
  TranscriptionResponse,
  InputMode,
  MemorySummary,
} from '@/types';
import {
  solveProblem,
  extractImageBase64,
  extractAudioBase64,
  submitHITL,
  submitFeedback,
  listMemory,
  fileToBase64,
} from '@/lib/api';
import { generateId } from '@/lib/utils';

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  currentMemoryId: string | null;
  extractedText: string | null;
  needsReview: boolean;
  extractionConfidence: 'high' | 'medium' | 'low' | null;
  showHitl: boolean;
  showFeedback: boolean;
  currentSolution: SolveResponse | null;
  history: MemorySummary[];
}

export function useChat() {
  const [state, setState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    currentMemoryId: null,
    extractedText: null,
    needsReview: false,
    extractionConfidence: null,
    showHitl: false,
    showFeedback: false,
    currentSolution: null,
    history: [],
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  // Add a message to the chat
  const addMessage = useCallback((message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage: Message = {
      ...message,
      id: generateId(),
      timestamp: new Date(),
    };
    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, newMessage],
    }));
    return newMessage.id;
  }, []);

  // Update a message
  const updateMessage = useCallback((id: string, updates: Partial<Message>) => {
    setState((prev) => ({
      ...prev,
      messages: prev.messages.map((m) => (m.id === id ? { ...m, ...updates } : m)),
    }));
  }, []);

  // Send text message
  const sendTextMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return;

      // Add user message
      addMessage({ role: 'user', content });

      setState((prev) => ({
        ...prev,
        isLoading: true,
        showHitl: false,
        showFeedback: false,
        extractedText: null,
        needsReview: false,
      }));

      try {
        // Add loading message
        const loadingId = addMessage({
          role: 'assistant',
          content: '⏳ Solving your problem...',
        });

        const request: SolveRequest = {
          input_type: 'text',
          content: content.trim(),
        };

        const response = await solveProblem(request);

        // Remove loading message
        setState((prev) => ({
          ...prev,
          messages: prev.messages.filter((m) => m.id !== loadingId),
        }));

        // Add solution message
        addMessage({
          role: 'assistant',
          content: formatSolution(response),
          metadata: { isCacheHit: response.is_cache_hit }
        });

        setState((prev) => ({
          ...prev,
          isLoading: false,
          currentMemoryId: response.memory_id,
          currentSolution: response,
          showHitl: response.hitl_required && response.verifier_result.confidence < 0.85,
          showFeedback: !(response.hitl_required && response.verifier_result.confidence < 0.85),
        }));
      } catch (error) {
        setState((prev) => ({ ...prev, isLoading: false }));
        addMessage({
          role: 'assistant',
          content: `❌ Error: ${error instanceof Error ? error.message : 'Failed to solve problem'}`,
        });
      }
    },
    [addMessage]
  );

  // Process image for extraction and showcase
  const sendImageMessage = useCallback(
    async (file: File) => {
      // Create local preview URL
      const imageUrl = URL.createObjectURL(file);
      
      // Add user message with image preview
      addMessage({
        role: 'user',
        content: '📷 [Image uploaded]',
        metadata: { imageUrl }
      });

      setState((prev) => ({ ...prev, isLoading: true, showHitl: false, showFeedback: false }));

      try {
        // Convert to base64 and extract
        const base64 = await fileToBase64(file);
        const extraction: ExtractionResponse = await extractImageBase64(
          base64,
          file.type
        );

        setState((prev) => ({
          ...prev,
          isLoading: false,
          extractedText: extraction.extracted_text,
          needsReview: extraction.needs_review,
          extractionConfidence: extraction.confidence,
        }));

        // Notification for the user
        addMessage({
          role: 'system',
          content: '✅ Image processed. Text has been added to your input box for review.'
        });

      } catch (error) {
        setState((prev) => ({ ...prev, isLoading: false }));
        addMessage({
          role: 'assistant',
          content: `❌ Error: ${error instanceof Error ? error.message : 'Failed to process image'}`,
        });
      }
    },
    [addMessage]
  );

  // Process audio for transcription and showcase
  const sendAudioMessage = useCallback(
    async (file: File) => {
      // Create local preview URL
      const audioUrl = URL.createObjectURL(file);

      // Add user message with audio preview
      addMessage({
        role: 'user',
        content: `🎤 [Audio capture]`,
        metadata: { audioUrl }
      });

      setState((prev) => ({ ...prev, isLoading: true, showHitl: false, showFeedback: false }));

      try {
        // Convert to base64 and extract
        const base64 = await fileToBase64(file);
        const transcription: TranscriptionResponse = await extractAudioBase64(
          base64,
          file.name
        );

        setState((prev) => ({
          ...prev,
          isLoading: false,
          extractedText: transcription.cleaned_text,
          needsReview: transcription.needs_review,
          extractionConfidence: 'medium',
        }));

        // Notification for the user
        addMessage({
          role: 'system',
          content: '✅ Audio transcribed. Text has been added to your input box for review.'
        });

      } catch (error) {
        setState((prev) => ({ ...prev, isLoading: false }));
        addMessage({
          role: 'assistant',
          content: `❌ Error: ${error instanceof Error ? error.message : 'Failed to process audio'}`,
        });
      }
    },
    [addMessage]
  );

  // Submit HITL feedback
  const submitHITLFeedback = useCallback(
    async (approved: boolean, editedAnswer?: string) => {
      if (!state.currentMemoryId) return;

      try {
        const response = await submitHITL(state.currentMemoryId, {
          approved,
          edited_answer: editedAnswer,
          comment: 'Reviewed via UI',
        });

        addMessage({
          role: 'system',
          content: approved
            ? `✅ Approved — Final answer: ${response.final_answer}`
            : `✏️ Corrected — Final answer: ${response.final_answer}`,
        });

        setState((prev) => ({ ...prev, showHitl: false, showFeedback: true }));
      } catch (error) {
        addMessage({
          role: 'system',
          content: `❌ Failed to submit feedback: ${error instanceof Error ? error.message : 'Unknown error'}`,
        });
      }
    },
    [state.currentMemoryId, addMessage]
  );

  // Submit user feedback
  const submitUserFeedback = useCallback(
    async (isCorrect: boolean, comment?: string) => {
      if (!state.currentMemoryId) return;

      try {
        await submitFeedback(state.currentMemoryId, {
          feedback: isCorrect ? 'correct' : 'incorrect',
          comment,
        });

        addMessage({
          role: 'system',
          content: isCorrect ? '✅ Thanks! Feedback saved.' : '❌ Noted — will improve accuracy.',
        });

        setState((prev) => ({ ...prev, showFeedback: false }));
      } catch (error) {
        addMessage({
          role: 'system',
          content: `❌ Failed to save feedback: ${error instanceof Error ? error.message : 'Unknown error'}`,
        });
      }
    },
    [state.currentMemoryId, addMessage]
  );

  // Load history
  const loadHistory = useCallback(async () => {
    try {
      const history = await listMemory(10);
      setState((prev) => ({ ...prev, history }));
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  }, []);

  // Clear chat
  const clearChat = useCallback(() => {
    setState({
      messages: [],
      isLoading: false,
      currentMemoryId: null,
      extractedText: null,
      needsReview: false,
      extractionConfidence: null,
      showHitl: false,
      showFeedback: false,
      currentSolution: null,
      history: state.history,
    });
  }, [state.history]);

  return {
    ...state,
    addMessage,
    updateMessage,
    sendTextMessage,
    sendImageMessage,
    sendAudioMessage,
    submitHITLFeedback,
    submitUserFeedback,
    loadHistory,
    clearChat,
  };
}

// Helper to format solution for display
function formatSolution(response: SolveResponse): string {
  const { explanation, verifier_result, solver_result } = response;

  let content = '';

  // Explanation
  if (explanation.explanation) {
    content += explanation.explanation;
  } else {
    content += solver_result.solution;
  }

  // Final answer
  content += `\n\n---\n\n**Final Answer:** ${explanation.final_answer || solver_result.final_answer}`;

  // Confidence badge
  const confidence = explanation.confidence || verifier_result.confidence;
  const confidenceLevel = confidence >= 0.85 ? 'High' : confidence >= 0.65 ? 'Medium' : 'Low';
  const confidenceIcon = confidence >= 0.85 ? '🟢' : confidence >= 0.65 ? '🟡' : '🔴';
  content += `\n\n${confidenceIcon} **${confidenceLevel} confidence** (${Math.round(confidence * 100)}%)`;

  // Issues if any
  if (verifier_result.issues && verifier_result.issues.length > 0) {
    content += `\n\n⚠️ **Issues:** ${verifier_result.issues.join(', ')}`;
  }

  return content;
}
