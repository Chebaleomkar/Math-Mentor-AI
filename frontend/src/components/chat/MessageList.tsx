'use client';

import { useRef, useEffect } from 'react';
import { Message } from '@/types';
import { MessageBubble } from './MessageBubble';
import { Sigma } from 'lucide-react';

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center px-6 text-center">
        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-[#1E1E3F]">
          <Sigma className="h-8 w-8 text-[#6366F1]" />
        </div>
        <h2 className="mb-2 text-lg font-medium text-[#EDEAE4]">
          Welcome to Math Mentor AI
        </h2>
        <p className="mb-6 max-w-md text-sm text-[#9B9693]">
          Ask a JEE-level math problem. Type, upload an image, or record audio.
        </p>

        <div className="flex flex-wrap justify-center gap-2">
          {['algebra', 'calculus', 'probability', 'linear algebra'].map((topic) => (
            <span
              key={topic}
              className="rounded-full border border-[#2C2C35] bg-[#15151A] px-3 py-1 text-xs text-[#55524F]"
            >
              {topic}
            </span>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="flex h-full flex-col overflow-y-auto px-4 py-6 scrollbar-thin scrollbar-thumb-[#2C2C35] scrollbar-track-transparent"
    >
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {isLoading && (
        <div className="flex items-center gap-2 px-4 py-2">
          <div className="flex space-x-1">
            <div className="h-2 w-2 animate-bounce rounded-full bg-[#6366F1]" style={{ animationDelay: '0ms' }} />
            <div className="h-2 w-2 animate-bounce rounded-full bg-[#6366F1]" style={{ animationDelay: '150ms' }} />
            <div className="h-2 w-2 animate-bounce rounded-full bg-[#6366F1]" style={{ animationDelay: '300ms' }} />
          </div>
          <span className="text-xs text-[#9B9693]">Solving...</span>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
