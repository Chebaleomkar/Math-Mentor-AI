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
}

export function InputBar({
  onSendMessage,
  onSendImage,
  onSendAudio,
  isLoading,
  extractedText,
}: InputBarProps) {
  const [message, setMessage] = useState('');
  const [showAttachments, setShowAttachments] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

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
    }
  }, [extractedText, adjustTextareaHeight]);

  // Focus textarea on mount
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);

  const handleInputChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setMessage(value);
    setShowPreview(containsLatex(value));
    adjustTextareaHeight();
  };

  const handleSend = () => {
    if (!message.trim() || isLoading) return;

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
      <div className="flex items-end gap-2 rounded-[24px] border border-[#2C2C35] bg-[#15151A]/80 p-4 shadow-[0_8px_32px_rgba(0,0,0,0.4)] backdrop-blur-md transition-all focus-within:border-[#6366F1] focus-within:shadow-[0_0_20px_rgba(99,102,241,0.15)]">
        {/* Attachment Button */}
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className={`h-10 w-10 shrink-0 rounded-xl border border-[#2C2C35] bg-[#1D1D23] text-[#9B9693] transition-all hover:border-[#6366F1] hover:text-[#6366F1] hover:scale-110 active:scale-90 ${
            showAttachments ? 'border-[#6366F1] text-[#6366F1]' : ''
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
          className="min-h-[44px] max-h-[150px] flex-1 resize-none border-0 bg-transparent px-2 py-2.5 text-base text-[#EDEAE4] placeholder:text-[#55524F] focus-visible:ring-0 focus-visible:ring-offset-0"
          rows={1}
          disabled={isLoading}
        />
      
        {/* Send Button */}
        <Button
          type="button"
          size="icon"
          className="h-10 w-10 shrink-0 rounded-xl bg-[#6366F1] text-[#0E0E11] shadow-[0_0_15px_rgba(99,102,241,0.3)] transition-all hover:bg-[#818CF8] hover:scale-110 active:scale-90 disabled:opacity-50"
          onClick={handleSend}
          disabled={!message.trim() || isLoading}
        >
          <Send className="h-5 w-5" />
        </Button>
      </div>
    </div>
  );
}
