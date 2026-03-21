'use client';

import { Message } from '@/types';
import { MathRenderer } from '@/components/shared/MathRenderer';
import { User, Bot } from 'lucide-react';
import { formatTimestamp } from '@/lib/utils';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  if (isSystem) {
    return (
      <div className="flex justify-center py-2">
        <div className="rounded-full bg-[#1D1D23] px-4 py-1.5 text-xs text-[#9B9693]">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'} mb-6 animate-in fade-in slide-in-from-bottom-2 duration-300`}
    >
      {/* Avatar */}
      <div
        className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl shadow-sm ${
          isUser
            ? 'bg-primary text-primary-foreground'
            : 'bg-secondary text-secondary-foreground border border-border'
        }`}
      >
        {isUser ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
      </div>

      {/* Message Content */}
      <div
        className={`relative max-w-[85%] rounded-2xl px-5 py-3.5 shadow-sm transition-all hover:shadow-md ${
          isUser
            ? 'bg-primary text-primary-foreground rounded-tr-none'
            : 'glass glass-dark text-foreground rounded-tl-none border'
        }`}
      >
        {message.metadata?.imageUrl && (
          <div className="mb-4 overflow-hidden rounded-xl border border-border/50 bg-background/20 group">
            <img 
              src={message.metadata.imageUrl} 
              alt="Uploaded" 
              className="max-h-80 w-full object-contain transition-transform group-hover:scale-[1.02]"
            />
          </div>
        )}

        {message.metadata?.audioUrl && (
          <div className="mb-4">
            <audio 
              src={message.metadata.audioUrl} 
              controls 
              className="h-10 w-full accent-primary"
            />
          </div>
        )}

        <div className="prose prose-sm dark:prose-invert max-w-none">
          <MathRenderer content={message.content} />
        </div>
        
        {message.metadata?.isCacheHit && (
          <div className="mt-3 flex items-center gap-2 rounded-full bg-primary/10 px-2.5 py-1 w-fit border border-primary/20">
            <span className="h-2 w-2 rounded-full bg-primary animate-pulse"></span>
            <span className="text-[10px] font-bold tracking-wider text-primary uppercase">Instant Memory Hit</span>
          </div>
        )}

        <div
          className={`mt-2 text-[10px] font-medium tracking-wide ${
            isUser ? 'text-primary-foreground/70' : 'text-muted-foreground'
          }`}
        >
          {formatTimestamp(message.timestamp)}
        </div>
      </div>
    </div>
  );
}
