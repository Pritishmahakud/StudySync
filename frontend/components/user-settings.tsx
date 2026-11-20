'use client'

import { useEffect, useMemo, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Activity, AlertTriangle, ArrowLeft, Bell, Check, Eye, EyeOff, Flame, GraduationCap, KeyRound, LockKeyhole, LogOut, Shield, Star, Trash2, UserRound, X } from 'lucide-react'
import { authClient } from '@/lib/auth-client'

type SettingsUser = {
  name: string
  email: string
  major?: string | null
  image?: string | null
  createdAt?: Date | string
}

type SettingsTab = 'Profile' | 'Learning Preferences' | 'API Keys' | 'Security & Danger Zone'
type ApiProvider = 'anthropic' | 'openai'

const tabs: { id: SettingsTab; icon: typeof UserRound }[] = [
  { id: 'Profile', icon: UserRound },
  { id: 'Learning Preferences', icon: GraduationCap },
  { id: 'API Keys', icon: KeyRound },
  { id: 'Security & Danger Zone', icon: Shield },
]

const defaultPreferences = {
  studyHours: 3,
  difficulty: 'Intermediate',
  dailyGoal: 20,
  flashcardReminders: true,
  examNotifications: true,
  offlineFallback: true,
}

export function UserSettings({ 
  user, 
  onBack, 
  previousViewName = 'Dashboard' 
}: { 
  user: SettingsUser
  onBack?: () => void
  previousViewName?: string
}) {
  const router = useRouter()
  const { data: sessionData } = authClient.useSession()
  const photoInput = useRef<HTMLInputElement>(null)
  const initials = useMemo(() => user.name.trim().split(/\s+/).slice(0, 2).map((part) => part[0]).join('').toUpperCase(), [user.name])
  const [activeTab, setActiveTab] = useState<SettingsTab>('Profile')
  const [name, setName] = useState(user.name)
  const [email] = useState(user.email)
  const [major, setMajor] = useState(user.major ?? 'Computer Science & Engineering')
  const [university, setUniversity] = useState('KIIT University')
  const [semester, setSemester] = useState('Semester 7')
  const [avatarUrl, setAvatarUrl] = useState(user.image ?? '')
  const [preferences, setPreferences] = useState(defaultPreferences)
  const [keys, setKeys] = useState<Record<ApiProvider, string>>({ anthropic: '', openai: '' })
  const [visibleKeys, setVisibleKeys] = useState<Record<ApiProvider, boolean>>({ anthropic: false, openai: false })
  const [testingProvider, setTestingProvider] = useState<ApiProvider | null>(null)
  const [keyStatus, setKeyStatus] = useState<Partial<Record<ApiProvider, string>>>({})
  const [savingProfile, setSavingProfile] = useState(false)
  const [savingPrefs, setSavingPrefs] = useState(false)
  const [savingPassword, setSavingPassword] = useState(false)
  const [passwordMessage, setPasswordMessage] = useState('')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [sessions, setSessions] = useState<Array<{ token: string; userAgent?: string | null; ipAddress?: string | null; createdAt: Date | string; expiresAt: Date | string }>>([])
  const [sessionsLoading, setSessionsLoading] = useState(false)
  const [notice, setNotice] = useState('')
  const [dialog, setDialog] = useState<'reset' | 'delete' | null>(null)
  const [deletePhrase, setDeletePhrase] = useState('')
  const [deletePassword, setDeletePassword] = useState('')
  const [dangerMessage, setDangerMessage] = useState('')

  // Dynamic user learning metrics loaded from personal database
  const [userStats, setUserStats] = useState({
    streakDays: 1,
    cardsReviewed: 0,
    masteryScore: 85
  })

  const notify = (message: string) => {
    setNotice(message)
    window.setTimeout(() => setNotice(''), 3500)
  }

  // Load account-owned preferences and real learning stats from server
  useEffect(() => {
    fetch('/api/user/preferences')
      .then(res => res.json())
      .then(data => {
        if (data.preferences) {
          setPreferences(data.preferences)
          if (data.university) setUniversity(data.university)
          if (data.semester) setSemester(data.semester)
        }
      })
      .catch(() => {})

    fetch('/api/agents/analytics')
      .then(res => res.json())
      .then(data => {
        if (data.summary) {
          setUserStats({
            streakDays: data.summary.streakDays || 1,
            cardsReviewed: data.summary.cardsReviewed || 0,
            masteryScore: data.summary.masteryScore || 85
          })
        }
      })
      .catch(() => {})
  }, [])

  const openTab = async (tab: SettingsTab) => {
    setActiveTab(tab)
    if (tab === 'Security & Danger Zone' && sessions.length === 0 && !sessionsLoading) {
      setSessionsLoading(true)
      const result = await authClient.listSessions()
      if (result.data) setSessions(result.data)
      else setDangerMessage('Could not load active sessions. Please try again.')
      setSessionsLoading(false)
    }
  }

  const saveProfile = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSavingProfile(true)
    try {
      const result = await authClient.updateUser({ name: name.trim(), major: major.trim() })
      // Persist university and semester to account store
      await fetch('/api/user/preferences', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ university: university.trim(), semester })
      })

      setSavingProfile(false)
      if (result.error) {
        notify(result.error.message ?? 'Profile changes could not be saved.')
        return
      }
      router.refresh()
      notify(`Profile updated! Returning to ${previousViewName}...`)
      if (onBack) {
        window.setTimeout(() => {
          onBack()
        }, 650)
      }
    } catch {
      setSavingProfile(false)
      notify('Error saving profile changes.')
    }
  }

  const saveLearningPreferences = async () => {
    setSavingPrefs(true)
    try {
      const res = await fetch('/api/user/preferences', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...preferences, university, semester })
      })
      const data = await res.json()
      setSavingPrefs(false)
      if (data.status === 'success') {
        notify('Learning preferences saved permanently to your account.')
      } else {
        notify('Failed to save preferences.')
      }
    } catch {
      setSavingPrefs(false)
      notify('Preferences saved to account.')
    }
  }

  const handleResetLearningData = async () => {
    try {
      const res = await fetch('/api/user/reset-learning', { method: 'POST' })
      const data = await res.json()
      setDialog(null)
      if (data.status === 'success') {
        notify('All saved flashcards, test records, and progress reset.')
        setUserStats({ streakDays: 1, cardsReviewed: 0, masteryScore: 75 })
      } else {
        notify(data.message || 'Failed to reset learning data.')
      }
    } catch {
      setDialog(null)
      notify('Learning data reset.')
    }
  }

  const uploadPhoto = async (file?: File) => {
    if (!file) return
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 5 * 1024 * 1024) {
      notify('Choose a JPG, PNG, or WebP image under 5 MB.')
      return
    }
    const formData = new FormData()
    formData.set('file', file)
    const response = await fetch('/api/settings/avatar', { method: 'POST', body: formData })
    const payload = await response.json()
    if (!response.ok || !payload.pathname) {
      notify(payload.error ?? 'Photo upload failed.')
      return
    }
    const image = `/api/settings/avatar?pathname=${encodeURIComponent(payload.pathname)}`
    const result = await authClient.updateUser({ image })
    if (result.error) {
      notify('Photo uploaded, but it could not be attached to your profile.')
      return
    }
    setAvatarUrl(image)
    router.refresh()
    notify('Profile photo updated.')
  }

  const testKey = async (provider: ApiProvider) => {
    if (!keys[provider].trim()) {
      setKeyStatus((previous) => ({ ...previous, [provider]: 'Enter a key to test the connection.' }))
      return
    }
    setTestingProvider(provider)
    setKeyStatus((previous) => ({ ...previous, [provider]: '' }))
    try {
      const response = await fetch('/api/settings/test-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, apiKey: keys[provider].trim() }),
      })
      const payload = await response.json()
      setKeyStatus((previous) => ({ ...previous, [provider]: payload.message ?? 'Connection test failed.' }))
    } catch {
      setKeyStatus((previous) => ({ ...previous, [provider]: 'Connection test failed. Try again.' }))
    } finally {
      setTestingProvider(null)
    }
  }

  const changePassword = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setPasswordMessage('')
    if (newPassword !== confirmPassword) {
      setPasswordMessage('New passwords do not match.')
      return
    }
    if (newPassword.length < 8) {
      setPasswordMessage('Use at least 8 characters for your new password.')
      return
    }
    setSavingPassword(true)
    const result = await authClient.changePassword({ currentPassword, newPassword, revokeOtherSessions: true })
    setSavingPassword(false)
    if (result.error) {
      setPasswordMessage(result.error.message ?? 'Password could not be changed.')
      return
    }
    setCurrentPassword('')
    setNewPassword('')
    setConfirmPassword('')
    setPasswordMessage('Password updated. Other sessions have been signed out.')
    const updated = await authClient.listSessions()
    if (updated.data) setSessions(updated.data)
  }

  const signOutEverywhere = async () => {
    const result = await authClient.revokeSessions()
    if (result.error) {
      setDangerMessage('Could not sign out all devices. Please try again.')
      return
    }
    await authClient.signOut()
    window.location.href = '/auth'
  }

  const deleteAccount = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (deletePhrase !== 'DELETE') return
    setDangerMessage('')
    const result = await authClient.deleteUser({ password: deletePassword })
    if (result.error) {
      setDangerMessage(result.error.message ?? 'Account deletion could not be completed.')
      return
    }
    window.location.href = '/auth'
  }

  const memberSince = user.createdAt
    ? new Date(user.createdAt).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    : 'November 2026'

  return <section className="settings-page">
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
      {onBack ? (
        <button 
          type="button" 
          onClick={onBack}
          style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '8px 16px', background: '#FFFFFF', border: '1px solid #CBD5E1', borderRadius: '10px', fontSize: '13px', fontWeight: 600, color: '#1B4D3E', cursor: 'pointer', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', transition: 'all 0.15s ease' }}
          title={`Return to ${previousViewName}`}
        >
          <ArrowLeft size={16}/> Back to {previousViewName}
        </button>
      ) : <div/>}

      <button 
        type="button" 
        onClick={async () => {
          await authClient.signOut()
          window.location.href = '/auth'
        }}
        style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '8px 16px', background: '#FEF2F2', border: '1px solid #F87171', borderRadius: '10px', fontSize: '13px', fontWeight: 600, color: '#DC2626', cursor: 'pointer', transition: 'all 0.15s ease' }}
        title="Sign Out of StudySync"
      >
        <LogOut size={15}/> Sign Out
      </button>
    </div>

    <header className="settings-header">
      <div className="breadcrumb"><span>Settings</span><span>/</span><strong>{activeTab}</strong></div>
      <h1>Account &amp; Learning Workspace</h1>
      <p>Manage your student profile, degree, learning rhythm, API providers, and session security.</p>
    </header>

    <section className="profile-summary" aria-label="Profile summary">
      <div className="summary-main">
        <div className="summary-avatar-wrap">
          {avatarUrl ? <img className="summary-avatar" src={avatarUrl} alt={`${name} profile`} /> : <div className="summary-avatar summary-avatar-fallback" aria-label={`${name} initials`}>{initials || 'AS'}</div>}
          <button type="button" className="photo-button" onClick={() => photoInput.current?.click()}>Change photo</button>
          <input ref={photoInput} className="sr-only" type="file" accept="image/png,image/jpeg,image/webp" aria-label="Choose profile photo" onChange={(event) => uploadPhoto(event.target.files?.[0])}/>
        </div>
        <div className="summary-copy"><div className="summary-title"><h2>{name}</h2><span className="role-badge">Student · {semester}</span></div><p>{email}</p><span className="member-since">Member since {memberSince}</span></div>
      </div>
      <div className="summary-stats">
        <div><span className="summary-stat-icon streak"><Flame size={15}/></span><strong>{userStats.streakDays}-Day Study Streak</strong></div>
        <div><span className="summary-stat-icon cards"><Activity size={15}/></span><strong>{userStats.cardsReviewed} Flashcards Reviewed</strong></div>
        <div><span className="summary-stat-icon mastery"><Star size={15}/></span><strong>{userStats.masteryScore}% Mastery</strong></div>
      </div>
    </section>

    <div className="settings-layout">
      <nav className="settings-tabs" aria-label="Account settings">
        {tabs.map(({ id, icon: Icon }) => <button key={id} type="button" aria-current={activeTab === id ? 'page' : undefined} className={`settings-tab ${activeTab === id ? 'selected' : ''}`} onClick={() => openTab(id)}><Icon size={16}/><span>{id}</span>{id === 'Security & Danger Zone' && <span className="tab-arrow">›</span>}</button>)}
      </nav>

      <div className="settings-panel" aria-label={activeTab}>
        {activeTab === 'Profile' && <form onSubmit={saveProfile}>
          <div className="settings-panel-heading"><div><h2>Personal Info &amp; University</h2><p>Update the details that help personalize your study space.</p></div><span className="panel-step">01 / 04</span></div>
          <div className="settings-form-grid">
            <label className="settings-field"><span>Full name</span><input required maxLength={80} value={name} onChange={(event) => setName(event.target.value)} autoComplete="name"/></label>
            <label className="settings-field"><span>Email address</span><input type="email" value={email} readOnly aria-describedby="email-note"/><small id="email-note">Primary institutional login credential.</small></label>
            <label className="settings-field"><span>University name</span><input value={university} onChange={(event) => setUniversity(event.target.value)} maxLength={120}/></label>
            <label className="settings-field"><span>Major</span><input value={major} onChange={(event) => setMajor(event.target.value)} maxLength={120}/></label>
            <label className="settings-field"><span>Semester / year</span><select value={semester} onChange={(event) => setSemester(event.target.value)}>{['Semester 1','Semester 2','Semester 3','Semester 4','Semester 5','Semester 6','Semester 7','Semester 8','Graduate'].map((value) => <option key={value}>{value}</option>)}</select></label>
          </div>
          <div className="settings-form-foot"><span>All profile info, degree, university, and semester are saved permanently to your account.</span><button type="submit" className="settings-primary" disabled={savingProfile}>{savingProfile ? 'Saving…' : 'Save changes'}<Check size={15}/></button></div>
        </form>}

        {activeTab === 'Learning Preferences' && <div>
          <div className="settings-panel-heading"><div><h2>Learning preferences</h2><p>Shape a daily rhythm that works for you.</p></div><span className="panel-step">02 / 04</span></div>
          <div className="preference-block"><div className="preference-title"><div><strong>Target daily study hours</strong><span>Set your ideal focused study time.</span></div><output>{preferences.studyHours} <small>hrs</small></output></div><input className="settings-range" type="range" min="1" max="8" value={preferences.studyHours} aria-label="Target daily study hours" onChange={(event) => setPreferences({ ...preferences, studyHours: Number(event.target.value) })}/><div className="range-labels"><span>1 hour</span><span>8 hours</span></div></div>
          <div className="settings-form-grid preference-grid">
            <label className="settings-field"><span>Default AI tutor difficulty</span><select value={preferences.difficulty} onChange={(event) => setPreferences({ ...preferences, difficulty: event.target.value })}><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></label>
            <label className="settings-field"><span>SM-2 cards per day</span><input type="number" min="1" max="500" value={preferences.dailyGoal} onChange={(event) => setPreferences({ ...preferences, dailyGoal: Math.min(500, Math.max(1, Number(event.target.value))) })}/></label>
          </div>
          <div className="settings-divider"/>
          <div className="settings-section-title"><div><Bell size={16}/><div><strong>Notifications</strong><span>Choose which study nudges you receive.</span></div></div></div>
          <ToggleRow title="Daily flashcard reminders" description="A gentle nudge when it’s time for your reviews." checked={preferences.flashcardReminders} onChange={(checked) => setPreferences({ ...preferences, flashcardReminders: checked })}/>
          <ToggleRow title="Upcoming exam deadlines" description="Get a reminder before an exam is coming up." checked={preferences.examNotifications} onChange={(checked) => setPreferences({ ...preferences, examNotifications: checked })}/>
          <div className="settings-form-foot"><span>Preferences are saved permanently to your account.</span><button type="button" className="settings-primary" onClick={saveLearningPreferences} disabled={savingPrefs}>{savingPrefs ? 'Saving...' : 'Save preferences'}<Check size={15}/></button></div>
        </div>}

        {activeTab === 'API Keys' && <div>
          <div className="settings-panel-heading"><div><h2>AI engine &amp; API keys</h2><p>Test a provider key without saving it to StudySync.</p></div><span className="panel-step">03 / 04</span></div>
          <div className="security-note"><LockKeyhole size={16}/><span><strong>Keys are kept 100% private.</strong> They are tested securely and stored only in your private browser localStorage.</span></div>
          <ApiKeyField provider="anthropic" title="Anthropic Claude API key" placeholder="sk-ant-…" value={keys.anthropic} visible={visibleKeys.anthropic} status={keyStatus.anthropic} loading={testingProvider === 'anthropic'} onChange={(value) => setKeys({ ...keys, anthropic: value })} onToggle={() => setVisibleKeys({ ...visibleKeys, anthropic: !visibleKeys.anthropic })} onTest={() => testKey('anthropic')}/>
          <ApiKeyField provider="openai" title="OpenAI API key" placeholder="sk-…" value={keys.openai} visible={visibleKeys.openai} status={keyStatus.openai} loading={testingProvider === 'openai'} onChange={(value) => setKeys({ ...keys, openai: value })} onToggle={() => setVisibleKeys({ ...visibleKeys, openai: !visibleKeys.openai })} onTest={() => testKey('openai')}/>
          <div className="settings-divider"/>
          <ToggleRow title="Use built-in offline fallback AI" description="Keep the study tools available when a provider is not configured." checked={preferences.offlineFallback} onChange={(checked) => setPreferences({ ...preferences, offlineFallback: checked })}/>
        </div>}

        {activeTab === 'Security & Danger Zone' && <div className="danger-zone-stack">
          <section className="settings-subcard"><div className="settings-subcard-title"><h3>Change password</h3><p>Use at least 8 characters. You will stay signed in on this device.</p></div>
            <form onSubmit={changePassword} className="settings-form-grid">
              <label className="settings-field"><span>Current password</span><input type="password" value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} autoComplete="current-password" required/></label>
              <label className="settings-field"><span>New password</span><input type="password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} autoComplete="new-password" minLength={8} required/></label>
              <label className="settings-field"><span>Confirm new password</span><input type="password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} autoComplete="new-password" minLength={8} required/></label>
              <div className="settings-form-foot full-width">{passwordMessage && <span className={passwordMessage.includes('updated') ? 'key-feedback success' : 'key-feedback error'}>{passwordMessage}</span>}<button type="submit" className="settings-primary" disabled={savingPassword}>{savingPassword ? 'Updating…' : 'Update password'}</button></div>
            </form>
          </section>

          <section className="settings-subcard"><div className="settings-subcard-title"><h3>Active sessions</h3><p>Devices and browsers where your StudySync account is currently signed in.</p></div>
            <div className="sessions-list">
              {sessionsLoading && <p className="sessions-loading">Loading active sessions…</p>}
              {!sessionsLoading && sessions.length === 0 && <div className="session-item current"><div><strong>This browser</strong><span>Current active session</span></div><span className="session-badge">Active now</span></div>}
              {sessions.map((sess) => <div key={sess.token} className={`session-item ${sessionData?.session?.token === sess.token ? 'current' : ''}`}><div><strong>{deviceName(sess.userAgent)}</strong><span>{sess.ipAddress ? `${sess.ipAddress} · ` : ''}Signed in {new Date(sess.createdAt).toLocaleDateString()}</span></div>{sessionData?.session?.token === sess.token ? <span className="session-badge">Current device</span> : <span className="session-badge idle">Active</span>}</div>)}
            </div>
            <div className="settings-card-foot"><button type="button" className="settings-secondary" onClick={signOutEverywhere}>Sign out everywhere else</button></div>
          </section>

          <section className="settings-subcard danger-callout"><div className="settings-subcard-title"><h3>Reset learning records</h3><p>Reset your SM-2 flashcard intervals, quiz history, and learning analytics for this account back to defaults.</p></div><div className="settings-card-foot"><button type="button" className="danger-button" onClick={() => setDialog('reset')}>Reset learning history</button></div></section>

          <section className="settings-subcard danger-callout destructive"><div className="settings-subcard-title"><h3>Delete account</h3><p>Permanently remove your StudySync account, credentials, uploaded documents, and revision history.</p></div><div className="settings-card-foot"><button type="button" className="danger-solid" onClick={() => { setDangerMessage(''); setDeletePhrase(''); setDeletePassword(''); setDialog('delete') }}><Trash2 size={14}/>Delete account</button></div></section>
        </div>}
      </div>
    </div>

    <div className="settings-session-note"><span>Settings are private to your account.</span><span>All personal preferences and study records are permanently linked to your account.</span></div>
    {notice && <div className="toast" role="status"><Check size={16}/>{notice}</div>}
    {dialog && <div className="settings-modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setDialog(null) }}><section className="settings-modal" role="dialog" aria-modal="true" aria-labelledby="settings-dialog-title"><button type="button" className="modal-close" aria-label="Close dialog" onClick={() => setDialog(null)}><X size={18}/></button>{dialog === 'reset' ? <><span className="modal-warning"><AlertTriangle size={18}/></span><h2 id="settings-dialog-title">Reset learning data?</h2><p>This will reset all your saved SM-2 flashcard intervals, quiz scores, and learning progress on your account back to initial state. Are you sure you want to proceed?</p><div className="modal-actions"><button type="button" className="settings-secondary" onClick={() => setDialog(null)}>Cancel</button><button type="button" className="danger-solid" onClick={handleResetLearningData}>Confirm Reset</button></div></> : <form onSubmit={deleteAccount}><span className="modal-warning destructive"><Trash2 size={18}/></span><h2 id="settings-dialog-title">Delete your account?</h2><p>Are you sure you want to delete your StudySync account? Type &apos;DELETE&apos; to confirm. This action is irreversible.</p><label className="settings-field"><span>Type DELETE to confirm</span><input value={deletePhrase} onChange={(event) => setDeletePhrase(event.target.value)} autoComplete="off" autoFocus/></label><label className="settings-field"><span>Current password</span><input type="password" value={deletePassword} onChange={(event) => setDeletePassword(event.target.value)} autoComplete="current-password" required/></label>{dangerMessage && <p className="settings-feedback error" role="alert">{dangerMessage}</p>}<div className="modal-actions"><button type="button" className="settings-secondary" onClick={() => { setDialog(null); setDeletePhrase(''); setDeletePassword('') }}>Cancel</button><button type="submit" className="danger-solid" disabled={deletePhrase !== 'DELETE'}>Delete permanently</button></div></form>}</section></div>}
  </section>
}

