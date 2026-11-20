import fs from 'fs'
import path from 'path'

export interface UserPreferences {
  studyHours: number
  difficulty: string
  dailyGoal: number
  flashcardReminders: boolean
  examNotifications: boolean
  offlineFallback: boolean
  university: string
  semester: string
}

export interface UserFlashcard {
  id: string
  front: string
  back: string
  hint?: string
  concept: string
  repetition: number
  interval: number
  easiness_factor: number
  next_review_date: string
  last_reviewed?: string
}

export interface UserQuizAttempt {
  id: string
  topic: string
  score: number
  total: number
  percentage: number
  difficulty: string
  timestamp: string
}

export interface UserDocument {
  id: string
  fileName: string
  title: string
  summary: string
  domain: string
  keyTakeaways: string[]
  modules: any[]
  quiz: any[]
  flashcards: any[]
  uploadedAt: string
}

export interface UserSubscription {
  tier: 'free' | 'pro'
  active: boolean
  planName: string
  billingCycle: 'monthly' | 'yearly' | 'lifetime'
  features: string[]
  updatedAt: string
}

export interface UserLearningRecord {
  userId: string
  email: string
  preferences: UserPreferences
  flashcards: UserFlashcard[]
  quizAttempts: UserQuizAttempt[]
  documents: UserDocument[]
  subscription: UserSubscription
  studyStreakDays: number
  lastActiveDate: string
}

const dataDir = path.resolve(process.cwd(), '..', 'data')
const learningStoreFile = path.join(dataDir, 'user_learning_store.json')

function ensureDir() {
  if (!fs.existsSync(dataDir)) {
    try {
      fs.mkdirSync(dataDir, { recursive: true })
    } catch {}
  }
}

function readAllRecords(): Record<string, UserLearningRecord> {
  ensureDir()
  if (fs.existsSync(learningStoreFile)) {
    try {
      const content = fs.readFileSync(learningStoreFile, 'utf-8')
      return JSON.parse(content)
    } catch {
      return {}
    }
  }
  return {}
}

function writeAllRecords(records: Record<string, UserLearningRecord>) {
  ensureDir()
  try {
    fs.writeFileSync(learningStoreFile, JSON.stringify(records, null, 2), 'utf-8')
  } catch {}
}

const DEFAULT_PREFERENCES: UserPreferences = {
  studyHours: 3,
  difficulty: 'Intermediate',
  dailyGoal: 20,
  flashcardReminders: true,
  examNotifications: true,
  offlineFallback: true,
  university: 'Kalinga Institute of Industrial Technology (KIIT)',
  semester: 'Semester 7',
}

const INITIAL_STARTER_CARDS: UserFlashcard[] = [
  {
    id: 'card-1',
    front: 'What makes a schedule conflict-serializable in Two-Phase Locking (2PL)?',
    back: 'A schedule is conflict-serializable if its precedence serialization graph contains no directed cycles, guaranteed by forbidding lock acquisition after the first lock release.',
    hint: 'Think about the shrinking phase rule.',
    concept: 'Database Concurrency Control',
    repetition: 1,
    interval: 1,
    easiness_factor: 2.5,
    next_review_date: new Date().toISOString().split('T')[0],
  },
  {
    id: 'card-2',
    front: 'What is the primary condition for a relation to be in Boyce-Codd Normal Form (BCNF)?',
    back: 'For every non-trivial functional dependency X -> Y, X must be a superkey of the relation schema.',
    hint: 'Strict superkey requirement.',
    concept: 'Database Normalization',
    repetition: 1,
    interval: 1,
    easiness_factor: 2.5,
    next_review_date: new Date().toISOString().split('T')[0],
  },
  {
    id: 'card-3',
    front: 'What core guarantee does the Raft consensus algorithm provide across distributed nodes?',
    back: 'State Machine Safety: if a leader applies a log entry at a given index, no other server will ever apply a different entry for that index.',
    hint: 'Log commitment and leader election safety.',
    concept: 'Distributed Systems Consensus',
    repetition: 0,
    interval: 0,
    easiness_factor: 2.5,
    next_review_date: new Date().toISOString().split('T')[0],
  },
]

