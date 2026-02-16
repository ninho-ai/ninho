import Link from 'next/link'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Documentation',
  description: 'Learn how to install, configure, and use Ninho for AI coding context management.',
}

export default function DocsPage() {
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
            <Link href="/docs/" className="text-ninho-600 font-medium">Docs</Link>
            <Link href="/blog/" className="text-gray-600 hover:text-gray-900">Blog</Link>
            <a href="https://github.com/ninho-ai/ninho" target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-gray-900">GitHub</a>
          </nav>
        </div>
      </header>

      <div className="container-wide py-12">
        <div className="max-w-3xl">
          <h1 className="text-4xl font-bold mb-6">Documentation</h1>
          <p className="text-xl text-gray-600 mb-12">
            Everything you need to know about Ninho.
          </p>

          {/* Quick Start */}
          <section className="mb-16">
            <h2 className="text-2xl font-bold mb-4">Quick Start</h2>
            <p className="text-gray-600 mb-6">
              Get Ninho running in under 2 minutes.
            </p>

            <h3 className="text-lg font-semibold mb-3">1. Install</h3>
            <div className="bg-gray-900 rounded-lg p-4 mb-6">
              <pre className="text-green-400 overflow-x-auto">
                <code>curl -fsSL https://raw.githubusercontent.com/ninho-ai/ninho/main/install.sh | bash</code>
              </pre>
            </div>

            <h3 className="text-lg font-semibold mb-3">2. Restart Claude Code</h3>
            <p className="text-gray-600 mb-6">
              Close and reopen Claude Code to activate the plugin.
            </p>

            <h3 className="text-lg font-semibold mb-3">3. Verify</h3>
            <div className="bg-gray-900 rounded-lg p-4 mb-4">
              <pre className="text-green-400 overflow-x-auto">
                <code>/ninho:status</code>
              </pre>
            </div>
            <p className="text-gray-600">
              You should see &quot;No Ninho data found&quot; initially. As you code, PRDs and learnings will accumulate automatically.
            </p>
          </section>

          {/* How It Works */}
          <section className="mb-16">
            <h2 className="text-2xl font-bold mb-4">How It Works</h2>

            <h3 className="text-lg font-semibold mb-3">Background Processing</h3>
            <p className="text-gray-600 mb-4">
              Ninho uses Claude Code hooks to run in the background:
            </p>
            <ul className="list-disc list-inside text-gray-600 space-y-2 mb-6">
              <li><strong>SessionStart</strong> - Injects PRD context when you start coding</li>
              <li><strong>Stop</strong> - Monitors for PRD-worthy content after each response</li>
              <li><strong>PreCompact</strong> - Captures context before memory compaction</li>
              <li><strong>SessionEnd</strong> - Extracts learnings when you exit</li>
            </ul>

            <h3 className="text-lg font-semibold mb-3">Signal Detection</h3>
            <p className="text-gray-600 mb-4">
              Ninho detects patterns in your conversations:
            </p>
            <div className="overflow-x-auto mb-6">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 pr-4">Signal Type</th>
                    <th className="text-left py-2">Patterns</th>
                  </tr>
                </thead>
                <tbody className="text-gray-600">
                  <tr className="border-b">
                    <td className="py-2 pr-4">Requirements</td>
                    <td className="py-2">&quot;need to&quot;, &quot;should have&quot;, &quot;must support&quot;</td>
                  </tr>
                  <tr className="border-b">
                    <td className="py-2 pr-4">Decisions</td>
                    <td className="py-2">&quot;let&apos;s use&quot;, &quot;decided on&quot;, &quot;we&apos;ll go with&quot;</td>
                  </tr>
                  <tr className="border-b">
                    <td className="py-2 pr-4">Constraints</td>
                    <td className="py-2">&quot;must be&quot;, &quot;cannot&quot;, &quot;limited to&quot;</td>
                  </tr>
                  <tr>
                    <td className="py-2 pr-4">Learnings</td>
                    <td className="py-2">&quot;no, don&apos;t&quot;, &quot;actually&quot;, &quot;remember:&quot;</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          {/* Directory Structure */}
          <section className="mb-16">
            <h2 className="text-2xl font-bold mb-4">Directory Structure</h2>
            <div className="bg-gray-900 rounded-lg p-4 text-gray-300">
              <pre className="overflow-x-auto">{`~/.ninho/                    # Global (user-level)
├── daily/
│   ├── 2026-02-16.md       # Today's learnings
│   └── 2026-02-15.md       # Yesterday's learnings
└── ninho.log               # Debug log

your-project/.ninho/        # Project-level (git-trackable)
├── prds/
│   ├── auth-system.md      # Auto-generated PRD
│   └── api-integration.md
├── prompts/
│   └── 2026-02-16.md       # Captured prompts
└── pr-mappings.json        # Branch-to-PRD links`}</pre>
            </div>
          </section>

          {/* Commands */}
          <section className="mb-16">
            <h2 className="text-2xl font-bold mb-4">Commands</h2>
            <p className="text-gray-600 mb-6">
              Ninho works automatically, but these commands are available for manual control:
            </p>
            <div className="space-y-4">
              <div className="border rounded-lg p-4">
                <code className="text-ninho-600">/ninho:status</code>
                <p className="text-gray-600 mt-2">View PRDs, learnings, and stale items</p>
              </div>
              <div className="border rounded-lg p-4">
                <code className="text-ninho-600">/ninho:prd-list</code>
                <p className="text-gray-600 mt-2">List all PRDs with detailed summaries</p>
              </div>
              <div className="border rounded-lg p-4">
                <code className="text-ninho-600">/ninho:search &lt;query&gt;</code>
                <p className="text-gray-600 mt-2">Search across PRDs and prompts</p>
              </div>
              <div className="border rounded-lg p-4">
                <code className="text-ninho-600">/ninho:digest</code>
                <p className="text-gray-600 mt-2">Generate weekly summary</p>
              </div>
            </div>
          </section>

          {/* PRD Format */}
          <section className="mb-16">
            <h2 className="text-2xl font-bold mb-4">PRD Format</h2>
            <p className="text-gray-600 mb-4">
              PRDs follow a consistent structure:
            </p>
            <div className="bg-gray-900 rounded-lg p-4 text-gray-300">
              <pre className="overflow-x-auto text-sm">{`# Feature Name

## Overview
Brief description of the feature.

## Requirements
- [ ] Incomplete requirement
- [x] Completed requirement

## Decisions
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-15 | Use JWT | Stateless, scales horizontally |

## Constraints
- Technical or business constraints

## Open Questions
- Unanswered questions *(asked 2026-02-15)*

## Related Files
- \`src/feature/file.ts\`

## Session Log
### 2026-02-15
- What happened ([prompt](prompts/2026-02-15.md#L12))`}</pre>
            </div>
          </section>

          {/* Troubleshooting */}
          <section>
            <h2 className="text-2xl font-bold mb-4">Troubleshooting</h2>

            <h3 className="text-lg font-semibold mb-3">Plugin not loading?</h3>
            <div className="bg-gray-900 rounded-lg p-4 mb-4">
              <pre className="text-green-400">claude --debug</pre>
            </div>
            <p className="text-gray-600 mb-6">
              Look for &quot;ninho&quot; in the loaded plugins list.
            </p>

            <h3 className="text-lg font-semibold mb-3">Check logs</h3>
            <div className="bg-gray-900 rounded-lg p-4 mb-4">
              <pre className="text-green-400">cat ~/.ninho/ninho.log | tail -20</pre>
            </div>

            <h3 className="text-lg font-semibold mb-3">Reinstall</h3>
            <div className="bg-gray-900 rounded-lg p-4">
              <pre className="text-green-400">rm -rf ~/.ninho-plugin && curl -fsSL https://raw.githubusercontent.com/ninho-ai/ninho/main/install.sh | bash</pre>
            </div>
          </section>
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
