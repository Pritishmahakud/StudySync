import { NextRequest, NextResponse } from 'next/server'
import { getApiSession } from '@/lib/api-auth'
import fs from 'fs'
import path from 'path'
import { hashPassword, verifyPassword } from 'better-auth/crypto'

const dataDir = path.resolve(process.cwd(), '..', 'data')
const storeFile = path.join(dataDir, 'auth_store.json')

function readAuthStore(): any {
  if (fs.existsSync(storeFile)) {
    try {
      return JSON.parse(fs.readFileSync(storeFile, 'utf-8'))
    } catch {}
  }
  return { user: [], session: [], account: [], verification: [] }
}

function writeAuthStore(store: any) {
  try {
    fs.writeFileSync(storeFile, JSON.stringify(store, null, 2), 'utf-8')
    const g = globalThis as any
    if (g.__studysync_db) {
      g.__studysync_db.user = store.user
      g.__studysync_db.session = store.session
      g.__studysync_db.account = store.account
      g.__studysync_db.verification = store.verification
    }
  } catch {}
}

export async function POST(req: NextRequest) {
  const { user, errorResponse } = await getApiSession()
  if (errorResponse) return errorResponse

  try {
    const body = await req.json()
    const currentPassword = (body.currentPassword || '').trim()
    const newEmail = (body.newEmail || '').trim().toLowerCase()
    const newPassword = (body.newPassword || '').trim()

    if (!currentPassword) {
      return NextResponse.json({ status: 'error', message: 'Current password is required to verify identity.' }, { status: 400 })
    }

    const store = readAuthStore()
    const account = store.account.find((a: any) => a.userId === user.id)

    if (!account) {
      return NextResponse.json({ status: 'error', message: 'User account credential not found.' }, { status: 404 })
    }

    const isCurrentValid = await verifyPassword({ hash: account.password, password: currentPassword })
    if (!isCurrentValid) {
      return NextResponse.json({ status: 'error', message: 'Current password does not match.' }, { status: 401 })
    }

    const userObj = store.user.find((u: any) => u.id === user.id)
    if (!userObj) {
      return NextResponse.json({ status: 'error', message: 'User profile record not found.' }, { status: 404 })
    }

    if (newEmail && newEmail !== userObj.email.toLowerCase()) {
      // Check if another user has this email
      const existing = store.user.find((u: any) => u.id !== user.id && u.email.toLowerCase() === newEmail)
      if (existing) {
        return NextResponse.json({ status: 'error', message: 'That email is already registered to another student.' }, { status: 409 })
      }
      userObj.email = newEmail
      userObj.updatedAt = new Date().toISOString()
    }

    if (newPassword) {
      if (newPassword.length < 8) {
        return NextResponse.json({ status: 'error', message: 'New password must be at least 8 characters long.' }, { status: 400 })
      }
      account.password = await hashPassword(newPassword)
      account.updatedAt = new Date().toISOString()
    }

    writeAuthStore(store)

    return NextResponse.json({
      status: 'success',
      message: 'Account credentials updated successfully.',
      user: {
        id: userObj.id,
        name: userObj.name,
        email: userObj.email,
        major: userObj.major
      }
    })
  } catch (error: any) {
    return NextResponse.json({ status: 'error', message: error.message }, { status: 500 })
  }
}