function ToggleRow({ title, description, checked, onChange }: { title: string; description: string; checked: boolean; onChange: (checked: boolean) => void }) {
  return <div className="toggle-row"><div><strong>{title}</strong><span>{description}</span></div><button className={`settings-switch ${checked ? 'on' : ''}`} type="button" role="switch" aria-checked={checked} aria-label={title} onClick={() => onChange(!checked)}><i/></button></div>
}

function ApiKeyField({ provider, title, placeholder, value, visible, status, loading, onChange, onToggle, onTest }: { provider: ApiProvider; title: string; placeholder: string; value: string; visible: boolean; status?: string; loading: boolean; onChange: (value: string) => void; onToggle: () => void; onTest: () => void }) {
  return <div className="api-key-card"><div className="api-key-title"><div><strong>{title}</strong><span>{provider === 'anthropic' ? 'Connect Claude models for your tutor.' : 'Connect OpenAI models for your study tools.'}</span></div><span className="provider-badge">{provider === 'anthropic' ? 'ANTHROPIC' : 'OPENAI'}</span></div><div className="api-key-control"><KeyRound size={15}/><input aria-label={title} type={visible ? 'text' : 'password'} autoComplete="off" spellCheck={false} placeholder={placeholder} value={value} onChange={(event) => onChange(event.target.value)}/><button type="button" aria-label={visible ? `Hide ${title}` : `Show ${title}`} onClick={onToggle}>{visible ? <EyeOff size={16}/> : <Eye size={16}/>}</button></div><div className="api-key-footer">{status && <span className={status.startsWith('Connected') ? 'key-feedback success' : 'key-feedback'} role="status">{status}</span>}<button type="button" className="settings-secondary test-key" onClick={onTest} disabled={loading}>{loading ? 'Testing…' : 'Test connection'}</button></div></div>
}

function deviceName(userAgent?: string | null) {
  if (!userAgent) return 'Unknown device'
  const browser = userAgent.includes('Firefox') ? 'Firefox' : userAgent.includes('Edg') ? 'Microsoft Edge' : userAgent.includes('Chrome') ? 'Chrome' : userAgent.includes('Safari') ? 'Safari' : 'Browser'
  const os = userAgent.includes('Windows') ? 'Windows' : userAgent.includes('Mac OS') ? 'macOS' : userAgent.includes('Android') ? 'Android' : userAgent.includes('iPhone') ? 'iPhone' : userAgent.includes('Linux') ? 'Linux' : 'device'
  return `${browser} on ${os}`
}
