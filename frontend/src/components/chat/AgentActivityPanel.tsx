'use client';

import { AgentActivity } from '@/types';
import { Check, Loader2, AlertCircle, Cpu, Database, Wrench, FileText, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

const AGENT_CONFIG: Record<string, { icon: React.ReactNode; label: string; color: string }> = {
  parser: { icon: <FileText className="h-3.5 w-3.5" />, label: 'Parsing problem', color: 'text-blue-400 bg-blue-500/20' },
  memory_lookup: { icon: <Database className="h-3.5 w-3.5" />, label: 'Searching memory', color: 'text-cyan-400 bg-cyan-500/20' },
  rag: { icon: <Database className="h-3.5 w-3.5" />, label: 'Retrieving context', color: 'text-purple-400 bg-purple-500/20' },
  solver: { icon: <Wrench className="h-3.5 w-3.5" />, label: 'Computing solution', color: 'text-amber-400 bg-amber-500/20' },
  verifier: { icon: <CheckCircle2 className="h-3.5 w-3.5" />, label: 'Verifying answer', color: 'text-green-400 bg-green-500/20' },
  explainer: { icon: <Cpu className="h-3.5 w-3.5" />, label: 'Generating explanation', color: 'text-rose-400 bg-rose-500/20' },
};

const ALL_AGENTS = ['parser', 'memory_lookup', 'rag', 'solver', 'verifier', 'explainer'];

interface AgentActivityPanelProps {
  activity: AgentActivity[];
  isLoading?: boolean;
}

export function AgentActivityPanel({ activity, isLoading }: AgentActivityPanelProps) {
  const getActivityStatus = (agent: string): AgentActivity['status'] => {
    const found = activity.find((a) => a.agent === agent);
    return found?.status || 'pending';
  };

  const completedCount = activity.filter((a) => a.status === 'completed').length;

  return (
    <div className="mt-4 rounded-xl border border-border/40 bg-card/50 p-4 backdrop-blur-sm">
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Cpu className="h-4 w-4 text-primary" />
          <span className="text-sm font-medium text-foreground">Agent Activity</span>
        </div>
        <span className="text-xs text-muted-foreground">
          {completedCount}/{ALL_AGENTS.length} completed
        </span>
      </div>

      <div className="space-y-2">
        {ALL_AGENTS.map((agent, index) => {
          const status = getActivityStatus(agent);
          const config = AGENT_CONFIG[agent] || { icon: <Cpu className="h-3.5 w-3.5" />, label: agent, color: 'text-gray-400 bg-gray-500/20' };
          const isRunning = status === 'running';

          return (
            <div
              key={agent}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 transition-all',
                status === 'pending' && 'opacity-40',
                isRunning && 'animate-pulse bg-primary/5'
              )}
            >
              <div
                className={cn(
                  'flex h-7 w-7 items-center justify-center rounded-full',
                  config.color,
                  status === 'running' && 'animate-spin'
                )}
              >
                {status === 'completed' ? (
                  <Check className="h-3.5 w-3.5" />
                ) : status === 'running' ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : status === 'error' ? (
                  <AlertCircle className="h-3.5 w-3.5" />
                ) : (
                  config.icon
                )}
              </div>

              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-foreground">{config.label}</span>
                  <span className="text-[10px] uppercase text-muted-foreground">{agent}</span>
                </div>
                {isRunning && (
                  <div className="mt-0.5 flex items-center gap-1">
                    <div className="flex space-x-0.5">
                      <div className="h-1 w-1 animate-bounce rounded-full bg-primary" style={{ animationDelay: '0ms' }} />
                      <div className="h-1 w-1 animate-bounce rounded-full bg-primary" style={{ animationDelay: '150ms' }} />
                      <div className="h-1 w-1 animate-bounce rounded-full bg-primary" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                )}
              </div>

              {status === 'completed' && (
                <Check className="h-4 w-4 text-green-400" />
              )}
            </div>
          );
        })}
      </div>

      {/* Progress bar */}
      <div className="mt-3 h-1 w-full overflow-hidden rounded-full bg-secondary">
        <div
          className="h-full bg-primary transition-all duration-500 ease-out"
          style={{ width: `${(completedCount / ALL_AGENTS.length) * 100}%` }}
        />
      </div>
    </div>
  );
}
