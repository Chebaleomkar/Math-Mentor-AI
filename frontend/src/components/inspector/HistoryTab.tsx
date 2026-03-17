'use client';

import { useEffect, useState } from 'react';
import { Clock, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { MemorySummary } from '@/types';
import { listMemory } from '@/lib/api';
import { formatDate, getTopicColor, truncate } from '@/lib/utils';

interface HistoryTabProps {
  onSelectProblem?: (problem: MemorySummary) => void;
}

export function HistoryTab({ onSelectProblem }: HistoryTabProps) {
  const [history, setHistory] = useState<MemorySummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await listMemory(10);
      setHistory(data);
    } catch (err) {
      setError('Failed to load history');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-[#6366F1] border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 p-4 text-center">
        <p className="text-sm text-red-400">{error}</p>
        <Button size="sm" variant="outline" onClick={loadHistory}>
          Retry
        </Button>
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-4 text-center">
        <Clock className="mb-2 h-8 w-8 text-[#2C2C35]" />
        <p className="text-sm text-[#55524F]">No history yet</p>
        <p className="text-xs text-[#55524F]/70">Solved problems will appear here</p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 space-y-2 overflow-y-auto p-3">
        {history.map((item) => (
          <div
            key={item.id}
            className="group cursor-pointer rounded-lg border border-[#2C2C35] bg-[#15151A] p-3 transition-all hover:border-[#6366F1]/50 hover:bg-[#1D1D23]"
            onClick={() => onSelectProblem?.(item)}
          >
            <div className="mb-1 flex items-center justify-between">
              <span
                className={`rounded-full border px-2 py-0.5 text-[10px] font-medium uppercase ${getTopicColor(
                  item.topic
                )}`}
              >
                {item.topic}
              </span>
              <span className="text-[10px] text-[#55524F]">{formatDate(item.timestamp)}</span>
            </div>

            <p className="mb-2 text-xs text-[#9B9693] line-clamp-2">
              {truncate(item.problem_text, 80)}
            </p>

            <div className="rounded bg-[#0E0E11] px-2 py-1">
              <span className="text-[10px] uppercase text-[#55524F]">Ans:</span>
              <span className="ml-1 text-xs font-medium text-green-400">
                {truncate(item.final_answer, 40)}
              </span>
            </div>

            {item.user_feedback && (
              <div className="mt-1 flex items-center gap-1">
                <span
                  className={`text-[10px] ${
                    item.user_feedback === 'correct'
                      ? 'text-green-400'
                      : item.user_feedback === 'incorrect'
                      ? 'text-red-400'
                      : 'text-amber-400'
                  }`}
                >
                  {item.user_feedback === 'correct' && '✓ Verified'}
                  {item.user_feedback === 'incorrect' && '✗ Reported incorrect'}
                  {item.user_feedback === 'corrected' && '✎ Corrected'}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="border-t border-[#2C2C35] p-3">
        <Button
          variant="ghost"
          size="sm"
          className="w-full gap-1 text-xs text-[#9B9693] hover:text-[#EDEAE4]"
          onClick={loadHistory}
        >
          <RefreshCw className="h-3 w-3" />
          Refresh History
        </Button>
      </div>
    </div>
  );
}
