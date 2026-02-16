import Link from 'next/link'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Why AI Coding Context Gets Lost (And How to Fix It)',
  description: 'AI coding assistants generate valuable insights during sessions. Here\'s why that context disappears and how to preserve it.',
  keywords: ['AI coding', 'context management', 'Claude Code', 'memory', 'developer productivity'],
  openGraph: {
    title: 'Why AI Coding Context Gets Lost (And How to Fix It)',
    description: 'AI coding assistants generate valuable insights during sessions. Here\'s why that context disappears and how to preserve it.',
    type: 'article',
    publishedTime: '2026-02-16',
  },
}

export default function ArticlePage() {
  return (
    <main className="min-h-screen">
      {/* Header */}
      <header className="border-b border-gray-100">
        <div className="container-wide py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-xl font-semibold">
            <span className="text-2xl">&#x1FAB9;</span>
            <span>Ninho</span>
          </Link>
          <nav className="flex items-center gap-6">
            <Link href="/docs/" className="text-gray-600 hover:text-gray-900">Docs</Link>
            <Link href="/blog/" className="text-gray-600 hover:text-gray-900">Blog</Link>
            <a href="https://github.com/ninho-ai/ninho" target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-gray-900">GitHub</a>
          </nav>
        </div>
      </header>

      <article className="container-narrow py-12">
        <Link href="/blog/" className="text-ninho-600 hover:underline mb-4 inline-block">
          &larr; Back to Blog
        </Link>

        <header className="mb-12">
          <span className="text-sm text-ninho-600 font-medium">Problem/Solution</span>
          <h1 className="text-4xl font-bold mt-2 mb-4">
            Why AI Coding Context Gets Lost (And How to Fix It)
          </h1>
          <time className="text-gray-500">February 16, 2026</time>
        </header>

        <div className="prose prose-lg max-w-none">
          <p className="lead text-xl text-gray-600">
            You&apos;ve spent an hour with Claude Code, making architectural decisions, discussing trade-offs, and building features. The session ends. Two weeks later, a teammate asks: &quot;Why did we use JWT instead of sessions?&quot;
          </p>
          <p className="text-xl font-semibold">You have no idea. The context is gone.</p>

          <h2>The Problem: Ephemeral Context</h2>
          <p>
            AI coding assistants like Claude Code, Cursor, and Aider operate in sessions. Each session builds rich context:
          </p>
          <ul>
            <li><strong>Decisions</strong> - &quot;We chose PostgreSQL for its JSON support&quot;</li>
            <li><strong>Constraints</strong> - &quot;Must support SSO for enterprise customers&quot;</li>
            <li><strong>Trade-offs</strong> - &quot;Went with bcrypt over Argon2 for compatibility&quot;</li>
            <li><strong>Rejected approaches</strong> - &quot;Considered Redis sessions, too complex for MVP&quot;</li>
          </ul>
          <p>
            But when the session ends or compacts, this context evaporates. The AI doesn&apos;t remember. Your future self doesn&apos;t remember. New team members never knew.
          </p>

          <h2>Why This Matters</h2>
          <ol>
            <li><strong>Repeated discussions</strong> - Same questions answered multiple times</li>
            <li><strong>Lost rationale</strong> - Code exists without documented &quot;why&quot;</li>
            <li><strong>Onboarding friction</strong> - New team members lack historical context</li>
            <li><strong>PR review gaps</strong> - Reviewers ask questions already answered in development</li>
          </ol>

          <h2>The Technical Cause</h2>
          <p>
            AI models have a <strong>context window</strong> - a maximum number of tokens they can process at once. For Claude, this is typically 100K-200K tokens. Sounds like a lot, right?
          </p>
          <p>
            But in a coding session:
          </p>
          <ul>
            <li>Each file you read consumes tokens</li>
            <li>Each response generates tokens</li>
            <li>Each tool call adds tokens</li>
          </ul>
          <p>
            When the context fills up, older content gets <strong>compacted</strong> or <strong>dropped</strong>. That architectural discussion from 30 minutes ago? Gone. That decision about authentication? Compressed beyond recognition.
          </p>

          <h2>Existing Solutions (and Their Limitations)</h2>

          <h3>1. CLAUDE.md Files</h3>
          <p>
            Claude Code supports project-level CLAUDE.md files that get injected at session start. Great for static rules, but:
          </p>
          <ul>
            <li>Requires manual maintenance</li>
            <li>Doesn&apos;t capture session-specific decisions</li>
            <li>Gets stale quickly</li>
          </ul>

          <h3>2. Manual Documentation</h3>
          <p>
            You could write everything down in Notion, Confluence, or README files. But:
          </p>
          <ul>
            <li>Adds friction to the workflow</li>
            <li>Often gets skipped under time pressure</li>
            <li>Separates documentation from where decisions are made</li>
          </ul>

          <h3>3. Git Commit Messages</h3>
          <p>
            Detailed commit messages capture intent, but:
          </p>
          <ul>
            <li>Only capture what was done, not what was considered</li>
            <li>Miss pre-implementation discussions</li>
            <li>Hard to search and navigate</li>
          </ul>

          <h2>The Solution: Automatic Context Capture</h2>
          <p>
            What if context capture happened automatically, in the background, without adding friction to your workflow?
          </p>
          <p>
            That&apos;s the idea behind <strong>Ninho</strong>. It runs as a Claude Code plugin, monitoring your sessions for:
          </p>
          <ul>
            <li>Requirements (&quot;we need to support...&quot;)</li>
            <li>Decisions (&quot;let&apos;s use JWT for...&quot;)</li>
            <li>Constraints (&quot;must be under 100ms&quot;)</li>
            <li>Learnings (&quot;actually, don&apos;t use git add .&quot;)</li>
          </ul>
          <p>
            It organizes this into <strong>PRDs (Product Requirements Documents)</strong> that live in your repository, versioned with your code.
          </p>

          <h2>How It Works</h2>
          <div className="bg-gray-100 p-6 rounded-lg my-6">
            <ol className="space-y-4">
              <li><strong>Session Start:</strong> Ninho injects relevant PRD context so Claude remembers previous decisions</li>
              <li><strong>During Session:</strong> Background monitoring captures requirements, decisions, and constraints</li>
              <li><strong>File Editing:</strong> When you edit related files, relevant decisions are surfaced</li>
              <li><strong>PR Creation:</strong> Branches are auto-linked to PRDs with context for reviewers</li>
              <li><strong>Session End:</strong> Learnings extracted and saved for future reference</li>
            </ol>
          </div>

          <h2>Getting Started</h2>
          <p>
            Install Ninho with a single command:
          </p>
          <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto">
            <code>curl -fsSL https://raw.githubusercontent.com/ninho-ai/ninho/main/install.sh | bash</code>
          </pre>
          <p>
            Then just code normally. Ninho works in the background. No configuration needed.
          </p>

          <h2>Conclusion</h2>
          <p>
            AI coding assistants are powerful, but their ephemeral nature creates a documentation gap. Every decision made in a session is valuable institutional knowledge that shouldn&apos;t be lost.
          </p>
          <p>
            Automatic context capture closes this gap. Your future self, your teammates, and your code reviewers will thank you.
          </p>
          <p>
            <Link href="/" className="text-ninho-600 hover:underline">
              Try Ninho &rarr;
            </Link>
          </p>
        </div>
      </article>

      {/* Footer */}
      <footer className="border-t border-gray-100 py-8 mt-12">
        <div className="container-wide text-center text-gray-400">
          <p>MIT License. Built with love for developers.</p>
        </div>
      </footer>
    </main>
  )
}
