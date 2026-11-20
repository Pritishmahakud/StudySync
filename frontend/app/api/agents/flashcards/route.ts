import { NextRequest, NextResponse } from 'next/server'
import { getApiSession } from '@/lib/api-auth'
import { invokePythonBridge } from '@/lib/bridge'
import { getUserFlashcards, reviewUserFlashcard } from '@/lib/user-learning-store'

export async function GET() {
  const { user, errorResponse } = await getApiSession()
  if (errorResponse) return errorResponse

  try {
    const result = await invokePythonBridge('flashcards_due', {
      user_id: user.id,
      email: user.email,
    })
    return NextResponse.json(result)
  } catch (error: any) {
    const cards = getUserFlashcards(user.id, user.email)
    return NextResponse.json({
      status: 'success',
      count: cards.length,
      cards,
    })
  }
}

export async function POST(req: NextRequest) {
  const { user, errorResponse } = await getApiSession()
  if (errorResponse) return errorResponse

  try {
    const body = await req.json()
    const result = await invokePythonBridge('flashcards_review', {
      ...body,
      user_id: user.id,
      email: user.email,
    })
    return NextResponse.json(result)
  } catch (error: any) {
    try {
      const body = await req.json()
      const card = reviewUserFlashcard(user.id, user.email, body.card_id, body.rating || 4)
      return NextResponse.json({ status: 'success', card })
    } catch {
      return NextResponse.json({ status: 'error', message: error.message }, { status: 500 })
    }
  }
}
