'use client';

import { Check, Loader2, AlertCircle, Wrench } from 'lucide-react';
import { SolveResponse } from '@/types';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { ChevronDown } from 'lucide-react';

interface AgentTraceTabProps {
  solution?: SolveResponse | null;
  isLoading?: boolean;
}

const AGENT_STEPS = [
  { name: 'Parser', icon: '📝', description: 'Extracting problem structure' },
  { name: 'RAG', icon: '🔍', description: 'Retrieving relevant formulas' },
  { name: 'Solver', icon: '🧮', description: 'Computing solution' },
  { name: 'Verifier', icon: '✓', description: 'Checking correctness' },
  { name: 'Explainer', icon: '💡', description: 'Formatting explanation' },
];

export function AgentTraceTab({ solution, isLoading }: AgentTraceTabProps) {
  if (!solution && !isLoading) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-4 text-center">
        <Wrench className="mb-2 h-8 w-8 text-[#2C2C35]" />
        <p className="text-sm text-[#55524F]">No active solution</p>
        <p className="text-xs text-[#55524F]/70">Agent trace will appear here</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-3">
      {/* Orchestration Flow */}
      <div className="rounded-lg border border-[#2C2C35] bg-[#15151A] p-3">
        <div className="mb-3 flex items-center justify-between">
          <h4 className="text-xs font-medium text-[#9B9693]">Orchestration Flow</h4>
          {solution?.is_cache_hit && (
            <span className="flex items-center gap-1 rounded-full bg-blue-500/20 px-2 py-0.5 text-[10px] font-semibold text-blue-400">
              <span className="h-1.5 w-1.5 rounded-full bg-blue-400 animate-pulse"></span>
              MEMORY CACHE HIT
            </span>
          )}
        </div>
        <div className="space-y-2">
          {AGENT_STEPS.map((step, index) => {
            const isCompleted = solution ? (solution.is_cache_hit || index < 5) : index === 0 && isLoading;
            const isCurrent = !solution?.is_cache_hit && isLoading && index === 1;
            const needsHitl = step.name === 'Verifier' && solution?.hitl_required;

            return (
              <div
                key={step.name}
                className={`flex items-center gap-2 rounded-md px-2 py-1.5 ${
                  isCurrent ? 'bg-[#6366F1]/10' : ''
                }`}
              >
                <div
                  className={`flex h-5 w-5 items-center justify-center rounded-full text-xs ${
                    isCompleted
                      ? needsHitl
                        ? 'bg-amber-500/20 text-amber-400'
                        : 'bg-green-500/20 text-green-400'
                      : isCurrent
                      ? 'bg-[#6366F1]/20 text-[#6366F1]'
                      : 'bg-[#2C2C35] text-[#55524F]'
                  }`}
                >
                  {isCompleted ? (
                    needsHitl ? (
                      <AlertCircle className="h-3 w-3" />
                    ) : (
                      <Check className="h-3 w-3" />
                    )
                  ) : isCurrent ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    step.icon
                  )}
                </div>
                <div className="flex-1">
                  <div className="text-xs font-medium text-[#EDEAE4]">{step.name}</div>
                  <div className="text-[10px] text-[#55524F]">{step.description}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Tool Calls */}
      {solution?.solver_result?.tool_calls && solution.solver_result.tool_calls.length > 0 && (
        <div className="rounded-lg border border-[#2C2C35] bg-[#15151A] p-3">
          <h4 className="mb-3 text-xs font-medium text-[#9B9693]">Tool Executions</h4>
          <div className="space-y-2">
            {solution.solver_result.tool_calls.map((call, index) => (
              <Collapsible key={index}>
                <CollapsibleTrigger className="flex w-full items-center justify-between rounded-md bg-[#1D1D23] px-2 py-1.5 text-left hover:bg-[#2C2C35]">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-[#55524F]">{index + 1}.</span>
                    <span className="text-xs font-medium text-[#6366F1]">{call.tool}</span>
                  </div>
                  <ChevronDown className="h-3 w-3 text-[#55524F]" />
                </CollapsibleTrigger>
                <CollapsibleContent className="mt-1 space-y-1 px-2">
                  <div className="rounded bg-[#0E0E11] p-2">
                    <div className="mb-1 text-[10px] uppercase text-[#55524F]">Input</div>
                    <pre className="max-h-20 overflow-auto text-[10px] text-[#9B9693]">
                      {call.input}
                    </pre>
                  </div>
                  <div className="rounded bg-[#0E0E11] p-2">
                    <div className="mb-1 text-[10px] uppercase text-[#55524F]">Output</div>
                    <pre className="max-h-20 overflow-auto text-[10px] text-green-400/80">
                      {call.output}
                    </pre>
                  </div>
                </CollapsibleContent>
              </Collapsible>
            ))}
          </div>
        </div>
      )}

      {/* Verifier Result */}
      {solution?.verifier_result && (
        <div className="rounded-lg border border-[#2C2C35] bg-[#15151A] p-3">
          <h4 className="mb-2 text-xs font-medium text-[#9B9693]">Verification Result</h4>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between">
              <span className="text-[#55524F]">Correct:</span>
              <span className={solution.verifier_result.is_correct ? 'text-green-400' : 'text-red-400'}>
                {solution.verifier_result.is_correct ? 'Yes' : 'No'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#55524F]">Confidence:</span>
              <span className="text-[#EDEAE4]">{Math.round(solution.verifier_result.confidence * 100)}%</span>
            </div>
            {solution.verifier_result.issues.length > 0 && (
              <div className="mt-2 rounded bg-red-500/10 p-2">
                <div className="mb-1 text-[10px] uppercase text-red-400">Issues Found</div>
                <ul className="list-inside list-disc text-[10px] text-red-300/70">
                  {solution.verifier_result.issues.map((issue, i) => (
                    <li key={i}>{issue}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
