'use client';

import { BookOpen } from 'lucide-react';
import { RetrievedSource } from '@/types';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { ChevronDown } from 'lucide-react';

interface ContextTabProps {
  sources?: RetrievedSource[];
}

export function ContextTab({ sources }: ContextTabProps) {
  if (!sources || sources.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-4 text-center">
        <BookOpen className="mb-2 h-8 w-8 text-[#2C2C35]" />
        <p className="text-sm text-[#55524F]">No context retrieved</p>
        <p className="text-xs text-[#55524F]/70">RAG sources will appear here</p>
      </div>
    );
  }

  return (
    <div className="space-y-3 p-3">
      <div className="mb-2 text-xs text-[#9B9693]">
        Retrieved {sources.length} relevant source{sources.length !== 1 ? 's' : ''}
      </div>

      {sources.map((source, index) => (
        <Collapsible key={index}>
          <CollapsibleTrigger className="w-full rounded-lg border border-[#2C2C35] bg-[#15151A] p-3 text-left transition-all hover:border-[#6366F1]/50 hover:bg-[#1D1D23]">
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1">
                <div className="mb-1 flex items-center gap-2">
                  <span className="text-xs font-medium text-[#EDEAE4]">{source.title}</span>
                  <span className="rounded bg-[#6366F1]/10 px-1.5 py-0.5 text-[10px] text-[#6366F1]">
                    {source.score.toFixed(2)}
                  </span>
                </div>
                <div className="text-[10px] text-[#55524F]">
                  {source.source} {source.section && `· ${source.section}`}
                </div>
              </div>
              <ChevronDown className="mt-0.5 h-4 w-4 shrink-0 text-[#55524F]" />
            </div>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <div className="mt-1 rounded-b-lg border-x border-b border-[#2C2C35] bg-[#0E0E11] p-3">
              <div className="text-[10px] uppercase text-[#55524F] mb-1">Snippet</div>
              <blockquote className="border-l-2 border-[#6366F1]/30 pl-3 text-xs italic text-[#9B9693]">
                {source.snippet}...
              </blockquote>
            </div>
          </CollapsibleContent>
        </Collapsible>
      ))}
    </div>
  );
}
