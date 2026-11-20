import { headers } from 'next/headers'
import { NextResponse } from 'next/server'
import { auth } from '@/lib/auth'

/**
 * Validates the caller's session.
 * Returns { user, session, errorResponse: null } on success,
 * or { user: null, session: null, errorResponse: NextResponse } on 401.
 */
export async function getApiSession() {
  try {
    const session = await auth.api.getSession({ headers: await headers() })
    if (!session?.user) {
      return {
        user: null,
        session: null,
        errorResponse: NextResponse.json({ status: 'error', message: 'Sign in to use this feature.' }, { status: 401 })
      }
    }
    return {
      user: session.user,
      session,
      errorResponse: null
    }
  } catch (error) {
    return {
      user: null,
      session: null,
      errorResponse: NextResponse.json({ status: 'error', message: 'Session validation error.' }, { status: 401 })
    }
  }
}

/** Legacy backwards-compatible helper: returns 401 NextResponse if unauthenticated, null otherwise. */
export async function requireApiSession() {
  const { errorResponse } = await getApiSession()
  return errorResponse
}
