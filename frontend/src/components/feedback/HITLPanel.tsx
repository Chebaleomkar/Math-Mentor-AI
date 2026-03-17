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
    <div className="mb-4 rounded-xl border border-[#6366F1] bg-[#1E1E3F] p-4 shadow-[0_4px_20px_rgba(0,0,0,0.3),0_0_12px_rgba(99,102,241,0.12)]">
      <Alert className="mb-3 border-amber-500/20 bg-amber-500/10">
        <AlertTriangle className="h-4 w-4 text-amber-400" />
        <AlertTitle className="text-amber-400">Low Confidence Alert</AlertTitle>
        <AlertDescription className="text-amber-200/70">
          Our AI is not confident about this solution. Please review and confirm or provide a correction.
        </AlertDescription>
      </Alert>

      {isEditing ? (
        <div className="space-y-3">
          <div className="space-y-1">
            <label className="text-xs text-[#9B9693]">Your corrected answer:</label>
            <Textarea
              value={editedAnswer}
              onChange={(e) => setEditedAnswer(e.target.value)}
              placeholder="Enter the correct solution here..."
              className="min-h-[80px] border-[#6366F1]/50 bg-[#15151A] text-sm text-[#EDEAE4] placeholder:text-[#55524F] focus-visible:ring-[#6366F1]"
            />
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              className="flex-1 border-[#2C2C35] text-[#9B9693]"
              onClick={() => setIsEditing(false)}
            >
              Cancel
            </Button>
            <Button
              size="sm"
              className="flex-1 gap-1 bg-[#6366F1] text-white hover:bg-[#818CF8]"
              onClick={handleEdit}
              disabled={!editedAnswer.trim()}
            >
              <Check className="h-3 w-3" />
              Submit Correction
            </Button>
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-2 sm:flex-row">
          <Button
            variant="outline"
            size="sm"
            className="flex-1 gap-1 border-green-500/30 text-green-400 hover:bg-green-500/10 hover:text-green-300"
            onClick={handleApprove}
          >
            <Check className="h-3 w-3" />
            Approve Solution
          </Button>
          <Button
            size="sm"
            className="flex-1 gap-1 bg-[#6366F1] text-white hover:bg-[#818CF8]"
            onClick={() => setIsEditing(true)}
          >
            <Edit3 className="h-3 w-3" />
            Provide Correction
          </Button>
        </div>
      )}
    </div>
  );
}
