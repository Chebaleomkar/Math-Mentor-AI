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
    extractionSource,
    sendTextMessage,
    sendImageMessage,
    sendAudioMessage,
    submitHITLFeedback,
    submitUserFeedback,
    clearChat,
    loadFromHistory,
    agentActivity,
  } = useChat();

  return (
    <div className="flex h-[100dvh] flex-col bg-background transition-colors duration-300">
      <Header />

      <div className="flex flex-1 overflow-hidden relative">
        {/* Background decorative elements */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none opacity-20">
          <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] rounded-full bg-primary/20 blur-[120px]" />
          <div className="absolute top-[20%] -right-[10%] w-[30%] h-[30%] rounded-full bg-primary/10 blur-[100px]" />
        </div>

        {/* Main Chat Area */}
        <div className="flex flex-1 flex-col relative z-10">
          {/* Messages */}
          <div className="flex-1 overflow-hidden">
            <MessageList 
              messages={messages} 
              isLoading={isLoading} 
              onSelectTopic={sendTextMessage}
              agentActivity={agentActivity}
            />
          </div>

          {/* Input Area */}
          <div className="border-t border-border/40 glass-dark p-4 pb-8 md:pb-6">
            <div className="mx-auto max-w-3xl space-y-4">
              {/* HITL Panel */}
              {showHitl && (
                <div className="animate-in slide-in-from-bottom-4 duration-500">
                  <HITLPanel onSubmit={submitHITLFeedback} />
                </div>
              )}

              {/* Feedback Strip */}
              {showFeedback && !showHitl && (
                <div className="animate-in fade-in slide-in-from-bottom-2 duration-500">
                  <FeedbackStrip onFeedback={submitUserFeedback} />
                </div>
              )}

              {/* Input Bar */}
              <InputBar
                onSendMessage={sendTextMessage}
                onSendImage={sendImageMessage}
                onSendAudio={sendAudioMessage}
                isLoading={isLoading}
                extractedText={extractedText}
                extractionSource={extractionSource}
              />

              {/* Clear Chat Button */}
              {messages.length > 0 && (
                <div className="flex justify-center">
                  <Button
                    variant="ghost"
                    size="xs"
                    className="text-[10px] font-bold tracking-widest uppercase text-muted-foreground/60 hover:text-primary transition-colors"
                    onClick={clearChat}
                  >
                    <Trash2 className="mr-1.5 h-3 w-3" />
                    Clear Conversation
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Inspector Panel - Hidden on mobile */}
        <div className="hidden w-[400px] border-l border-border/40 glass-dark p-0 lg:block relative z-10 transition-all">
          <InspectorPanel
            solution={currentSolution}
            isLoading={isLoading}
            onSelectHistoryItem={(item) => loadFromHistory(item.id)}
          />
        </div>
      </div>
    </div>
  );
}
