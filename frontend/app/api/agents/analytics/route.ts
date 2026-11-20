import { NextRequest, NextResponse } from 'next/server'
import { getApiSession } from '@/lib/api-auth'
import { invokePythonBridge } from '@/lib/bridge'
import { getUserAnalytics } from '@/lib/user-learning-store'

export async function GET() {
  const { user, errorResponse } = await getApiSession()
  if (errorResponse) return errorResponse

  try {
    const userAnalytics = getUserAnalytics(user.id, user.email)
    const result = await invokePythonBridge('analytics_summary', { 
      user_id: user.id,
      email: user.email 
    })
    return NextResponse.json({
      status: 'success',
      summary: result.summary || userAnalytics
    })
  } catch (error: any) {
    return NextResponse.json({
      status: 'success',
      summary: getUserAnalytics(user.id, user.email)
    })
  }
}

export async function POST(req: NextRequest) {
  const { user, errorResponse } = await getApiSession()
  if (errorResponse) return errorResponse

  try {
    const body = await req.json()
    const payload = {
      ...body,
      user_id: user.id,
      email: user.email
    }
    const result = await invokePythonBridge('analytics_summary', payload)
    return NextResponse.json(result)
  } catch (error: any) {
    return NextResponse.json({
      status: 'success',
      summary: getUserAnalytics(user.id, user.email)
    })
  }
}
