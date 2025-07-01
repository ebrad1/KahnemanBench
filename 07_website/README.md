# KahnemanBench Website

This is a Next.js website for the KahnemanBench AI evaluation platform.

## Getting Started

First, install the dependencies:

```bash
npm install
```

Then, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Project Structure

```
07_website/
├── app/                 # Next.js App Router pages
│   ├── layout.tsx      # Root layout with Inter font
│   ├── page.tsx        # Home page
│   ├── globals.css     # Global styles with Tailwind
│   ├── try/            # Interactive evaluation interface
│   │   └── page.tsx
│   └── expert/         # Analysis dashboard
│       └── page.tsx
├── components/         # Reusable React components
│   ├── QuestionViewer.tsx
│   ├── Navigation.tsx
│   └── AnswerCard.tsx
├── lib/               # Utility functions and types
│   └── questions.ts   # TypeScript definitions
└── public/           # Static assets
```

## Features

- **Interactive Evaluation**: Load and browse rating datasets
- **Question Viewer**: Display questions with context toggle
- **Answer Comparison**: Side-by-side response comparison
- **Navigation**: Keyboard and button navigation
- **Expert Analysis**: Detailed performance analysis dashboard

## Development

- Built with Next.js 15+ App Router
- TypeScript for type safety
- Tailwind CSS for styling
- Responsive design for mobile and desktop

## TODO

- [ ] Implement file loading functionality in `/try`
- [ ] Add data fetching for rating datasets
- [ ] Build expert analysis dashboard
- [ ] Add interactive charts and visualizations
- [ ] Implement keyboard shortcuts
- [ ] Add export functionality