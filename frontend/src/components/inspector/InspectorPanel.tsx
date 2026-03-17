'use client';

import { useState } from 'react';
import { History, Activity, BookOpen } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { HistoryTab } from './HistoryTab';
import { AgentTraceTab } from './AgentTraceTab';
import { ContextTab } from './ContextTab';
import { SolveResponse, MemorySummary } from '@/types';

interface InspectorPanelProps {
  solution?: SolveResponse | null;
  isLoading?: boolean;
  onSelectHistoryItem?: (item: MemorySummary) => void;
}

export function InspectorPanel({
  solution,
  isLoading,
  onSelectHistoryItem,
}: InspectorPanelProps) {
  const [activeTab, setActiveTab] = useState('history');

  return (
    <div className="flex h-full flex-col rounded-xl border border-[#2C2C35] bg-[#15151A]/75 backdrop-blur-md shadow-[0_8px_32px_rgba(0,0,0,0.4)]">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex h-full flex-col">
        <TabsList className="grid w-full grid-cols-3 border-b border-[#2C2C35] bg-[#1D1D23]/90 p-1">
          <TabsTrigger
            value="history"
            className="flex items-center justify-center gap-1.5 text-xs text-[#9B9693] transition-colors data-[state=active]:bg-[#6366F1]/10 data-[state=active]:text-[#6366F1] hover:text-[#EDEAE4]"
          >
            <History className="h-3.5 w-3.5" />
            History
          </TabsTrigger>
          <TabsTrigger
            value="trace"
            className="flex items-center justify-center gap-1.5 text-xs text-[#9B9693] transition-colors data-[state=active]:bg-[#6366F1]/10 data-[state=active]:text-[#6366F1] hover:text-[#EDEAE4]"
          >
            <Activity className="h-3.5 w-3.5" />
            Trace
          </TabsTrigger>
          <TabsTrigger
            value="context"
            className="flex items-center justify-center gap-1.5 text-xs text-[#9B9693] transition-colors data-[state=active]:bg-[#6366F1]/10 data-[state=active]:text-[#6366F1] hover:text-[#EDEAE4]"
          >
            <BookOpen className="h-3.5 w-3.5" />
            Context
          </TabsTrigger>
        </TabsList>

        <div className="flex-1 overflow-hidden">
          <TabsContent value="history" className="mt-0 h-full">
            <HistoryTab onSelectProblem={onSelectHistoryItem} />
          </TabsContent>

          <TabsContent value="trace" className="mt-0 h-full overflow-y-auto">
            <AgentTraceTab solution={solution} isLoading={isLoading} />
          </TabsContent>

          <TabsContent value="context" className="mt-0 h-full overflow-y-auto">
            <ContextTab sources={solution?.retrieved_sources} />
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}
