import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

interface StudentReview {
  quote: string
  author: string
  rating: number
  branch?: string
  date?: string
}

const dataDir = path.resolve(process.cwd(), '..', 'data')
const reviewsFile = path.join(dataDir, 'reviews.json')

const INITIAL_REVIEWS: StudentReview[] = [
  {
    quote: "Tested the RAG Tutor with our OS notes—the exact citations are super helpful!",
    author: "Asha Sharma · CSE Semester 7",
    rating: 5,
    date: "2026-11-18"
  },
  {
    quote: "The Two-Phase Locking analogy with safety deposit boxes made concurrency click before our mid-sems.",
    author: "Rohan Patel · CSE Semester 5",
    rating: 5,
    date: "2026-11-15"
  },
  {
    quote: "Generating flashcards directly from PDF slides cut my exam revision time in half.",
    author: "Pritish Dash · IT Semester 7",
    rating: 5,
    date: "2026-11-12"
  }
]

function getReviews(): StudentReview[] {
  if (!fs.existsSync(dataDir)) {
    try { fs.mkdirSync(dataDir, { recursive: true }) } catch {}
  }
  if (fs.existsSync(reviewsFile)) {
    try {
      const content = fs.readFileSync(reviewsFile, 'utf-8')
      const parsed = JSON.parse(content)
      if (Array.isArray(parsed) && parsed.length > 0) return parsed
    } catch {}
  }
  try {
    fs.writeFileSync(reviewsFile, JSON.stringify(INITIAL_REVIEWS, null, 2), 'utf-8')
  } catch {}
  return INITIAL_REVIEWS
}

export async function GET() {
  const reviews = getReviews()
  return NextResponse.json({ status: 'success', reviews })
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const author = (body.author || '').trim()
    const quote = (body.quote || '').trim()
    const rating = Math.min(5, Math.max(1, Number(body.rating || 5)))

    if (!author || !quote) {
      return NextResponse.json({ status: 'error', message: 'Author and review quote are required.' }, { status: 400 })
    }

    const current = getReviews()
    const newReview: StudentReview = {
      quote,
      author,
      rating,
      date: new Date().toISOString().split('T')[0]
    }

    current.unshift(newReview)
    try {
      fs.writeFileSync(reviewsFile, JSON.stringify(current, null, 2), 'utf-8')
    } catch {}

    return NextResponse.json({ status: 'success', review: newReview, reviews: current })
  } catch (error: any) {
    return NextResponse.json({ status: 'error', message: error.message }, { status: 500 })
  }
}
