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
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'} mb-4 animate-in fade-in slide-in-from-bottom-2 duration-300`}
    >
      {/* Avatar */}
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
          isUser
            ? 'bg-[#6366F1] text-white'
            : 'bg-[#1D1D23] border border-[#2C2C35] text-[#9B9693]'
        }`}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      {/* Message Content */}
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-[#6366F1] text-white'
            : 'bg-[#1D1D23] border border-[#2C2C35] text-[#EDEAE4]'
        }`}
      >
        {message.metadata?.imageUrl && (
          <div className="mb-3 overflow-hidden rounded-lg border border-white/10">
            <img 
              src={message.metadata.imageUrl} 
              alt="Uploaded" 
              className="max-h-60 w-full object-contain"
            />
          </div>
        )}

        {message.metadata?.audioUrl && (
          <div className="mb-3">
            <audio 
              src={message.metadata.audioUrl} 
              controls 
              className="h-8 w-full accent-[#6366F1]"
            />
          </div>
        )}

        <MathRenderer content={message.content} />
        <div
          className={`mt-1 text-[10px] ${
            isUser ? 'text-white/60' : 'text-[#55524F]'
          }`}
        >
          {formatTimestamp(message.timestamp)}
        </div>
      </div>
    </div>
  );
}
