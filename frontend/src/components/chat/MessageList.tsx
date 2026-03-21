'use client';

import { useRef, useEffect } from 'react';
import { Message } from '@/types';
import { MessageBubble } from './MessageBubble';
import { Sigma, Bot } from 'lucide-react';

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
  onSelectTopic?: (problem: string) => void;
}

export function MessageList({ messages, isLoading, onSelectTopic }: MessageListProps) {
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

        <div className="flex flex-wrap justify-center gap-3 max-w-2xl px-4">
          {[
            { label: 'Algebra', problem: 'Solve for x: 3x^2 - 7x + 2 = 0' },
            { label: 'Calculus', problem: 'Calculate the integral of sin(x) * e^x dx' },
            { label: 'Trigonometry', problem: 'Verify the identity sin(2x) = 2sin(x)cos(x)' },
            { label: 'Coordinate Geometry', problem: 'Find the intersection point of y=2x+1 and y=-x+4' }
          ].map((topic) => (
            <button
              key={topic.label}
              onClick={() => onSelectTopic?.(topic.problem)}
              className="group relative flex items-center gap-2 rounded-xl border border-border bg-secondary/50 px-4 py-2.5 text-sm font-semibold text-muted-foreground transition-all hover:border-primary/50 hover:bg-primary/5 hover:text-primary hover:scale-105 active:scale-95 shadow-sm overflow-hidden"
            >
              <div className="absolute inset-x-0 bottom-0 h-0.5 w-full scale-x-0 bg-primary transition-transform group-hover:scale-x-100" />
              {topic.label}
            </button>
          ))}
          
          {/* Try HITL Button */}
          <div className="group relative">
            <button
              onClick={() => onSelectTopic?.('Prove the uniqueness of the solution to the Navier-Stokes equations in 3D.')}
              className="flex items-center gap-2 rounded-xl border border-primary/30 bg-primary/5 px-4 py-2.5 text-sm font-bold text-primary transition-all hover:border-primary hover:bg-primary hover:text-primary-foreground hover:scale-105 active:scale-95 shadow-md shadow-primary/5"
            >
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
              </span>
              Try HITL Demo
            </button>
            
            {/* Tooltip */}
            <div className="invisible absolute -top-12 left-1/2 -translate-x-1/2 scale-95 whitespace-nowrap rounded-lg bg-foreground px-3 py-1.5 text-[10px] font-bold text-background opacity-0 transition-all group-hover:visible group-hover:scale-100 group-hover:opacity-100 z-50 shadow-xl">
              Preview Human-in-the-Loop review for complex problems
              <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 h-2 w-2 rotate-45 bg-foreground" />
            </div>
          </div>
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
