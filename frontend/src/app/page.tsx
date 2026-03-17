'use client';

import { useChat } from '@/hooks/useChat';
import { Header } from '@/components/shared/Header';
import { MessageList } from '@/components/chat/MessageList';
import { InputBar } from '@/components/input/InputBar';
import { InspectorPanel } from '@/components/inspector/InspectorPanel';
import { HITLPanel } from '@/components/feedback/HITLPanel';
import { FeedbackStrip } from '@/components/feedback/FeedbackStrip';
import { Button } from '@/components/ui/button';
import { Trash2 } from 'lucide-react';

export default function Home() {
  const {
    messages,
    isLoading,
    currentSolution,
    showHitl,
    showFeedback,
    extractedText,
    sendTextMessage,
    sendImageMessage,
    sendAudioMessage,
    submitHITLFeedback,
    submitUserFeedback,
    clearChat,
  } = useChat();

  return (
    <div className="flex h-screen flex-col bg-[#0E0E11]">
      <Header />

      <div className="flex flex-1 overflow-hidden">
        {/* Main Chat Area */}
        <div className="flex flex-1 flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-hidden">
            <MessageList messages={messages} isLoading={isLoading} />
          </div>

          {/* Input Area */}
          <div className="border-t border-[#2C2C35] bg-[#0E0E11] p-4">
            <div className="mx-auto max-w-3xl space-y-3">
              {/* HITL Panel */}
              {showHitl && (
                <HITLPanel onSubmit={submitHITLFeedback} />
              )}

              {/* Feedback Strip */}
              {showFeedback && !showHitl && (
                <FeedbackStrip onFeedback={submitUserFeedback} />
              )}

              {/* Input Bar */}
              <InputBar
                onSendMessage={sendTextMessage}
                onSendImage={sendImageMessage}
                onSendAudio={sendAudioMessage}
                isLoading={isLoading}
                extractedText={extractedText}
              />

              {/* Clear Chat Button */}
              {messages.length > 0 && (
                <div className="flex justify-center">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-xs text-[#55524F] hover:text-[#9B9693]"
                    onClick={clearChat}
                  >
                    <Trash2 className="mr-1 h-3 w-3" />
                    Clear Chat
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Inspector Panel - Hidden on mobile */}
        <div className="hidden w-[380px] border-l border-[#2C2C35] bg-[#0E0E11] p-4 lg:block">
          <InspectorPanel
            solution={currentSolution}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  );
}
