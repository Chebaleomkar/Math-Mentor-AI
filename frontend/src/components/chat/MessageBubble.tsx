'use client';

import { Message } from '@/types';
import { MathRenderer } from '@/components/shared/MathRenderer';
import { User, Bot, Play, Pause, Mic } from 'lucide-react';
import { formatTimestamp } from '@/lib/utils';
import { useState, useRef, useEffect } from 'react';

function CustomAudioPlayer({ src }: { src: string }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const audioRef = useRef<HTMLAudioElement>(null);

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const onTimeUpdate = () => {
    if (audioRef.current) {
      const current = audioRef.current.currentTime;
      const total = audioRef.current.duration;
      setCurrentTime(current);
      setProgress((current / total) * 100);
    }
  };

  const onLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const formatTime = (time: number) => {
    const mins = Math.floor(time / 60);
    const secs = Math.floor(time % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex items-center gap-3 bg-background/40 backdrop-blur-md rounded-xl p-3 border border-border/50 shadow-sm group hover:border-primary/30 transition-all w-full max-w-[300px]">
      <button
        onClick={togglePlay}
        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary hover:bg-primary hover:text-primary-foreground transition-all active:scale-95"
      >
        {isPlaying ? <Pause className="h-5 w-5 fill-current" /> : <Play className="h-5 w-5 fill-current ml-1" />}
      </button>

      <div className="flex-1 space-y-1.5">
        <div className="flex justify-between items-center text-[10px] font-bold tracking-tight text-muted-foreground uppercase opacity-80">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
        <div className="relative h-1.5 w-full bg-muted/30 rounded-full overflow-hidden">
          <div
            className="absolute left-0 top-0 h-full bg-primary transition-all duration-100 ease-linear rounded-full"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <audio
        ref={audioRef}
        src={src}
        onTimeUpdate={onTimeUpdate}
        onLoadedMetadata={onLoadedMetadata}
        onEnded={() => setIsPlaying(false)}
        className="hidden"
      />
    </div>
  );
}

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
        className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl shadow-sm ${isUser
          ? 'bg-primary text-primary-foreground'
          : 'bg-secondary text-secondary-foreground border border-border'
          }`}
      >
        {isUser ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
      </div>

      {/* Message Content */}
      <div
        className={`relative max-w-[85%] rounded-2xl px-5 py-3.5 shadow-sm transition-all hover:shadow-md ${isUser
          ? (message.metadata?.audioUrl && !message.content ? 'bg-secondary/30 border border-border/50 text-foreground rounded-tr-none' : 'bg-primary text-primary-foreground rounded-tr-none')
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
            <div className="flex items-center gap-2 mb-2 text-[10px] font-bold uppercase tracking-widest opacity-60">
              <Mic className="h-3 w-3" />
              Voice Note
            </div>
            <CustomAudioPlayer src={message.metadata.audioUrl} />
          </div>
        )}

        {message.content && (
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <MathRenderer content={message.content} />
          </div>
        )}

        {message.metadata?.isCacheHit && (
          <div className="mt-3 flex items-center gap-2 rounded-full bg-primary/10 px-2.5 py-1 w-fit border border-primary/20">
            <span className="h-2 w-2 rounded-full bg-primary animate-pulse"></span>
            <span className="text-[10px] font-bold tracking-wider text-primary uppercase">Instant Memory Hit</span>
          </div>
        )}

        <div
          className={`mt-2 text-[10px] font-medium tracking-wide ${isUser ? 'text-primary-foreground/70' : 'text-muted-foreground'
            }`}
        >
          {formatTimestamp(message.timestamp)}
        </div>
      </div>
    </div>
  );
}
