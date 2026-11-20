import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'
import crypto from 'crypto'

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
      g.__studysync_db = store
    }
  } catch {}
}

function hashPassword(password: string): string {
  const salt = crypto.randomBytes(16).toString('hex')
  const derived = crypto.scryptSync(password, salt, 64)
  return `${salt}:${derived.toString('hex')}`
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const action = body.action || 'request_code'
    const email = (body.email || '').trim().toLowerCase()

    if (!email) {
      return NextResponse.json({ status: 'error', message: 'Email address is required.' }, { status: 400 })
    }

    const store = readAuthStore()
    const user = store.user.find((u: any) => u.email.toLowerCase() === email)

    if (!user) {
      return NextResponse.json({ status: 'error', message: 'No registered student account was found with that email address.' }, { status: 404 })
    }

    if (action === 'request_code') {
      // Generate a 6-digit verification code
      const code = Math.floor(100000 + Math.random() * 900000).toString()
      const expiresAt = new Date(Date.now() + 15 * 60 * 1000).toISOString() // 15 mins

      if (!store.verification) store.verification = []
      // Remove any existing verifications for this email
      store.verification = store.verification.filter((v: any) => v.identifier !== email)
      store.verification.push({
        id: `v-${Date.now()}`,
        identifier: email,
        value: code,
        expiresAt,
        createdAt: new Date().toISOString()
      })
      writeAuthStore(store)

      return NextResponse.json({
        status: 'success',
        message: `Verification code generated for ${email}. (Code: ${code})`,
        verificationCode: code
      })
    }

    if (action === 'reset_password') {
      const code = (body.code || '').trim()
      const newPassword = (body.newPassword || '').trim()

      if (!code) {
        return NextResponse.json({ status: 'error', message: 'Verification code is required.' }, { status: 400 })
      }
      if (!newPassword || newPassword.length < 8) {
        return NextResponse.json({ status: 'error', message: 'New password must be at least 8 characters long.' }, { status: 400 })
      }

      // Verify code
      const verification = (store.verification || []).find((v: any) => v.identifier === email && v.value === code)
      if (!verification) {
        return NextResponse.json({ status: 'error', message: 'Invalid or expired verification code.' }, { status: 400 })
      }

      if (new Date(verification.expiresAt) < new Date()) {
        return NextResponse.json({ status: 'error', message: 'Verification code has expired. Please request a new code.' }, { status: 400 })
      }

      // Find account
      const account = store.account.find((a: any) => a.userId === user.id)
      if (!account) {
        return NextResponse.json({ status: 'error', message: 'Account credential record not found.' }, { status: 404 })
      }

      // Hash and update password
      account.password = hashPassword(newPassword)
      account.updatedAt = new Date().toISOString()

      // Clean up verification
      store.verification = store.verification.filter((v: any) => v.identifier !== email)
      writeAuthStore(store)

      return NextResponse.json({
        status: 'success',
        message: 'Password reset successfully! You can now sign in with your new password.'
      })
    }

    return NextResponse.json({ status: 'error', message: 'Unknown action.' }, { status: 400 })
  } catch (error: any) {
    return NextResponse.json({ status: 'error', message: error.message }, { status: 500 })
  }
}
