import { headers } from 'next/headers'
import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth'

const keyLimit = 4096

export async function POST(request: NextRequest) {
  const session = await auth.api.getSession({ headers: await headers() })
  if (!session?.user) return NextResponse.json({ message: 'Sign in to test an API key.' }, { status: 401 })
  if (Number(request.headers.get('content-length') ?? 0) > keyLimit + 1024) {
    return NextResponse.json({ message: 'The API key is too long.' }, { status: 413 })
  }

  let body: { provider?: unknown; apiKey?: unknown }
  try {
    body = await request.json()
  } catch {
    return NextResponse.json({ message: 'Invalid request.' }, { status: 400 })
  }

  const { provider, apiKey } = body
  if ((provider !== 'anthropic' && provider !== 'openai') || typeof apiKey !== 'string' || apiKey.length > keyLimit || apiKey.length < 8) {
    return NextResponse.json({ message: 'Enter a valid provider and API key.' }, { status: 400 })
  }

  const endpoint = provider === 'anthropic'
    ? 'https://api.anthropic.com/v1/models?limit=1'
    : 'https://api.openai.com/v1/models'
  const requestHeaders: Record<string, string> = provider === 'anthropic'
    ? { 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' }
    : { Authorization: `Bearer ${apiKey}` }

  try {
    const response = await fetch(endpoint, {
      headers: requestHeaders,
      signal: AbortSignal.timeout(8000),
      cache: 'no-store',
    })
    if (response.ok) return NextResponse.json({ message: 'Connected successfully. The key remains only in this page session.' })
    if (response.status === 401 || response.status === 403) {
      return NextResponse.json({ message: 'The provider rejected this key. Check it and try again.' }, { status: 200 })
    }
    return NextResponse.json({ message: 'The provider could not validate this key right now. Try again later.' }, { status: 200 })
  } catch {
    return NextResponse.json({ message: 'Could not reach the provider. Try again later.' }, { status: 200 })
  }
}
