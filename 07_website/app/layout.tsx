import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Link from 'next/link'
import './globals.css'

const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter'
})

export const metadata: Metadata = {
  title: 'KahnemanBench - Testing Human-Like Reasoning in AI',
  description: 'An evaluation benchmark for testing whether AI systems exhibit human-like reasoning patterns and biases.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans antialiased bg-gray-50 text-gray-900">
        <div className="min-h-screen flex flex-col">
          <header className="bg-white border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center h-16">
                <div className="flex items-center">
                  <h1 className="text-xl font-semibold">KahnemanBench</h1>
                </div>
                <nav className="hidden md:flex space-x-8">
                  <Link href="/" className="text-gray-700 hover:text-gray-900 transition-colors">Home</Link>
                  <Link href="/try" className="text-gray-700 hover:text-gray-900 transition-colors">Try It</Link>
                  <Link href="/expert" className="text-gray-700 hover:text-gray-900 transition-colors">Expert Mode</Link>
                  <Link href="/dashboard" className="text-gray-700 hover:text-gray-900 transition-colors">Dashboard</Link>
                  <span className="text-gray-500 cursor-not-allowed">Paper</span>
                </nav>
              </div>
            </div>
          </header>
          <main className="flex-grow">
            {children}
          </main>
          <footer className="bg-white border-t border-gray-200 py-8 mt-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-gray-600">
              © 2024 KahnemanBench. All rights reserved.
            </div>
          </footer>
        </div>
      </body>
    </html>
  )
}