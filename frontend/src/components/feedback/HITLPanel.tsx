'use client';

import { useState } from 'react';
import { AlertTriangle, Check, Edit3 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

interface HITLPanelProps {
  onSubmit: (approved: boolean, editedAnswer?: string) => void;
}

export function HITLPanel({ onSubmit }: HITLPanelProps) {
  const [editedAnswer, setEditedAnswer] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  const handleApprove = () => {
    onSubmit(true);
  };

  const handleEdit = () => {
    if (isEditing && editedAnswer.trim()) {
      onSubmit(false, editedAnswer.trim());
    } else {
      setIsEditing(true);
    }
  };

  return (
    <div className="mb-4 rounded-xl border border-primary/30 bg-primary/5 p-5 shadow-xl shadow-primary/5 backdrop-blur-sm animate-in slide-in-from-top-4 duration-500">
      <Alert className="mb-4 border-amber-500/30 bg-amber-500/5">
        <AlertTriangle className="h-4 w-4 text-amber-500" />
        <AlertTitle className="text-amber-500 font-bold">Low Confidence Alert</AlertTitle>
        <AlertDescription className="text-foreground/80">
          Our AI is not fully confident about this solution. Please review and confirm or provide a correction.
        </AlertDescription>
      </Alert>
 
      {isEditing ? (
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground/80">Your corrected answer</label>
            <Textarea
              value={editedAnswer}
              onChange={(e) => setEditedAnswer(e.target.value)}
              placeholder="Enter the correct solution here..."
              className="min-h-[100px] border-primary/20 bg-background/50 text-sm text-foreground placeholder:text-muted-foreground/40 focus-visible:ring-primary/40 shadow-inner"
            />
          </div>
          <div className="flex gap-3">
            <Button
              variant="outline"
              size="sm"
              className="flex-1 border-border text-muted-foreground hover:bg-secondary/50"
              onClick={() => setIsEditing(false)}
            >
              Cancel
            </Button>
            <Button
              size="sm"
              className="flex-1 gap-2 bg-primary text-primary-foreground shadow-lg shadow-primary/20 hover:bg-primary/90"
              onClick={handleEdit}
              disabled={!editedAnswer.trim()}
            >
              <Check className="h-3.5 w-3.5" />
              Submit Correction
            </Button>
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-3 sm:flex-row">
          <Button
            variant="outline"
            size="sm"
            className="flex-1 gap-2 border-green-500/40 text-green-600 hover:bg-green-500/10 dark:text-green-400 dark:hover:bg-green-500/20"
            onClick={handleApprove}
          >
            <Check className="h-3.5 w-3.5" />
            Approve Solution
          </Button>
          <Button
            size="sm"
            className="flex-1 gap-2 bg-primary text-primary-foreground shadow-lg shadow-primary/20 hover:bg-primary/90"
            onClick={() => setIsEditing(true)}
          >
            <Edit3 className="h-3.5 w-3.5" />
            Provide Correction
          </Button>
        </div>
      )}
    </div>
  );
}