export function getOrCreateUserRecord(userId: string, email: string): UserLearningRecord {
  const records = readAllRecords()
  const key = userId || email || 'default_user'

  if (records[key]) {
    return records[key]
  }

  const newRecord: UserLearningRecord = {
    userId: key,
    email: email || key,
    preferences: { ...DEFAULT_PREFERENCES },
    flashcards: [...INITIAL_STARTER_CARDS],
    quizAttempts: [],
    documents: [],
    subscription: {
      tier: 'free',
      active: true,
      planName: 'StudySync Student Free',
      billingCycle: 'monthly',
      features: ['Standard AI Tutor', 'Core Flashcards', '3 Document Uploads/mo', 'Community PYQs'],
      updatedAt: new Date().toISOString(),
    },
    studyStreakDays: 1,
    lastActiveDate: new Date().toISOString().split('T')[0],
  }

  records[key] = newRecord
  writeAllRecords(records)
  return newRecord
}

export function updateUserPreferences(userId: string, email: string, prefs: Partial<UserPreferences>): UserPreferences {
  const records = readAllRecords()
  const key = userId || email || 'default_user'
  const record = records[key] || getOrCreateUserRecord(key, email)

  record.preferences = { ...record.preferences, ...prefs }
  records[key] = record
  writeAllRecords(records)
  return record.preferences
}

export function getUserFlashcards(userId: string, email: string): UserFlashcard[] {
  const record = getOrCreateUserRecord(userId, email)
  return record.flashcards || []
}

export function reviewUserFlashcard(
  userId: string,
  email: string,
  cardId: string,
  rating: number // 0 to 5 SM-2 rating
): UserFlashcard | null {
  const records = readAllRecords()
  const key = userId || email || 'default_user'
  const record = records[key] || getOrCreateUserRecord(key, email)

  const card = record.flashcards.find((c) => c.id === cardId)
  if (!card) return null

  // SuperMemo SM-2 algorithm calculation
  const q = Math.max(0, Math.min(5, rating))
  if (q >= 3) {
    if (card.repetition === 0) {
      card.interval = 1
    } else if (card.repetition === 1) {
      card.interval = 6
    } else {
      card.interval = Math.round(card.interval * card.easiness_factor)
    }
    card.repetition += 1
  } else {
    card.repetition = 0
    card.interval = 1
  }

  card.easiness_factor = Math.max(
    1.3,
    card.easiness_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
  )

  const nextDate = new Date()
  nextDate.setDate(nextDate.getDate() + Math.max(1, card.interval))
  card.next_review_date = nextDate.toISOString().split('T')[0]
  card.last_reviewed = new Date().toISOString()

  // Update activity streak
  updateUserStreak(record)

  records[key] = record
  writeAllRecords(records)
  return card
}

export function recordUserQuizAttempt(
  userId: string,
  email: string,
  attempt: Omit<UserQuizAttempt, 'id' | 'timestamp'>
): UserQuizAttempt {
  const records = readAllRecords()
  const key = userId || email || 'default_user'
  const record = records[key] || getOrCreateUserRecord(key, email)

  const newAttempt: UserQuizAttempt = {
    id: `quiz-att-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
    ...attempt,
    timestamp: new Date().toISOString(),
  }

  if (!record.quizAttempts) record.quizAttempts = []
  record.quizAttempts.unshift(newAttempt)

  updateUserStreak(record)
  records[key] = record
  writeAllRecords(records)
  return newAttempt
}

export function getUserDocuments(userId: string, email: string): UserDocument[] {
  const record = getOrCreateUserRecord(userId, email)
  return record.documents || []
}

export function saveUserDocument(userId: string, email: string, doc: Omit<UserDocument, 'id' | 'uploadedAt'>): UserDocument {
  const records = readAllRecords()
  const key = userId || email || 'default_user'
  const record = records[key] || getOrCreateUserRecord(key, email)

  const newDoc: UserDocument = {
    id: `doc-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
    ...doc,
    uploadedAt: new Date().toISOString(),
  }

  if (!record.documents) record.documents = []
  // Avoid duplicate by filename
  record.documents = record.documents.filter((d) => d.fileName !== newDoc.fileName)
  record.documents.unshift(newDoc)

  updateUserStreak(record)
  records[key] = record
  writeAllRecords(records)
  return newDoc
}

