import Link from 'next/link'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Blog',
  description: 'Articles about AI coding, context management, and developer productivity.',
}

const articles = [
  {
    slug: 'why-ai-coding-context-gets-lost',
    title: 'Why AI Coding Context Gets Lost (And How to Fix It)',
    description: 'AI coding assistants generate valuable insights during sessions. Here\'s why that context disappears and how to preserve it.',
    date: '2026-02-16',
    category: 'Problem/Solution',
  },
  {
    slug: 'context-window-problem',
    title: 'The Context Window Problem: What Every Developer Should Know',
    description: 'Understanding token limits, context compression, and why your AI assistant "forgets" instructions.',
    date: '2026-02-15',
    category: 'Educational',
  },
  {
    slug: 'preserve-context-claude-code',
    title: 'How to Preserve Context Across Claude Code Sessions',
    description: 'Practical techniques for maintaining continuity when working with AI coding assistants.',
    date: '2026-02-14',
    category: 'Tutorial',
  },
]

export default function BlogPage() {
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
            <Link href="/blog/" className="text-ninho-600 font-medium">Blog</Link>
            <a href="https://github.com/ninho-ai/ninho" target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-gray-900">GitHub</a>
          </nav>
        </div>
      </header>

      <div className="container-narrow py-12">
        <h1 className="text-4xl font-bold mb-4">Blog</h1>
        <p className="text-xl text-gray-600 mb-12">
          Insights on AI coding, context management, and developer productivity.
        </p>

        <div className="space-y-8">
          {articles.map((article) => (
            <article key={article.slug} className="border-b border-gray-100 pb-8">
              <Link href={`/blog/${article.slug}/`} className="group">
                <span className="text-sm text-ninho-600 font-medium">{article.category}</span>
                <h2 className="text-2xl font-semibold mt-1 group-hover:text-ninho-600 transition-colors">
                  {article.title}
                </h2>
                <p className="text-gray-600 mt-2">{article.description}</p>
                <time className="text-sm text-gray-400 mt-3 block">{article.date}</time>
              </Link>
            </article>
          ))}
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-100 py-8 mt-12">
        <div className="container-wide text-center text-gray-400">
          <p>MIT License. Built with love for developers.</p>
        </div>
      </footer>
    </main>
  )
}
