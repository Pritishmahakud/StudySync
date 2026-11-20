import { NextRequest, NextResponse } from 'next/server'
import { getApiSession } from '@/lib/api-auth'
import { invokePythonBridge } from '@/lib/bridge'

export async function GET() {
  const { user, errorResponse } = await getApiSession()
  if (errorResponse) return errorResponse

  try {
    const result = await invokePythonBridge('planner_schedule', {
      hours_per_day: 3.0,
      user_id: user.id,
      email: user.email,
    })
    return NextResponse.json(result)
  } catch (error: any) {
    return NextResponse.json({ status: 'error', message: error.message }, { status: 500 })
  }
}

export async function POST(req: NextRequest) {
  const { user, errorResponse } = await getApiSession()
  if (errorResponse) return errorResponse

  try {
    const body = await req.json()
    const result = await invokePythonBridge('planner_schedule', {
      ...body,
      user_id: user.id,
      email: user.email,
    })
    return NextResponse.json(result)
  } catch (error: any) {
    return NextResponse.json({ status: 'error', message: error.message }, { status: 500 })
  }
}
