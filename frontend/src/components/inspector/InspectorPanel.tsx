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
    <div className="flex h-full flex-col rounded-xl border border-border/40 glass glass-dark shadow-2xl">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex h-full flex-col">
        <TabsList className="grid w-full grid-cols-3 border-b border-border/40 bg-secondary/80 p-1">
          <TabsTrigger
            value="history"
            className="flex items-center justify-center gap-1.5 text-xs font-medium text-muted-foreground transition-all data-[state=active]:bg-background data-[state=active]:text-primary data-[state=active]:shadow-sm hover:text-foreground"
          >
            <History className="h-3.5 w-3.5" />
            History
          </TabsTrigger>
          <TabsTrigger
            value="trace"
            className="flex items-center justify-center gap-1.5 text-xs font-medium text-muted-foreground transition-all data-[state=active]:bg-background data-[state=active]:text-primary data-[state=active]:shadow-sm hover:text-foreground"
          >
            <Activity className="h-3.5 w-3.5" />
            Trace
          </TabsTrigger>
          <TabsTrigger
            value="context"
            className="flex items-center justify-center gap-1.5 text-xs font-medium text-muted-foreground transition-all data-[state=active]:bg-background data-[state=active]:text-primary data-[state=active]:shadow-sm hover:text-foreground"
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
