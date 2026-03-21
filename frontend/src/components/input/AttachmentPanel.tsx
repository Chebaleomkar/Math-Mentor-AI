'use client';

import { useState, useRef, ChangeEvent } from 'react';
import { ImageIcon, Mic, Upload, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface AttachmentPanelProps {
  onImageSelect: (file: File) => void;
  onAudioSelect: (file: File) => void;
  onClose: () => void;
}

export function AttachmentPanel({
  onImageSelect,
  onAudioSelect,
  onClose,
}: AttachmentPanelProps) {
  const [activeTab, setActiveTab] = useState('image');
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Handle file selection
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>, type: 'image' | 'audio') => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Create preview for images
    if (type === 'image') {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }

    // Auto-submit after selection
    if (type === 'image') {
      onImageSelect(file);
    } else {
      onAudioSelect(file);
    }

    // Reset
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Start audio recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const file = new File([blob], 'recording.webm', { type: 'audio/webm' });
        onAudioSelect(file);

        // Stop all tracks
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (error) {
      console.error('Failed to start recording:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  // Stop audio recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setRecordingTime(0);

      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  // Format recording time
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="absolute bottom-full left-0 right-0 z-50 mb-3 rounded-2xl border border-border/50 bg-background/80 p-4 shadow-2xl backdrop-blur-xl transition-all animate-in slide-in-from-bottom-2 duration-300">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-xs font-medium text-muted-foreground"></span>
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6 text-muted-foreground hover:text-foreground hover:bg-secondary/50"
          onClick={onClose}
        >
          <X className="h-3 w-3" />
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2 bg-secondary/80 p-1">
          <TabsTrigger
            value="image"
            className="text-xs text-muted-foreground transition-all data-[state=active]:bg-primary data-[state=active]:text-primary-foreground hover:text-foreground"
          >
            <ImageIcon className="mr-1 h-3 w-3" /> Image
          </TabsTrigger>
          <TabsTrigger
            value="audio"
            className="text-xs text-muted-foreground transition-all data-[state=active]:bg-primary data-[state=active]:text-primary-foreground hover:text-foreground"
          >
            <Mic className="mr-1 h-3 w-3" /> Audio
          </TabsTrigger>
        </TabsList>

        <TabsContent value="image" className="mt-2">
          <div className="space-y-2">
            {previewUrl ? (
              <div className="relative">
                <img
                  src={previewUrl}
                  alt="Preview"
                  className="max-h-32 w-full rounded-lg border border-border object-contain"
                />
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute right-1 top-1 h-6 w-6 bg-background/80 text-foreground hover:bg-background"
                  onClick={() => setPreviewUrl(null)}
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            ) : (
              <div
                className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-border/60 bg-secondary/30 p-4 transition-all hover:border-primary/50 hover:bg-primary/5"
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload className="mb-2 h-6 w-6 text-primary" />
                <span className="text-xs font-medium text-foreground">Click to upload image</span>
                <span className="text-[10px] text-muted-foreground">JPG, PNG, WebP up to 5MB</span>
              </div>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => handleFileChange(e, 'image')}
            />
          </div>
        </TabsContent>

        <TabsContent value="audio" className="mt-2">
          <div className="space-y-2">
            {isRecording ? (
              <div className="flex flex-col items-center gap-2 rounded-lg border border-primary/40 bg-primary/5 p-4">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 animate-pulse rounded-full bg-destructive" />
                  <span className="font-mono text-lg font-bold text-primary">{formatTime(recordingTime)}</span>
                </div>
                <Button
                  variant="destructive"
                  size="sm"
                  className="w-full shadow-lg shadow-destructive/20"
                  onClick={stopRecording}
                >
                  Stop Recording
                </Button>
              </div>
            ) : (
              <>
                <Button
                  variant="outline"
                  className="w-full border-border bg-secondary/50 text-foreground hover:border-primary/50 hover:bg-primary/5"
                  onClick={startRecording}
                >
                  <Mic className="mr-2 h-4 w-4" />
                  Start Recording
                </Button>

                <div className="relative">
                  <input
                    type="file"
                    accept="audio/*"
                    className="hidden"
                    id="audio-upload"
                    onChange={(e) => handleFileChange(e, 'audio')}
                  />
                  <label
                    htmlFor="audio-upload"
                    className="flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-border/60 bg-secondary/30 p-3 transition-all hover:border-primary/50 hover:bg-primary/5"
                  >
                    <Upload className="mb-1 h-4 w-4 text-primary" />
                    <span className="text-[10px] font-medium text-muted-foreground">Or upload audio file</span>
                  </label>
                </div>
              </>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
