import Link from 'next/link'

export default function Home() {
  return (
    <main>
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
            <a
              href="https://github.com/ninho-ai/ninho"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-gray-900"
            >
              GitHub
            </a>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="py-20 md:py-32">
        <div className="container-narrow text-center">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
            Where your codebase<br />
            <span className="text-ninho-600">decisions live</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Automatically capture decisions, requirements, and learnings from AI coding sessions.
            Never explain &quot;why&quot; twice.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="#install" className="btn-primary">
              Get Started
            </a>
            <a
              href="https://github.com/ninho-ai/ninho"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary"
            >
              View on GitHub
            </a>
          </div>
        </div>
      </section>

      {/* Problem */}
      <section className="py-16 bg-gray-50">
        <div className="container-narrow">
          <h2 className="text-3xl font-bold text-center mb-12">The Problem</h2>
          <div className="prose prose-lg mx-auto">
            <p className="text-gray-600">
              Every AI coding session generates valuable context:
            </p>
            <ul className="text-gray-600 space-y-2 mt-4">
              <li>Why you chose JWT over sessions</li>
              <li>What constraints shaped the architecture</li>
              <li>Which approaches you tried and rejected</li>
            </ul>
            <p className="text-xl font-semibold text-gray-900 mt-6">
              But when the session ends, that context disappears.
            </p>
          </div>
        </div>
      </section>

      {/* Solution */}
      <section className="py-16">
        <div className="container-wide">
          <h2 className="text-3xl font-bold text-center mb-12">The Solution</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6 bg-white border border-gray-200 rounded-xl">
              <div className="text-3xl mb-4">&#128220;</div>
              <h3 className="text-xl font-semibold mb-2">PRDs</h3>
              <p className="text-gray-600">
                Living documents that track requirements, decisions, and constraints.
                Auto-generated from your conversations.
              </p>
            </div>
            <div className="p-6 bg-white border border-gray-200 rounded-xl">
              <div className="text-3xl mb-4">&#128161;</div>
              <h3 className="text-xl font-semibold mb-2">Learnings</h3>
              <p className="text-gray-600">
                Corrections and insights captured automatically.
                Never make the same mistake twice.
              </p>
            </div>
            <div className="p-6 bg-white border border-gray-200 rounded-xl">
              <div className="text-3xl mb-4">&#128279;</div>
              <h3 className="text-xl font-semibold mb-2">PR Context</h3>
              <p className="text-gray-600">
                Rich context for code reviewers.
                PRs linked to PRDs with decisions and rationale.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-16 bg-gray-50">
        <div className="container-narrow">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
          <div className="space-y-8">
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-ninho-600 text-white rounded-full flex items-center justify-center font-semibold">1</div>
              <div>
                <h3 className="font-semibold text-lg">Install the plugin</h3>
                <p className="text-gray-600">One command. Works with Claude Code.</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-ninho-600 text-white rounded-full flex items-center justify-center font-semibold">2</div>
              <div>
                <h3 className="font-semibold text-lg">Code normally</h3>
                <p className="text-gray-600">Ninho works in the background. Zero configuration.</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-ninho-600 text-white rounded-full flex items-center justify-center font-semibold">3</div>
              <div>
                <h3 className="font-semibold text-lg">Context accumulates</h3>
                <p className="text-gray-600">PRDs, learnings, and PR links build up automatically.</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-ninho-600 text-white rounded-full flex items-center justify-center font-semibold">4</div>
              <div>
                <h3 className="font-semibold text-lg">Never lose context again</h3>
                <p className="text-gray-600">Session starts? Context is injected. New team member? Full history available.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Install */}
      <section id="install" className="py-16">
        <div className="container-narrow">
          <h2 className="text-3xl font-bold text-center mb-12">Quick Start</h2>
          <div className="bg-gray-900 rounded-xl p-6 mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">One-liner install</span>
            </div>
            <pre className="text-green-400 overflow-x-auto">
              <code>curl -fsSL https://raw.githubusercontent.com/ninho-ai/ninho/main/install.sh | bash</code>
            </pre>
          </div>
          <p className="text-center text-gray-600 mb-4">
            Or install via GitHub:
          </p>
          <div className="bg-gray-900 rounded-xl p-6">
            <pre className="text-green-400 overflow-x-auto">
              <code>git clone https://github.com/ninho-ai/ninho ~/.ninho-plugin{'\n'}~/.ninho-plugin/install.sh</code>
            </pre>
          </div>
          <p className="text-center text-gray-500 mt-6">
            Requires Python 3.9+ and Claude Code
          </p>
        </div>
      </section>

      {/* Automatic features */}
      <section className="py-16 bg-gray-50">
        <div className="container-wide">
          <h2 className="text-3xl font-bold text-center mb-12">Fully Automatic</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="py-4 px-6 font-semibold">When</th>
                  <th className="py-4 px-6 font-semibold">What Happens</th>
                </tr>
              </thead>
              <tbody className="text-gray-600">
                <tr className="border-b border-gray-100">
                  <td className="py-4 px-6">Session starts</td>
                  <td className="py-4 px-6">PRD summaries and stale questions surfaced</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="py-4 px-6">You discuss features</td>
                  <td className="py-4 px-6">Requirements, decisions, constraints captured</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="py-4 px-6">You edit files</td>
                  <td className="py-4 px-6">Related PRD context shown</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="py-4 px-6">You run <code>gh pr create</code></td>
                  <td className="py-4 px-6">Branch auto-linked to PRD</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="py-4 px-6">PR merges</td>
                  <td className="py-4 px-6">Requirements auto-marked complete</td>
                </tr>
                <tr>
                  <td className="py-4 px-6">Session ends</td>
                  <td className="py-4 px-6">Learnings extracted and saved</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="container-narrow text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to stop losing context?</h2>
          <p className="text-gray-600 mb-8">
            Join developers who never have to explain their decisions twice.
          </p>
          <a href="#install" className="btn-primary">
            Install Ninho
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 py-12">
        <div className="container-wide">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-xl">&#x1FAB9;</span>
              <span className="font-semibold">Ninho</span>
              <span className="text-gray-400">- Where your codebase decisions live</span>
            </div>
            <div className="flex gap-6 text-gray-600">
              <Link href="/docs/" className="hover:text-gray-900">Docs</Link>
              <Link href="/blog/" className="hover:text-gray-900">Blog</Link>
              <a href="https://github.com/ninho-ai/ninho" target="_blank" rel="noopener noreferrer" className="hover:text-gray-900">GitHub</a>
            </div>
          </div>
          <p className="text-center text-gray-400 mt-8">
            MIT License. Built with love for developers.
          </p>
        </div>
      </footer>
    </main>
  )
}
