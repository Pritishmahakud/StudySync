import { get, put } from '@vercel/blob'
import { headers } from 'next/headers'
import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth'

const MAX_AVATAR_BYTES = 5 * 1024 * 1024
const imageTypes: Record<string, string> = {
  'image/jpeg': 'jpg',
  'image/png': 'png',
  'image/webp': 'webp',
}

export async function POST(request: NextRequest) {
  const session = await auth.api.getSession({ headers: await headers() })
  if (!session?.user) return NextResponse.json({ error: 'Sign in to update your profile photo.' }, { status: 401 })

  const contentLength = Number(request.headers.get('content-length') ?? 0)
  if (contentLength > MAX_AVATAR_BYTES + 64 * 1024) {
    return NextResponse.json({ error: 'Choose an image under 5 MB.' }, { status: 413 })
  }

  const formData = await request.formData()
  const file = formData.get('file')
  if (!(file instanceof File) || !imageTypes[file.type] || file.size > MAX_AVATAR_BYTES) {
    return NextResponse.json({ error: 'Choose a JPG, PNG, or WebP image under 5 MB.' }, { status: 400 })
  }

  try {
    const blob = await put(`avatars/${session.user.id}/${crypto.randomUUID()}.${imageTypes[file.type]}`, file, {
      access: 'private',
      contentType: file.type,
      addRandomSuffix: true,
    })
    return NextResponse.json({ pathname: blob.pathname })
  } catch {
    return NextResponse.json({ error: 'Photo upload failed. Please try again.' }, { status: 503 })
  }
}

export async function GET(request: NextRequest) {
  const session = await auth.api.getSession({ headers: await headers() })
  if (!session?.user) return NextResponse.json({ error: 'Sign in to view this photo.' }, { status: 401 })

  const pathname = request.nextUrl.searchParams.get('pathname')
  if (!pathname || !pathname.startsWith(`avatars/${session.user.id}/`)) {
    return NextResponse.json({ error: 'Photo not found.' }, { status: 404 })
  }

  try {
    const result = await get(pathname, {
      access: 'private',
      ifNoneMatch: request.headers.get('if-none-match') ?? undefined,
    })
    if (!result) return NextResponse.json({ error: 'Photo not found.' }, { status: 404 })
    if (result.statusCode === 304) {
      return new NextResponse(null, {
        status: 304,
        headers: { ETag: result.blob.etag, 'Cache-Control': 'private, no-cache' },
      })
    }
    return new NextResponse(result.stream, {
      headers: {
        'Content-Type': result.blob.contentType,
        ETag: result.blob.etag,
        'Cache-Control': 'private, no-cache',
        'X-Content-Type-Options': 'nosniff',
      },
    })
  } catch {
    return NextResponse.json({ error: 'Photo could not be loaded.' }, { status: 503 })
  }
}
