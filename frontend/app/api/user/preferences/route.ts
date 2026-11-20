import { NextRequest, NextResponse } from 'next/server'
import { getApiSession } from '@/lib/api-auth'
import { getOrCreateUserRecord, updateUserPreferences } from '@/lib/user-learning-store'

export async function GET() {
  const { user, errorResponse } = await getApiSession()
  if (errorResponse) return errorResponse

  const record = getOrCreateUserRecord(user.id, user.email)
  return NextResponse.json({
    status: 'success',
    preferences: record.preferences,
    university: record.preferences.university,
    semester: record.preferences.semester,
    studyStreakDays: record.studyStreakDays
  })
}

export async function POST(req: NextRequest) {
  const { user, errorResponse } = await getApiSession()
  if (errorResponse) return errorResponse

  try {
    const body = await req.json()
    const updated = updateUserPreferences(user.id, user.email, body)
    return NextResponse.json({
      status: 'success',
      preferences: updated
    })
  } catch (error: any) {
    return NextResponse.json({ status: 'error', message: error.message }, { status: 500 })
  }
}
