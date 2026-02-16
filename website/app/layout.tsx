import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const jetbrains = JetBrains_Mono({ subsets: ['latin'], variable: '--font-jetbrains' })

export const metadata: Metadata = {
  title: {
    default: 'Ninho - Where Your Codebase Decisions Live',
    template: '%s | Ninho',
  },
  description: 'Automatically capture decisions, requirements, and learnings from AI coding sessions. Never lose context again.',
  keywords: ['AI coding', 'Claude Code', 'context management', 'PRD', 'developer tools', 'documentation'],
  authors: [{ name: 'Ninho', url: 'https://ninho.ai' }],
  creator: 'Ninho',
  openGraph: {
    title: 'Ninho - AI Coding Context Management',
    description: 'Stop losing context from AI coding sessions. Automatic PRD and learning capture.',
    url: 'https://ninho.ai',
    siteName: 'Ninho',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Ninho - Where your codebase decisions live',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Ninho - AI Coding Context Management',
    description: 'Stop losing context from AI coding sessions',
    images: ['/og-image.png'],
  },
  robots: {
    index: true,
    follow: true,
  },
  metadataBase: new URL('https://ninho.ai'),
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrains.variable}`}>
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'SoftwareApplication',
              name: 'Ninho',
              description: 'Context management plugin for AI coding assistants',
              applicationCategory: 'DeveloperApplication',
              operatingSystem: 'macOS, Linux, Windows',
              offers: {
                '@type': 'Offer',
                price: '0',
                priceCurrency: 'USD',
              },
            }),
          }}
        />
      </head>
      <body className="min-h-screen">
        {children}
      </body>
    </html>
  )
}
