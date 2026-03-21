'use client';

import { useState, useRef, useCallback, KeyboardEvent, ChangeEvent, useEffect } from 'react';
import { Plus, Send, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { LatexPreview } from '@/components/shared/MathRenderer';
import { containsLatex } from '@/lib/utils';
import { AttachmentPanel } from './AttachmentPanel';

interface InputBarProps {
  onSendMessage: (message: string) => void;
  onSendImage: (file: File) => void;
  onSendAudio: (file: File) => void;
  isLoading?: boolean;
  extractedText?: string | null;
  extractionSource?: 'image' | 'audio' | null;
}

export function InputBar({
  onSendMessage,
  onSendImage,
  onSendAudio,
  isLoading,
  extractedText,
  extractionSource,
}: InputBarProps) {
  const [message, setMessage] = useState('');
  const [showAttachments, setShowAttachments] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const autoSendTimerRef = useRef<NodeJS.Timeout | null>(null);

  const clearAutoSendTimer = useCallback(() => {
    if (autoSendTimerRef.current) {
      clearTimeout(autoSendTimerRef.current);
      autoSendTimerRef.current = null;
    }
  }, []);

  // Auto-resize textarea
  const adjustTextareaHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
    }
  }, []);

  // Sync extracted text from props to local message state
  useEffect(() => {
    if (extractedText) {
      setMessage(extractedText);
      adjustTextareaHeight();

      // If it's from audio, start an auto-send timer
      if (extractionSource === 'audio') {
        clearAutoSendTimer();
        autoSendTimerRef.current = setTimeout(() => {
          if (!isLoading && extractedText) {
            onSendMessage(extractedText);
            setMessage('');
            setShowPreview(false);
            clearAutoSendTimer();
          }
        }, 10000);
      }
    }
    return () => {
      clearAutoSendTimer();
    };
  }, [extractedText, extractionSource, adjustTextareaHeight, onSendMessage, isLoading, clearAutoSendTimer]);

  // Focus textarea on mount
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);

  const handleInputChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    clearAutoSendTimer();
    const value = e.target.value;
    setMessage(value);
    setShowPreview(containsLatex(value));
    adjustTextareaHeight();
  };

  const handleSend = () => {
    if (!message.trim() || isLoading) return;

    clearAutoSendTimer();
    onSendMessage(message.trim());
    setMessage('');
    setShowPreview(false);

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleImageUpload = (file: File) => {
    onSendImage(file);
    setShowAttachments(false);
  };

  const handleAudioUpload = (file: File) => {
    onSendAudio(file);
    setShowAttachments(false);
  };

  return (
    <div className="relative">
      {/* Attachment Panel */}
      {showAttachments && (
        <AttachmentPanel
          onImageSelect={handleImageUpload}
          onAudioSelect={handleAudioUpload}
          onClose={() => setShowAttachments(false)}
        />
      )}

      {/* LaTeX Preview */}
      <LatexPreview text={message} visible={showPreview} />

      {/* Input Bar */}
      <div className="flex items-end gap-2 rounded-[24px] border border-border/50 bg-background/40 p-4 shadow-xl backdrop-blur-xl transition-all focus-within:border-primary/50 focus-within:shadow-2xl focus-within:shadow-primary/10">
        {/* Attachment Button */}
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className={`h-10 w-10 shrink-0 rounded-xl border border-border bg-secondary/50 text-muted-foreground transition-all hover:border-primary/50 hover:text-primary hover:scale-105 active:scale-95 ${
            showAttachments ? 'border-primary text-primary bg-primary/10' : ''
          }`}
          onClick={() => setShowAttachments(!showAttachments)}
        >
          {showAttachments ? <X className="h-5 w-5" /> : <Plus className="h-5 w-5" />}
        </Button>
      
        {/* Text Input */}
        <Textarea
          ref={textareaRef}
          value={message}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          autoFocus
          placeholder={
            extractedText
              ? 'Edit the extracted text if needed...'
              : 'Type a math problem...'
          }
          className="min-h-[44px] max-h-[150px] flex-1 resize-none border-0 bg-transparent px-2 py-2.5 text-base text-foreground placeholder:text-muted-foreground/60 focus-visible:ring-0 focus-visible:ring-offset-0"
          rows={1}
          disabled={isLoading}
        />
      
        {/* Send Button */}
        <Button
          type="button"
          size="icon"
          className="h-10 w-10 shrink-0 rounded-xl bg-primary text-primary-foreground shadow-lg shadow-primary/20 transition-all hover:bg-primary/90 hover:scale-105 active:scale-95 disabled:opacity-50"
          onClick={handleSend}
          disabled={!message.trim() || isLoading}
        >
          <Send className="h-5 w-5" />
        </Button>
      </div>
    </div>
  );
}
