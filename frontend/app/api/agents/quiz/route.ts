import { NextRequest, NextResponse } from 'next/server'
import { getApiSession } from '@/lib/api-auth'
import { invokePythonBridge } from '@/lib/bridge'
import { recordUserQuizAttempt } from '@/lib/user-learning-store'

export async function POST(req: NextRequest) {
  const { user, errorResponse } = await getApiSession()
  if (errorResponse) return errorResponse

  try {
    const body = await req.json()
    const action = body.action || 'generate'

    if (action === 'submit_attempt') {
      const attempt = recordUserQuizAttempt(user.id, user.email, {
        topic: body.topic || 'General Academic Quiz',
        score: Number(body.score || 0),
        total: Number(body.total || 1),
        percentage: Math.round(((Number(body.score || 0)) / (Number(body.total || 1))) * 100),
        difficulty: body.difficulty || 'medium',
      })
      return NextResponse.json({ status: 'success', attempt })
    }

    const result = await invokePythonBridge('quiz_generate', {
      ...body,
      user_id: user.id,
      email: user.email,
    })
    return NextResponse.json(result)
  } catch (error: any) {
    return NextResponse.json({ status: 'error', message: error.message }, { status: 500 })
  }
}
