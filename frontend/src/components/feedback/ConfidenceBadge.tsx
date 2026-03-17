'use client';

import { getConfidenceColor, getConfidenceIcon, getConfidenceLevel } from '@/lib/utils';

interface ConfidenceBadgeProps {
  confidence: number;
  showLabel?: boolean;
}

export function ConfidenceBadge({ confidence, showLabel = true }: ConfidenceBadgeProps) {
  const level = getConfidenceLevel(confidence);
  const colorClass = getConfidenceColor(confidence);
  const icon = getConfidenceIcon(confidence);

  return (
    <div
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium ${colorClass}`}
    >
      <span>{icon}</span>
      {showLabel && (
        <>
          <span className="uppercase">{level}</span>
          <span className="opacity-70">({Math.round(confidence * 100)}%)</span>
        </>
      )}
    </div>
  );
}
