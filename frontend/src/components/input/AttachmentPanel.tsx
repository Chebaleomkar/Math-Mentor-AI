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
    <div className="absolute bottom-full left-0 right-0 z-50 mb-3 rounded-2xl border border-[#2C2C35] bg-[#15151A]/90 p-4 shadow-[0_-8px_32px_rgba(0,0,0,0.5)] backdrop-blur-md transition-all animate-in slide-in-from-bottom-2 duration-300">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-xs font-medium text-[#9B9693]">Add attachment</span>
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6 text-[#55524F] hover:text-[#EDEAE4]"
          onClick={onClose}
        >
          <X className="h-3 w-3" />
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2 bg-[#1D1D23]/80 p-1">
          <TabsTrigger 
            value="image" 
            className="text-xs text-[#9B9693] transition-all data-[state=active]:bg-[#6366F1] data-[state=active]:text-white hover:text-[#EDEAE4]"
          >
            <ImageIcon className="mr-1 h-3 w-3" /> Image
          </TabsTrigger>
          <TabsTrigger 
            value="audio" 
            className="text-xs text-[#9B9693] transition-all data-[state=active]:bg-[#6366F1] data-[state=active]:text-white hover:text-[#EDEAE4]"
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
                  className="max-h-32 w-full rounded-lg border border-[#2C2C35] object-contain"
                />
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute right-1 top-1 h-6 w-6 bg-[#0E0E11]/80 text-[#EDEAE4]"
                  onClick={() => setPreviewUrl(null)}
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            ) : (
              <div
                className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-[#2C2C35] bg-[#1D1D23] p-4 transition-colors hover:border-[#6366F1] hover:bg-[#1E1E3F]"
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload className="mb-2 h-6 w-6 text-[#6366F1]" />
                <span className="text-xs text-[#9B9693]">Click to upload image</span>
                <span className="text-[10px] text-[#55524F]">JPG, PNG, WebP up to 5MB</span>
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
              <div className="flex flex-col items-center gap-2 rounded-lg border border-[#6366F1] bg-[#1E1E3F] p-4">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 animate-pulse rounded-full bg-red-500" />
                  <span className="font-mono text-lg text-[#6366F1]">{formatTime(recordingTime)}</span>
                </div>
                <Button
                  variant="destructive"
                  size="sm"
                  className="w-full"
                  onClick={stopRecording}
                >
                  Stop Recording
                </Button>
              </div>
            ) : (
              <>
                <Button
                  variant="outline"
                  className="w-full border-[#2C2C35] bg-[#1D1D23] text-[#EDEAE4] hover:border-[#6366F1] hover:bg-[#1E1E3F]"
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
                    className="flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-[#2C2C35] bg-[#1D1D23] p-3 transition-colors hover:border-[#6366F1] hover:bg-[#1E1E3F]"
                  >
                    <Upload className="mb-1 h-4 w-4 text-[#6366F1]" />
                    <span className="text-[10px] text-[#9B9693]">Or upload audio file</span>
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
