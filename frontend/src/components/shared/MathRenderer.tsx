'use client';

import { useEffect, useRef } from 'react';
import katex from 'katex';
import 'katex/dist/katex.min.css';

interface MathRendererProps {
  content: string;
  className?: string;
}

export function MathRenderer({ content, className = '' }: MathRendererProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Process LaTeX in the content
    let processedContent = content;

    // Replace block math $$...$$
    processedContent = processedContent.replace(
      /\$\$([^$]+)\$\$/g,
      (match, latex) => {
        try {
          return katex.renderToString(latex.trim(), {
            displayMode: true,
            throwOnError: false,
          });
        } catch {
          return match;
        }
      }
    );

    // Replace inline math $...$
    processedContent = processedContent.replace(
      /\$([^$]+)\$/g,
      (match, latex) => {
        try {
          return katex.renderToString(latex.trim(), {
            displayMode: false,
            throwOnError: false,
          });
        } catch {
          return match;
        }
      }
    );

    // Replace \[...\] block math
    processedContent = processedContent.replace(
      /\\\[([^\\]+)\\\]/g,
      (match, latex) => {
        try {
          return katex.renderToString(latex.trim(), {
            displayMode: true,
            throwOnError: false,
          });
        } catch {
          return match;
        }
      }
    );

    // Replace \(...\) inline math
    processedContent = processedContent.replace(
      /\\\(([^\\]+)\\\)/g,
      (match, latex) => {
        try {
          return katex.renderToString(latex.trim(), {
            displayMode: false,
            throwOnError: false,
          });
        } catch {
          return match;
        }
      }
    );

    // Process markdown-like formatting
    // Bold
    processedContent = processedContent.replace(
      /\*\*([^*]+)\*\*/g,
      '<strong>$1</strong>'
    );

    // Italic
    processedContent = processedContent.replace(
      /\*([^*]+)\*/g,
      '<em>$1</em>'
    );

    // Code blocks
    processedContent = processedContent.replace(
      /```([^`]+)```/gs,
      '<pre class="math-code-block"><code>$1</code></pre>'
    );

    // Inline code
    processedContent = processedContent.replace(
      /`([^`]+)`/g,
      '<code class="math-inline-code">$1</code>'
    );

    // Line breaks
    processedContent = processedContent.replace(/\n/g, '<br />');

    // Horizontal rule
    processedContent = processedContent.replace(
      /---/g,
      '<hr class="math-hr" />'
    );

    containerRef.current.innerHTML = processedContent;
  }, [content]);

  return (
    <div
      ref={containerRef}
      className={`prose prose-invert max-w-none ${className}`}
      style={{
        color: '#EDEAE4',
        lineHeight: 1.7,
      }}
    />
  );
}

// Live preview component for input
interface LatexPreviewProps {
  text: string;
  visible: boolean;
}

export function LatexPreview({ text, visible }: LatexPreviewProps) {
  const previewRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!previewRef.current || !visible) return;

    // Extract and render only LaTeX parts
    const latexMatches = text.match(/\$[^$]+\$/g) || [];

    if (latexMatches.length === 0) {
      previewRef.current.innerHTML = '';
      return;
    }

    const rendered = latexMatches.map((match) => {
      const latex = match.slice(1, -1); // Remove $ delimiters
      try {
        return katex.renderToString(latex, {
          displayMode: false,
          throwOnError: false,
        });
      } catch {
        return match;
      }
    });

    previewRef.current.innerHTML = `
      <div class="flex flex-col gap-1">
        <div class="text-[10px] font-bold uppercase tracking-[0.1em] text-blue-500  ">Live Preview</div>
        <div class="text-[#EDEAE4] overflow-x-auto">
          ${rendered.join(' ')}
        </div>
      </div>
    `;
  }, [text, visible]);

  if (!visible) return null;

  return (
    <div
      ref={previewRef}
      className="mb-4 rounded-xl border border-dashed border-[#2C2C35] bg-[#1D1D23]/40 px-4 py-3 text-sm backdrop-blur-sm shadow-inner"
    />
  );
}
