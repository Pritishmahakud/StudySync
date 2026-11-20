import fs from 'fs'
import path from 'path'
import { betterAuth } from 'better-auth'
import { memoryAdapter } from 'better-auth/adapters/memory'
import { pool } from './db'

if (process.env.NODE_ENV === 'production') {
  if (!process.env.DATABASE_URL) throw new Error('DATABASE_URL must be configured for production authentication.')
  if (!process.env.BETTER_AUTH_SECRET || process.env.BETTER_AUTH_SECRET.length < 32) {
    throw new Error('Set BETTER_AUTH_SECRET to a random value of at least 32 characters in production.')
  }
}

// Path to persistent auth store on disk
const storeDir = path.resolve(process.cwd(), '..', 'data')
const storeFile = path.join(storeDir, 'auth_store.json')

function getPersistentStore() {
  if (!fs.existsSync(storeDir)) {
    try {
      fs.mkdirSync(storeDir, { recursive: true })
    } catch {}
  }
  if (fs.existsSync(storeFile)) {
    try {
      const content = fs.readFileSync(storeFile, 'utf-8')
      const parsed = JSON.parse(content)
      if (
        Array.isArray(parsed.user) &&
        Array.isArray(parsed.session) &&
        Array.isArray(parsed.account) &&
        Array.isArray(parsed.verification)
      ) {
        return parsed
      }
    } catch {}
  }
  const fresh = {
    user: [],
    session: [],
    account: [],
    verification: [],
  }
  try {
    fs.writeFileSync(storeFile, JSON.stringify(fresh, null, 2), 'utf-8')
  } catch {}
  return fresh
}

function persistStore(store: any) {
  try {
    if (!fs.existsSync(storeDir)) {
      fs.mkdirSync(storeDir, { recursive: true })
    }
    fs.writeFileSync(storeFile, JSON.stringify(store, null, 2), 'utf-8')
  } catch {}
}

const g = globalThis as any
if (!(process.env.DATABASE_URL && pool) && !g.__studysync_db) {
  g.__studysync_db = getPersistentStore()
  // Auto-sync disk persistence every 2 seconds
  if (!g.__studysync_interval) {
    g.__studysync_interval = setInterval(() => {
      if (g.__studysync_db) {
        persistStore(g.__studysync_db)
      }
    }, 2000)
  }
}

const dbStore = g.__studysync_db

export const auth = betterAuth({
  database: process.env.DATABASE_URL && pool ? pool : memoryAdapter(dbStore),
  secret: process.env.BETTER_AUTH_SECRET || 'local-development-only-studysync-secret',
  baseURL:
    process.env.BETTER_AUTH_URL ??
    (process.env.VERCEL_PROJECT_PRODUCTION_URL
      ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`
      : process.env.VERCEL_URL
        ? `https://${process.env.VERCEL_URL}`
        : process.env.V0_RUNTIME_URL ?? 'http://localhost:3000'),
  emailAndPassword: {
    enabled: true,
    autoSignIn: true,
  },
  user: {
    deleteUser: {
      enabled: true,
    },
    additionalFields: {
      major: {
        type: 'string',
        required: false,
        input: true,
      },
    },
  },
  trustedOrigins: [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    ...(process.env.V0_RUNTIME_URL ? [process.env.V0_RUNTIME_URL] : []),
    ...(process.env.V0_DEV_APP_URL ? [process.env.V0_DEV_APP_URL] : []),
    ...(process.env.V0_BUILD_URL ? [process.env.V0_BUILD_URL] : []),
    ...(process.env.V0_SANDBOX_URL ? [process.env.V0_SANDBOX_URL] : []),
    ...(process.env.VERCEL_URL ? [`https://${process.env.VERCEL_URL}`] : []),
    ...(process.env.VERCEL_PROJECT_PRODUCTION_URL
      ? [`https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`]
      : []),
  ],
  session: {
    expiresIn: 60 * 60 * 24 * 7,
    updateAge: 60 * 60 * 24,
  },
})
