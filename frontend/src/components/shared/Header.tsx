'use client';

import { Sigma } from 'lucide-react';

export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-[#2C2C35] bg-[#15151A]/95 backdrop-blur-sm">
      <div className="flex h-[60px] items-center gap-3 px-5">
        <div className="flex h-[34px] w-[34px] items-center justify-center rounded-md border border-[#6366F1] bg-[#1E1E3F] shadow-[0_0_14px_rgba(99,102,241,0.12)]">
          <Sigma className="h-5 w-5 text-[#6366F1]" />
        </div>
        <div className="flex flex-col">
          <span className="font-mono text-sm font-medium tracking-wider text-[#6366F1]">
            MATH MENTOR AI
          </span>
          <span className="text-[11px] text-[#55524F]">
            JEE-level · RAG + Multi-Agent AI
          </span>
        </div>
      </div>
    </header>
  );
}
