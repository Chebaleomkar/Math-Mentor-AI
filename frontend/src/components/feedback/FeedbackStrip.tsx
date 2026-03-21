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
      <div className="flex items-center justify-center gap-3 rounded-xl border border-green-500/30 bg-green-500/5 px-6 py-3 text-sm font-medium text-green-600 dark:text-green-400 shadow-lg shadow-green-500/5 animate-in zoom-in-95 duration-500">
        <div className="flex h-6 w-6 items-center justify-center rounded-full bg-green-500/20">
          <Check className="h-4 w-4" />
        </div>
        Thanks for your feedback!
      </div>
    );
  }
 
  if (showComment) {
    return (
      <div className="space-y-3 rounded-xl border border-border/60 bg-secondary/30 p-4 shadow-xl backdrop-blur-sm animate-in slide-in-from-bottom-2 duration-300">
        <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground/80">What went wrong? <span className="text-[10px] lowercase font-normal opacity-60">(optional)</span></p>
        <Textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Describe the issue..."
          className="min-h-[80px] border-border/60 bg-background/50 text-sm text-foreground placeholder:text-muted-foreground/40 focus-visible:ring-primary/40"
        />
        <div className="flex gap-3">
          <Button
            size="sm"
            variant="outline"
            className="flex-1 border-border text-muted-foreground hover:bg-secondary/50"
            onClick={() => setShowComment(false)}
          >
            Cancel
          </Button>
          <Button
            size="sm"
            className="flex-1 bg-primary text-primary-foreground shadow-lg shadow-primary/20 hover:bg-primary/90"
            onClick={handleSubmitComment}
          >
            Submit
          </Button>
        </div>
      </div>
    );
  }
 
  return (
    <div className="flex items-center gap-4 py-2">
      <span className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">Was this solution correct?</span>
      <div className="flex gap-2">
        <Button
          variant="ghost"
          size="sm"
          className="h-8 gap-2 rounded-xl border border-border/60 bg-secondary/30 px-4 text-xs font-medium text-muted-foreground transition-all hover:border-green-500/40 hover:bg-green-500/5 hover:text-green-600 dark:hover:text-green-400 shadow-sm"
          onClick={() => handleFeedback(true)}
        >
          <ThumbsUp className="h-3.5 w-3.5" />
          Yes
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="h-8 gap-2 rounded-xl border border-border/60 bg-secondary/30 px-4 text-xs font-medium text-muted-foreground transition-all hover:border-destructive/40 hover:bg-destructive/5 hover:text-destructive shadow-sm"
          onClick={() => handleFeedback(false)}
        >
          <ThumbsDown className="h-3.5 w-3.5" />
          No
        </Button>
      </div>
    </div>
  );
}
