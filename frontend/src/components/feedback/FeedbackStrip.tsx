'use client';

import { useState } from 'react';
import { ThumbsUp, ThumbsDown, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

interface FeedbackStripProps {
  onFeedback: (isCorrect: boolean, comment?: string) => void;
}

export function FeedbackStrip({ onFeedback }: FeedbackStripProps) {
  const [showComment, setShowComment] = useState(false);
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleFeedback = (isCorrect: boolean) => {
    if (isCorrect) {
      onFeedback(true);
      setSubmitted(true);
    } else {
      setShowComment(true);
    }
  };

  const handleSubmitComment = () => {
    onFeedback(false, comment);
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <div className="flex items-center justify-center gap-2 rounded-lg border border-green-500/20 bg-green-500/10 px-4 py-2 text-sm text-green-400">
        <Check className="h-4 w-4" />
        Thanks for your feedback!
      </div>
    );
  }

  if (showComment) {
    return (
      <div className="space-y-2 rounded-lg border border-[#2C2C35] bg-[#1D1D23] p-3">
        <p className="text-xs text-[#9B9693]">What went wrong? (optional)</p>
        <Textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Describe the issue..."
          className="min-h-[60px] border-[#2C2C35] bg-[#15151A] text-sm text-[#EDEAE4] placeholder:text-[#55524F]"
        />
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            className="flex-1 border-[#2C2C35] text-[#9B9693]"
            onClick={() => setShowComment(false)}
          >
            Cancel
          </Button>
          <Button
            size="sm"
            className="flex-1 bg-[#6366F1] text-white hover:bg-[#818CF8]"
            onClick={handleSubmitComment}
          >
            Submit
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-[#9B9693]">Was this solution correct?</span>
      <div className="flex gap-1">
        <Button
          variant="ghost"
          size="sm"
          className="h-7 gap-1 rounded-full border border-[#2C2C35] bg-[#1D1D23] px-3 text-xs text-[#9B9693] hover:border-green-500/50 hover:text-green-400"
          onClick={() => handleFeedback(true)}
        >
          <ThumbsUp className="h-3 w-3" />
          Yes
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="h-7 gap-1 rounded-full border border-[#2C2C35] bg-[#1D1D23] px-3 text-xs text-[#9B9693] hover:border-red-500/50 hover:text-red-400"
          onClick={() => handleFeedback(false)}
        >
          <ThumbsDown className="h-3 w-3" />
          No
        </Button>
      </div>
    </div>
  );
}
