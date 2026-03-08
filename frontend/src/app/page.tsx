"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Input } from "@/components/ui/input";
import {
  Brain, Send, Plus, Mic, Image as ImageIcon, ThumbsUp, ThumbsDown,
  CheckCircle2, AlertCircle, RefreshCw, Cpu, Database, User, Copy, Check
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  type: "text" | "image" | "audio";
  isProcessing?: boolean;
  needsReview?: boolean;
  ocrData?: any;
  solution?: any;
  error?: string;
  imageUrl?: string;
};

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const scrollRef = useRef<HTMLDivElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const audioInputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const addMessage = (msg: Omit<ChatMessage, "id">) => {
    const id = Math.random().toString(36).substring(7);
    setMessages(prev => [...prev, { ...msg, id }]);
    return id;
  };

  const updateMessage = (id: string, updates: Partial<ChatMessage>) => {
    setMessages(prev => prev.map(msg => msg.id === id ? { ...msg, ...updates } : msg));
  };

  const handleSolveText = async (query: string) => {
    if (!query.trim()) return;

    setInputValue("");
    addMessage({ role: "user", type: "text", content: query });

    const aiMsgId = addMessage({
      role: "assistant",
      type: "text",
      content: "",
      isProcessing: true
    });

    setIsProcessing(true);

    try {
      const res = await axios.post(`${API_URL}/solve`, {
        question: query,
        use_full_pipeline: true
      });

      updateMessage(aiMsgId, { isProcessing: false, solution: res.data });
    } catch (error: any) {
      updateMessage(aiMsgId, {
        isProcessing: false,
        error: error.response?.data?.detail || error.message || "Failed to solve problem."
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const imageUrl = URL.createObjectURL(file);
    addMessage({ role: "user", type: "image", content: "Uploaded an image for OCR:\n" + file.name, imageUrl });

    const aiMsgId = addMessage({
      role: "assistant",
      type: "text",
      content: "Extracting text from image...",
      isProcessing: true
    });

    setIsProcessing(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(`${API_URL}/ocr/extract`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      const { text, low_confidence, message } = res.data;

      updateMessage(aiMsgId, {
        isProcessing: false,
        content: text,
        needsReview: low_confidence,
        ocrData: res.data
      });

      // If confident, automatically solve
      if (!low_confidence) {
        handleSolveText(text);
      }
    } catch (error: any) {
      updateMessage(aiMsgId, {
        isProcessing: false,
        error: error.response?.data?.detail || "Could not process image."
      });
    } finally {
      setIsProcessing(false);
      if (imageInputRef.current) imageInputRef.current.value = "";
    }
  };

  const handleAudioUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    addMessage({ role: "user", type: "audio", content: "Uploaded an audio file:\n" + file.name });

    const aiMsgId = addMessage({
      role: "assistant",
      type: "text",
      content: "Transcribing audio...",
      isProcessing: true
    });

    setIsProcessing(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(`${API_URL}/asr/transcribe?language=en`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      updateMessage(aiMsgId, {
        isProcessing: false,
        content: res.data.text,
        needsReview: true // Always good to review audio transcription
      });
    } catch (error: any) {
      updateMessage(aiMsgId, {
        isProcessing: false,
        error: error.response?.data?.detail || "Could not process audio."
      });
    } finally {
      setIsProcessing(false);
      if (audioInputRef.current) audioInputRef.current.value = "";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSolveText(inputValue);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-black text-slate-100 font-sans selection:bg-orange-500/30">

      {/* Background Neon Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-orange-600/10 blur-[150px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-orange-900/10 blur-[150px]" />
      </div>

      {/* Header */}
      <header className="relative z-10 p-4 border-b border-orange-500/20 bg-black/50 backdrop-blur-md flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-orange-500 to-red-600 rounded-lg shadow-lg shadow-orange-500/20">
            <Brain className="w-6 h-6 text-black" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-wide flex items-center gap-2">
              <span className="text-white">MATH</span>
              <span className="text-orange-500 drop-shadow-[0_0_8px_rgba(249,115,22,0.8)]">MENTOR</span>
            </h1>
            <p className="text-xs text-orange-200/60 uppercase tracking-widest">Agentic Framework</p>
          </div>
        </div>
        <Badge variant="outline" className="border-orange-500/30 text-orange-400 bg-orange-500/10 uppercase text-[10px] tracking-wider px-3 py-1 animate-pulse">
          Online
        </Badge>
      </header>

      {/* Chat Area */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto w-full max-w-5xl mx-auto p-4 md:p-6 space-y-6 relative z-10 scroll-smooth"
      >
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-50">
            <div className="relative">
              <Cpu className="w-16 h-16 text-orange-500" />
              <div className="absolute inset-0 bg-orange-500 blur-xl opacity-30"></div>
            </div>
            <div>
              <h2 className="text-xl font-medium text-white mb-2">How can I help you today?</h2>
              <p className="text-sm text-slate-400 max-w-md">
                Type a math problem below, upload a photo, or send an audio clip. I will use my agentic pipeline to solve it step-by-step.
              </p>
            </div>
          </div>
        )}

        <AnimatePresence>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div className={`flex gap-4 max-w-[85%] ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}>

                {/* Avatar */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === "user"
                  ? "bg-slate-800 border border-slate-700 text-slate-300"
                  : "bg-gradient-to-br from-orange-500 to-red-600 shadow-md shadow-orange-500/30 text-black"
                  }`}>
                  {msg.role === "user" ? <User className="w-4 h-4" /> : <Brain className="w-4 h-4" />}
                </div>

                {/* Message Bubble */}
                <div className={`flex flex-col space-y-2 ${msg.role === "user" ? "items-end" : "items-start"}`}>
                  <div className={`px-5 py-4 rounded-2xl ${msg.role === "user"
                    ? "bg-slate-800 text-white rounded-tr-sm border border-slate-700/50"
                    : "bg-[#0a0a0a] text-slate-200 rounded-tl-sm border border-orange-500/20 shadow-lg shadow-orange-500/5 min-w-[300px]"
                    }`}>

                    {/* User Text / Preview */}
                    {msg.role === "user" && (
                      <div className="relative group pb-1">
                        {msg.type === "image" && msg.imageUrl && (
                          <div className="mb-2 max-w-sm rounded-lg overflow-hidden border border-slate-700/50">
                            {/* eslint-disable-next-line @next/next/no-img-element */}
                            <img src={msg.imageUrl} alt="Uploaded Math Problem" className="w-full h-auto object-contain" />
                          </div>
                        )}
                        <div className="whitespace-pre-wrap text-sm leading-relaxed pr-8">{msg.content}</div>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleCopy(msg.id, msg.content)}
                          className="absolute right-[-10px] top-[-5px] h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity text-slate-400 hover:text-white"
                        >
                          {copiedId === msg.id ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
                        </Button>
                      </div>
                    )}

                    {/* Assistant Processing */}
                    {msg.role === "assistant" && msg.isProcessing && (
                      <div className="flex items-center gap-3 text-orange-400 text-sm">
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        <span className="animate-pulse">Agents orchestrating...</span>
                      </div>
                    )}

                    {/* Assistant Error */}
                    {msg.role === "assistant" && msg.error && (
                      <div className="flex items-center gap-2 text-red-400 text-sm">
                        <AlertCircle className="w-4 h-4" />
                        {msg.error}
                      </div>
                    )}

                    {/* OCR Review (HITL) */}
                    {msg.role === "assistant" && !msg.isProcessing && msg.needsReview && (
                      <div className="space-y-4 w-full">
                        <div className="flex items-center gap-2 text-yellow-500 text-sm font-medium">
                          <AlertCircle className="w-4 h-4" /> Please review extracted text:
                        </div>
                        <Textarea
                          className="min-h-[100px] bg-black border-orange-500/30 text-orange-100 focus-visible:ring-orange-500"
                          value={msg.content}
                          onChange={(e) => updateMessage(msg.id, { content: e.target.value })}
                        />
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            className="bg-orange-600 hover:bg-orange-700 text-white"
                            onClick={() => {
                              updateMessage(msg.id, { needsReview: false });
                              handleSolveText(msg.content);
                            }}
                          >
                            <CheckCircle2 className="w-4 h-4 mr-2" /> Looks Good, Solve It
                          </Button>
                        </div>
                      </div>
                    )}

                    {/* Solution Details */}
                    {msg.role === "assistant" && msg.solution && (
                      <div className="space-y-6 w-full text-sm">
                        {/* Agent Trace */}
                        {msg.solution.hits && (
                          <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
                            <span className="text-slate-500">Pipeline:</span>
                            {msg.solution.hits.map((hit: string, i: number) => (
                              <div key={i} className="flex items-center gap-1">
                                {i > 0 && <span className="text-slate-600">→</span>}
                                <span className="text-orange-400 bg-orange-500/10 px-1.5 py-0.5 rounded border border-orange-500/20">
                                  {hit}
                                </span>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Parsed Vars */}
                        {msg.solution.parsed && (
                          <div className="bg-orange-950/20 border border-orange-900/50 rounded p-3 font-mono text-xs space-y-1">
                            <div className="flex gap-2">
                              <span className="text-orange-500/70">Topic:</span>
                              <span className="text-orange-200">{msg.solution.parsed.topic || 'General'}</span>
                            </div>
                            {msg.solution.parsed.variables?.length > 0 && (
                              <div className="flex gap-2">
                                <span className="text-orange-500/70">Variables:</span>
                                <span className="text-orange-200">{msg.solution.parsed.variables.join(', ')}</span>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Explanation Content */}
                        {msg.solution.explanation && (
                          <div className="relative group/solution">
                            <div className="prose prose-invert prose-orange max-w-none text-slate-300 pr-8">
                              <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                                {msg.solution.explanation.explanation}
                              </ReactMarkdown>
                            </div>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleCopy(msg.id + '-sol', msg.solution.explanation.explanation)}
                              className="absolute right-[-10px] top-[-5px] h-6 w-6 border border-slate-700 bg-black opacity-0 group-hover/solution:opacity-100 transition-opacity text-slate-400 hover:text-orange-400 z-10"
                            >
                              {copiedId === msg.id + '-sol' ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
                            </Button>
                          </div>
                        )}

                        {/* Verification Notice */}
                        {msg.solution.verification && (
                          <div className={`p-3 rounded border text-xs flex gap-3 items-start ${msg.solution.verification.is_correct
                            ? "bg-green-950/30 border-green-900/50 text-green-400"
                            : "bg-red-950/30 border-red-900/50 text-red-400"
                            }`}>
                            {msg.solution.verification.is_correct ? <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" /> : <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />}
                            <div>
                              <span className="font-bold opacity-80 uppercase tracking-wider block mb-1">
                                Verifier Agent {msg.solution.verification.is_correct ? 'Approved' : 'Flagged'}
                              </span>
                              {msg.solution.verification.issues || "The mathematical steps appear sound."}
                            </div>
                          </div>
                        )}

                        {/* HITL Feedback Buttons */}
                        <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
                          <span className="text-xs text-slate-500">Provide memory feedback:</span>
                          <div className="flex gap-2">
                            <Tooltip>
                              <TooltipTrigger render={
                                <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-green-500/10 hover:text-green-400">
                                  <ThumbsUp className="w-4 h-4" />
                                </Button>
                              } />
                              <TooltipContent className="bg-black border-slate-800 text-white">Correct</TooltipContent>
                            </Tooltip>

                            <Tooltip>
                              <TooltipTrigger render={
                                <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-red-500/10 hover:text-red-400">
                                  <ThumbsDown className="w-4 h-4" />
                                </Button>
                              } />
                              <TooltipContent className="bg-black border-slate-800 text-white">Incorrect / Issue</TooltipContent>
                            </Tooltip>
                          </div>
                        </div>

                      </div>
                    )}

                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Input Area (Bottom) */}
      <div className="relative z-10 w-full max-w-4xl mx-auto p-4 md:p-6">
        <div className="relative flex items-end gap-2 bg-[#050505] border border-orange-500/30 rounded-2xl p-2 shadow-2xl shadow-orange-900/20 focus-within:border-orange-500 transition-colors">

          {/* Upload Dropdown / Plus button */}
          <input
            type="file"
            accept="image/*"
            className="hidden"
            ref={imageInputRef}
            onChange={handleImageUpload}
          />
          <Tooltip>
            <TooltipTrigger render={
              <Button
                variant="ghost"
                size="icon"
                className="shrink-0 text-slate-400 hover:text-orange-400 hover:bg-orange-500/10 h-10 w-10 rounded-xl"
                onClick={() => imageInputRef.current?.click()}
                disabled={isProcessing}
              >
                <Plus className="w-5 h-5" />
              </Button>
            } />
            <TooltipContent className="bg-black border-orange-500/30 text-white">Upload Image</TooltipContent>
          </Tooltip>

          {/* Text Area */}
          <Textarea
            placeholder="Type your math problem here..."
            className="flex-1 min-h-[40px] max-h-[200px] bg-transparent border-0 focus-visible:ring-0 resize-none shadow-none text-sm text-white placeholder:text-slate-600 py-3"
            rows={1}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isProcessing}
            autoFocus
          />

          {/* Audio & Send Trigger */}
          <div className="flex items-center gap-1 shrink-0">
            <input
              type="file"
              accept="audio/*"
              className="hidden"
              ref={audioInputRef}
              onChange={handleAudioUpload}
            />
            {inputValue ? (
              <Button
                className="h-10 w-10 rounded-xl bg-orange-600 hover:bg-orange-500 text-white shadow-lg shadow-orange-600/20 transition-all"
                size="icon"
                onClick={() => handleSolveText(inputValue)}
                disabled={isProcessing}
              >
                <Send className="w-4 h-4 ml-0.5" />
              </Button>
            ) : (
              <Tooltip>
                <TooltipTrigger render={
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-10 w-10 rounded-xl text-slate-400 hover:text-orange-400 hover:bg-orange-500/10"
                    onClick={() => audioInputRef.current?.click()}
                    disabled={isProcessing}
                  >
                    <Mic className="w-5 h-5" />
                  </Button>
                } />
                <TooltipContent className="bg-black border-orange-500/30 text-white">Audio Input</TooltipContent>
              </Tooltip>
            )}
          </div>
        </div>
        <div className="text-center mt-3">
          <p className="text-[10px] text-slate-600 uppercase tracking-widest font-semibold flex items-center justify-center gap-2">
            <Database className="w-3 h-3" /> Math Mentor Memory System Enabled
          </p>
        </div>
      </div>
    </div>
  );
}