export function deleteUserDocument(userId: string, email: string, docId: string): boolean {
  const records = readAllRecords()
  const key = userId || email || 'default_user'
  const record = records[key]
  if (!record) return false

  record.documents = (record.documents || []).filter((d) => d.id !== docId && d.fileName !== docId)
  records[key] = record
  writeAllRecords(records)
  return true
}

export function getUserSubscription(userId: string, email: string): UserSubscription {
  const record = getOrCreateUserRecord(userId, email)
  return record.subscription
}

export function upgradeUserSubscription(userId: string, email: string, tier: 'free' | 'pro'): UserSubscription {
  const records = readAllRecords()
  const key = userId || email || 'default_user'
  const record = records[key] || getOrCreateUserRecord(key, email)

  record.subscription = {
    tier,
    active: true,
    planName: tier === 'pro' ? 'StudySync Pro Scholar' : 'StudySync Student Free',
    billingCycle: 'monthly',
    features: tier === 'pro'
      ? [
          'Unlimited Live AI Academic Tutoring (GPT-4o & Claude 3.5)',
          'AI Exam Paper Solver with Step-by-Step Marking Rubrics',
          'Unlimited Document Library & OCR Extraction',
          'Interactive Code Lab with Multi-Language Sandbox',
          'Export Verified Study Packs to Anki & Notion',
          'Priority GPU Inference & Instant Audio Transcripts',
        ]
      : ['Standard AI Tutor', 'Core Flashcards', '3 Document Uploads/mo', 'Community PYQs'],
    updatedAt: new Date().toISOString(),
  }

  records[key] = record
  writeAllRecords(records)
  return record.subscription
}

export function getUserAnalytics(userId: string, email: string) {
  const record = getOrCreateUserRecord(userId, email)
  const flashcards = record.flashcards || []
  const quizzes = record.quizAttempts || []

  // Real cards reviewed
  const reviewedCards = flashcards.filter((c) => c.repetition > 0)
  const totalReviewedCount = reviewedCards.reduce((acc, c) => acc + c.repetition, 0)

  // Real mastery calculation based on SM-2 factors & quiz scores
  let mastery = 75
  if (quizzes.length > 0) {
    const avgQuiz = quizzes.reduce((sum, q) => sum + q.percentage, 0) / quizzes.length
    mastery = Math.round(avgQuiz)
  } else if (reviewedCards.length > 0) {
    const avgEasiness = reviewedCards.reduce((sum, c) => sum + c.easiness_factor, 0) / reviewedCards.length
    mastery = Math.min(98, Math.round((avgEasiness / 2.5) * 85))
  }

  return {
    userId: record.userId,
    email: record.email,
    streakDays: record.studyStreakDays || 1,
    cardsReviewed: totalReviewedCount,
    masteryScore: Math.min(100, Math.max(10, mastery)),
    quizzesCompleted: quizzes.length,
    documentsCount: (record.documents || []).length,
    subscriptionTier: record.subscription.tier,
    recentQuizzes: quizzes.slice(0, 5),
    weakAreas: quizzes.filter((q) => q.percentage < 70).map((q) => q.topic),
    strongAreas: quizzes.filter((q) => q.percentage >= 80).map((q) => q.topic),
  }
}

export function resetUserLearningData(userId: string, email: string): boolean {
  const records = readAllRecords()
  const key = userId || email || 'default_user'
  if (!records[key]) return false

  records[key].flashcards = [...INITIAL_STARTER_CARDS]
  records[key].quizAttempts = []
  records[key].documents = []
  records[key].studyStreakDays = 1
  writeAllRecords(records)
  return true
}

function updateUserStreak(record: UserLearningRecord) {
  const today = new Date().toISOString().split('T')[0]
  if (record.lastActiveDate === today) return

  const lastDate = record.lastActiveDate ? new Date(record.lastActiveDate) : null
  const now = new Date(today)

  if (lastDate) {
    const diffDays = Math.round((now.getTime() - lastDate.getTime()) / (1000 * 3600 * 24))
    if (diffDays === 1) {
      record.studyStreakDays = (record.studyStreakDays || 0) + 1
    } else if (diffDays > 1) {
      record.studyStreakDays = 1
    }
  } else {
    record.studyStreakDays = 1
  }
  record.lastActiveDate = today
}
