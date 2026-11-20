import { NextRequest, NextResponse } from 'next/server'
import { getApiSession } from '@/lib/api-auth'
import { resetUserLearningData } from '@/lib/user-learning-store'

export async function POST() {
  const { user, errorResponse } = await getApiSession()
  if (errorResponse) return errorResponse

  const success = resetUserLearningData(user.id, user.email)
  return NextResponse.json({
    status: success ? 'success' : 'error',
    message: success ? 'All user flashcards, test records, and learning history reset successfully.' : 'Failed to reset learning history.'
  })
}
