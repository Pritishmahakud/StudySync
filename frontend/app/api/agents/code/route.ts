import { NextRequest, NextResponse } from 'next/server'
import { getApiSession } from '@/lib/api-auth'
import { invokePythonBridge } from '@/lib/bridge'

export async function POST(req: NextRequest) {
  const { user, errorResponse } = await getApiSession()
  if (errorResponse) return errorResponse

  try {
    const body = await req.json()
    const code = (body.code || '').trim()
    const language = (body.language || 'python').toLowerCase()

    if (!code) {
      return NextResponse.json({ status: 'error', message: 'No code supplied to execute.' }, { status: 400 })
    }

    // Invoke execution engine (hybrid Python bridge or safe isolated native runner)
    const result = await invokePythonBridge('code_run', {
      code,
      language,
      user_id: user.id,
      email: user.email,
    })

    return NextResponse.json(result)
  } catch (error: any) {
    return NextResponse.json({ 
      status: 'error', 
      message: error.message || 'Execution runner encountered an error.' 
    }, { status: 500 })
  }
}
