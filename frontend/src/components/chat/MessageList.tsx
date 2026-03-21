'use client';

import { useRef, useEffect } from 'react';
import { Message } from '@/types';
import { MessageBubble } from './MessageBubble';
import { Sigma, Bot } from 'lucide-react';

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
      <div className="flex h-full flex-col items-center justify-center px-6 text-center animate-in fade-in duration-700">
        <div className="mb-6 relative">
          <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-linear-to-br from-primary to-primary/60 shadow-xl shadow-primary/20">
            <Sigma className="h-10 w-10 text-white" />
          </div>
          <div className="absolute -bottom-2 -right-2 h-8 w-8 rounded-xl glass glass-dark flex items-center justify-center shadow-lg border border-border/50">
            <Bot className="h-4 w-4 text-primary" />
          </div>
        </div>
        <h2 className="mb-3 text-2xl font-bold tracking-tight text-foreground">
          Welcome to <span className="text-primary">MathMentor</span> AI
        </h2>
        <p className="mb-8 max-w-md text-base leading-relaxed text-muted-foreground">
          Your specialized AI for mastering JEE-level mathematics. How can I help you excel today?
        </p>

        <div className="flex flex-wrap justify-center gap-3 max-w-lg">
          {['Algebra', 'Calculus', 'Trigonometry', 'Coordinate Geometry'].map((topic) => (
            <button
              key={topic}
              className="rounded-xl border border-border bg-secondary/50 px-4 py-2 text-sm font-medium text-muted-foreground transition-all hover:border-primary/50 hover:bg-primary/5 hover:text-primary hover:scale-105 active:scale-95 shadow-sm"
            >
              {topic}
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="flex h-full flex-col overflow-y-auto px-6 py-8 scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent"
    >
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {isLoading && (
        <div className="flex items-center gap-3 px-4 py-3 animate-pulse">
          <div className="flex space-x-1.5">
            <div className="h-2.5 w-2.5 rounded-full bg-primary/40 animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="h-2.5 w-2.5 rounded-full bg-primary/60 animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="h-2.5 w-2.5 rounded-full bg-primary/80 animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <span className="text-sm font-medium text-muted-foreground">Formulating solution...</span>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
