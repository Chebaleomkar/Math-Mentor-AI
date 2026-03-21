'use client';

import { Sigma, Sparkles } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';

export function Header() {
  return (
    <header className="sticky top-0 z-50 glass glass-dark border-b">
      <div className="flex h-[64px] items-center justify-between px-6">
        <div className="flex items-center gap-4">
          <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-linear-to-br from-primary to-primary/60 shadow-lg shadow-primary/20 transition-transform hover:scale-105">
            <Sigma className="h-6 w-6 text-white" />
            <Sparkles className="absolute -top-1 -right-1 h-4 w-4 text-primary animate-pulse" />
          </div>
          <div className="flex flex-col">
            <span className="text-lg font-bold tracking-tight text-foreground sm:text-xl">
              Math<span className="text-primary">Mentor</span> AI
            </span>
            <span className="hidden text-[11px] font-medium text-muted-foreground md:inline-block">
              A specialized AI, specially trained to solve complex mathematics with precision
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
