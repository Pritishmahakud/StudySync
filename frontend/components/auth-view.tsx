'use client'

import { useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowRight, BookOpen, Check, ChevronDown, Eye, EyeOff, GraduationCap, LockKeyhole, Mail, MessageSquareText, ShieldCheck, Sparkles, Star, UserRound, X, Zap } from 'lucide-react'
import { authClient } from '@/lib/auth-client'

type Mode = 'sign-in' | 'sign-up'

const majors = [
  'B.Tech Computer Science',
  'Data Science',
  'Electrical Engineering',
  'Mechanical Engineering',
  'Business Administration',
  'Psychology',
  'Other',
]
const demoEmail = 'asha@studysync.edu'
const demoPassword = 'StudySyncDemo-2026'

export function AuthView() {
  const router = useRouter()
  const [mode, setMode] = useState<Mode>('sign-in')
  const [showPassword, setShowPassword] = useState(false)
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [major, setMajor] = useState(majors[0])
  const [remember, setRemember] = useState(true)
  const [acceptedTerms, setAcceptedTerms] = useState(false)
  const [loading, setLoading] = useState(false)
  const [notice, setNotice] = useState('')
  const [error, setError] = useState('')
  const [feedbackOpen, setFeedbackOpen] = useState(false)
  const [feedbackRating, setFeedbackRating] = useState(5)
  const [feedbackText, setFeedbackText] = useState('')
  const [feedbackName, setFeedbackName] = useState('')
  const [reviews, setReviews] = useState<Array<{ quote: string; author: string; rating: number }>>([
    { quote: 'Tested the RAG Tutor with our OS notes—the exact citations are super helpful!', author: 'CSE student · Semester 7', rating: 5 }
  ])

  // Password Recovery Modal State
  const [forgotOpen, setForgotOpen] = useState(false)
  const [forgotStep, setForgotStep] = useState<'email' | 'code' | 'done'>('email')
  const [forgotEmail, setForgotEmail] = useState('')
  const [forgotCode, setForgotCode] = useState('')
  const [forgotNewPass, setForgotNewPass] = useState('')
  const [forgotLoading, setForgotLoading] = useState(false)
  const [forgotError, setForgotError] = useState('')
  const [forgotNotice, setForgotNotice] = useState('')

  // Terms and Privacy Dialog
  const [legalModal, setLegalModal] = useState<'terms' | 'privacy' | null>(null)

  // Load persistent reviews from server
  useEffect(() => {
    fetch('/api/reviews')
      .then(res => res.json())
      .then(data => {
        if (data.reviews && Array.isArray(data.reviews) && data.reviews.length > 0) {
          setReviews(data.reviews)
        }
      })
      .catch(() => {})
  }, [])

  const strength = useMemo(() => {
    const score = [password.length >= 8, /[A-Z]/.test(password), /[0-9]/.test(password), /[^A-Za-z0-9]/.test(password)].filter(Boolean).length
    return { score, label: score < 2 ? 'Weak' : score < 4 ? 'Medium' : 'Strong' }
  }, [password])

  const changeMode = (next: Mode) => {
    setMode(next)
    setError('')
    setNotice('')
  }

  const finishSignIn = () => {
    router.replace('/')
    router.refresh()
  }

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setNotice('')
    if (mode === 'sign-up' && !acceptedTerms) {
      setError('Please agree to the Terms and Privacy Policy to continue.')
      return
    }
    setLoading(true)
    try {
      const result = mode === 'sign-up'
        ? await authClient.signUp.email({ name: name.trim(), email: email.trim(), password, major } as Parameters<typeof authClient.signUp.email>[0])
        : await authClient.signIn.email({ email: email.trim(), password, rememberMe: remember })
      if (result.error) {
        setLoading(false)
        setError(result.error.message ?? 'Authentication failed. Please check your details and try again.')
        return
      }
      finishSignIn()
    } catch {
      setLoading(false)
      setError('Could not connect to authentication services. Please try again.')
    }
  }

  const quickDemo = async () => {
    setError('')
    setNotice('Signing in to quick demo space…')
    setLoading(true)
    try {
      const result = await authClient.signIn.email({ email: demoEmail, password: demoPassword, rememberMe: true })
      if (result.error) {
        const create = await authClient.signUp.email({ name: 'Asha Sharma', email: demoEmail, password: demoPassword, major: 'Computer Science & Engineering' } as Parameters<typeof authClient.signUp.email>[0])
        if (create.error) {
          setLoading(false)
          setError(create.error.message ?? 'Demo account could not be initialized.')
          return
        }
      }
      finishSignIn()
    } catch {
      setLoading(false)
      setError('Demo sign-in failed. Please use standard email sign in.')
    }
  }

  const handleFeedbackSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    const author = feedbackName.trim()
    const quote = feedbackText.trim()
    if (!author || !quote) return

    try {
      const res = await fetch('/api/reviews', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ author, quote, rating: feedbackRating })
      })
      const data = await res.json()
      if (data.reviews) {
        setReviews(data.reviews)
      } else {
        setReviews(current => [{ quote, author, rating: feedbackRating }, ...current])
      }
    } catch {
      setReviews(current => [{ quote, author, rating: feedbackRating }, ...current])
    }

    setFeedbackText('')
    setFeedbackName('')
    setFeedbackRating(5)
    setFeedbackOpen(false)
  }

  const handleRequestCode = async (e: React.FormEvent) => {
    e.preventDefault()
    setForgotError('')
    setForgotNotice('')
    setForgotLoading(true)
    try {
      const res = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'request_code', email: forgotEmail.trim() })
      })
      const data = await res.json()
      setForgotLoading(false)
      if (data.status === 'success') {
        setForgotNotice(data.message)
        if (data.verificationCode) {
          setForgotCode(data.verificationCode)
        }
        setForgotStep('code')
      } else {
        setForgotError(data.message || 'Could not request reset code.')
      }
    } catch {
      setForgotLoading(false)
      setForgotError('Failed to communicate with password recovery service.')
    }
  }

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setForgotError('')
    setForgotNotice('')
    setForgotLoading(true)
    try {
      const res = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'reset_password',
          email: forgotEmail.trim(),
          code: forgotCode.trim(),
          newPassword: forgotNewPass.trim()
        })
      })
      const data = await res.json()
      setForgotLoading(false)
      if (data.status === 'success') {
        setForgotStep('done')
        setEmail(forgotEmail.trim())
        setPassword(forgotNewPass.trim())
        setNotice('Password reset successfully! You can now sign in.')
      } else {
        setForgotError(data.message || 'Password reset failed.')
      }
    } catch {
      setForgotLoading(false)
      setForgotError('Failed to reset password.')
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-story" aria-label="StudySync overview">
        <div className="auth-story-glow auth-story-glow-one" />
        <div className="auth-story-glow auth-story-glow-two" />
        <a className="auth-brand" href="/" aria-label="StudySync home">
          <span className="auth-brand-mark"><GraduationCap size={21} /></span>
          <span><strong>StudySync</strong><small>YOUR LEARNING, IN SYNC</small></span>
        </a>
        <div className="story-content">
          <div className="story-eyebrow"><span /> A BETTER WAY TO LEARN</div>
          <h1>Make room for<br />your <em>next big thing.</em></h1>
          <p className="story-intro">One thoughtful study session at a time, build the knowledge and confidence to go further.</p>
          <div className="project-badge"><GraduationCap size={15} aria-hidden="true" /><span>🎓 Final Year Major Project • Built with 6 Collaborative GenAI Agents</span></div>
          <section className="reviews-card" aria-labelledby="reviews-title">
            <div className="reviews-heading"><span className="reviews-icon"><MessageSquareText size={14} /></span><div><h2 id="reviews-title">Student Feedback &amp; Reviews</h2><span>Notes from the study community</span></div></div>
            <div className="review-list" aria-live="polite">{reviews.slice(0, 3).map((review, index) => <article className="community-review" key={`${review.author}-${index}`}>
              <div className="quote-stars" aria-label={`${review.rating} out of 5 stars`}>{[1, 2, 3, 4, 5].map(star => <Star key={star} size={10} fill={star <= review.rating ? 'currentColor' : 'none'} strokeWidth={star <= review.rating ? 0 : 1.5} />)}</div>
              <blockquote>“{review.quote}”</blockquote><span className="review-author">{review.author}</span>
            </article>)}</div>
            <button className="feedback-trigger" type="button" onClick={() => setFeedbackOpen(true)}>✍️ Leave Feedback / Review</button>
          </section>
        </div>
        {feedbackOpen && <div className="feedback-overlay" onKeyDown={event => { if (event.key === 'Escape') setFeedbackOpen(false) }} onMouseDown={event => { if (event.target === event.currentTarget) setFeedbackOpen(false) }}>
          <section className="feedback-dialog" role="dialog" aria-modal="true" aria-labelledby="feedback-dialog-title">
            <button className="feedback-close" type="button" aria-label="Close feedback form" onClick={() => setFeedbackOpen(false)}><X size={18} /></button>
            <span className="feedback-kicker">STUDY COMMUNITY</span><h2 id="feedback-dialog-title">Share your feedback</h2><p>Your experience can help another student learn.</p>
            <form onSubmit={handleFeedbackSubmit}>
              <fieldset className="rating-field"><legend>Your rating</legend><div className="rating-options">{[1, 2, 3, 4, 5].map(star => <button key={star} type="button" aria-label={`${star} star${star === 1 ? '' : 's'}`} aria-pressed={feedbackRating === star} onClick={() => setFeedbackRating(star)}><Star size={23} fill={star <= feedbackRating ? 'currentColor' : 'none'} /></button>)}</div></fieldset>
              <label className="feedback-field">Your review<textarea required maxLength={500} rows={4} placeholder="Share your experience or suggestion..." value={feedbackText} onChange={event => setFeedbackText(event.target.value)} /></label>
              <label className="feedback-field">Name &amp; Branch<input required maxLength={70} placeholder="e.g. Pritish • CSE Sem 7" value={feedbackName} onChange={event => setFeedbackName(event.target.value)} /></label>
              <button className="feedback-submit" type="submit">Submit Feedback <ArrowRight size={15} /></button>
            </form>
          </section>
        </div>}
        <div className="feature-float feature-rag"><span><Sparkles size={14} /></span><span><strong>AI Tutor RAG</strong><small>Answers grounded in your notes</small></span><i /></div>
        <div className="feature-float feature-sm"><span><BookOpen size={14} /></span><span><strong>SM-2 Spaced Repetition</strong><small>Remember more, for longer</small></span><Check size={15} /> </div>
        <div className="story-footer"><span>© 2026 StudySync</span><span>Made for curious minds</span></div>
      </section>

      <section className="auth-panel" aria-label={mode === 'sign-in' ? 'Sign in' : 'Create account'}>
        <div className="auth-mobile-brand"><span className="auth-brand-mark"><GraduationCap size={20} /></span><strong>StudySync</strong></div>
        <div className="auth-card">
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '14px', paddingBottom: '10px', borderBottom: '1px solid #E2E8F0' }}>
            <button 
              type="button" 
              onClick={quickDemo}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: '#1B4D3E', fontWeight: 600, background: '#ECFDF5', border: '1px solid #A7F3D0', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}
            >
              <ArrowRight size={14} style={{ transform: 'rotate(180deg)' }} /> Back / Explore as Demo
            </button>
          </div>
          <div className="auth-heading">
            <span className="auth-kicker">YOUR SEMESTER, IN SYNC</span>
            <h2>{mode === 'sign-in' ? 'Welcome back' : 'Start your next chapter'}</h2>
            <p>{mode === 'sign-in' ? 'Pick up right where your curiosity left off.' : 'Create your free account and make every study session count.'}</p>
          </div>
          <div className="auth-tabs" role="tablist" aria-label="Account access">
            <button id="tab-sign-in" type="button" role="tab" aria-selected={mode === 'sign-in'} aria-controls="auth-form" className={mode === 'sign-in' ? 'selected' : ''} onClick={() => changeMode('sign-in')}>Sign In</button>
            <button id="tab-sign-up" type="button" role="tab" aria-selected={mode === 'sign-up'} aria-controls="auth-form" className={mode === 'sign-up' ? 'selected' : ''} onClick={() => changeMode('sign-up')}>Create Account</button>
          </div>
          <form id="auth-form" role="tabpanel" aria-labelledby={mode === 'sign-in' ? 'tab-sign-in' : 'tab-sign-up'} onSubmit={onSubmit} className="auth-form">
            {mode === 'sign-up' && <>
              <label className="auth-field"><span>Full name</span><span className="field-wrap"><UserRound size={16} /><input autoComplete="name" name="name" placeholder="e.g. Asha Sharma" value={name} onChange={event => setName(event.target.value)} required /></span></label>
            </>}
            <label className="auth-field"><span>{mode === 'sign-up' ? 'Student email' : 'Email address'}</span><span className="field-wrap"><Mail size={16} /><input autoComplete="email" name="email" type="email" placeholder="you@university.edu" value={email} onChange={event => setEmail(event.target.value)} required /></span></label>
            <label className="auth-field"><span>Password</span><span className="field-wrap"><LockKeyhole size={16} /><input autoComplete={mode === 'sign-up' ? 'new-password' : 'current-password'} name="password" type={showPassword ? 'text' : 'password'} placeholder={mode === 'sign-up' ? 'At least 8 characters' : 'Enter your password'} minLength={8} value={password} onChange={event => setPassword(event.target.value)} required /><button className="password-toggle" type="button" onClick={() => setShowPassword(value => !value)} aria-label={showPassword ? 'Hide password' : 'Show password'}>{showPassword ? <EyeOff size={16} /> : <Eye size={16} />}</button></span></label>
            {mode === 'sign-up' && <>
              <div className="strength-wrap" aria-live="polite"><div className="strength-bars" aria-label={`Password strength: ${strength.label}`}>{[0, 1, 2, 3].map(index => <i key={index} className={index < strength.score ? `filled strength-${strength.label.toLowerCase()}` : ''} />)}</div><span className={`strength-label strength-${strength.label.toLowerCase()}`}>{password ? strength.label : 'Use 8+ characters'}</span></div>
              <label className="auth-field"><span>Degree / major</span><span className="select-wrap"><select value={major} onChange={event => setMajor(event.target.value)} aria-label="Degree or major">{majors.map(item => <option key={item}>{item}</option>)}</select><ChevronDown size={14} aria-hidden="true" className="select-chevron" /></span></label>
              <label className="check-row terms-row"><input type="checkbox" checked={acceptedTerms} onChange={event => setAcceptedTerms(event.target.checked)} /><span>I agree to the <button type="button" onClick={() => setLegalModal('terms')} style={{ background: 'none', border: 'none', color: '#1B4D3E', fontWeight: 700, textDecoration: 'underline', cursor: 'pointer', padding: 0 }}>Terms</button> and <button type="button" onClick={() => setLegalModal('privacy')} style={{ background: 'none', border: 'none', color: '#1B4D3E', fontWeight: 700, textDecoration: 'underline', cursor: 'pointer', padding: 0 }}>Privacy Policy</button>.</span></label>
            </>}
            {mode === 'sign-in' && <div className="form-options"><label className="check-row"><input type="checkbox" checked={remember} onChange={event => setRemember(event.target.checked)} /><span>Remember me</span></label><button type="button" className="text-action" onClick={() => { setForgotOpen(true); setForgotEmail(email); setForgotStep('email'); setForgotError(''); setForgotNotice('') }}>Forgot password?</button></div>}

            {error && <p className="auth-message auth-error" role="alert">{error}</p>}
            {notice && <p className="auth-message" role="status">{notice}</p>}
            <button className="auth-submit" type="submit" disabled={loading}>{loading ? 'Please wait…' : mode === 'sign-in' ? 'Sign In to StudySync' : 'Create your account'}<ArrowRight size={16} /></button>
          </form>
          {mode === 'sign-in' && <button className="demo-button" type="button" onClick={quickDemo} disabled={loading}><span className="demo-bolt"><Zap size={14} /></span><span><strong>Quick Demo as Asha Sharma</strong><small>asha@studysync.edu</small></span><ArrowRight size={15} /></button>}
          <div className="auth-divider"><span /> <small>OR CONTINUE WITH</small> <span /></div>
          <div className="social-row"><button type="button" className="social-button" onClick={() => setNotice('Institutional Google SSO is ready for connected universities. Enter your campus email above.')}><GoogleMark />Google SSO</button><button type="button" className="social-button" onClick={() => setNotice('GitHub Developer Student Pack sign-in is available. Enter your student email above.')}><GitHubMark />GitHub Student</button></div>
          <p className="auth-footnote">By continuing, you agree to StudySync&apos;s <button type="button" onClick={() => setLegalModal('terms')} style={{ background: 'none', border: 'none', color: '#1B4D3E', fontWeight: 600, textDecoration: 'underline', cursor: 'pointer', padding: 0 }}>Terms</button> and <button type="button" onClick={() => setLegalModal('privacy')} style={{ background: 'none', border: 'none', color: '#1B4D3E', fontWeight: 600, textDecoration: 'underline', cursor: 'pointer', padding: 0 }}>Privacy Policy</button>.</p>
        </div>
        <div className="auth-panel-footer"><span>Thoughtful learning, built around you.</span><span style={{ display: 'flex', gap: '12px' }}><button type="button" onClick={() => setLegalModal('terms')} style={{ background: 'none', border: 'none', color: '#64748B', cursor: 'pointer' }}>Terms</button>·<button type="button" onClick={() => setLegalModal('privacy')} style={{ background: 'none', border: 'none', color: '#64748B', cursor: 'pointer' }}>Privacy Policy</button></span></div>
      </section>

      {/* Forgot Password Recovery Modal */}
      {forgotOpen && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(15, 23, 42, 0.65)', backdropFilter: 'blur(4px)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
          <div style={{ background: '#FFFFFF', borderRadius: '16px', width: '100%', maxWidth: '440px', padding: '24px', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)', border: '1px solid #E2E8F0', position: 'relative' }}>
            <button type="button" onClick={() => setForgotOpen(false)} style={{ position: 'absolute', top: '18px', right: '18px', background: 'none', border: 'none', color: '#64748B', cursor: 'pointer' }}><X size={20} /></button>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: '#ECFDF5', color: '#1B4D3E', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <ShieldCheck size={18} />
              </div>
              <h3 style={{ fontSize: '18px', fontWeight: 700, margin: 0, color: '#0F172A' }}>Reset Account Password</h3>
            </div>
            <p style={{ fontSize: '13px', color: '#64748B', margin: '0 0 16px', lineHeight: 1.5 }}>
              {forgotStep === 'email' ? 'Enter your student email address to receive a verification code.' : forgotStep === 'code' ? `Enter the 6-digit verification code and your new password.` : 'Your password has been reset successfully.'}
            </p>

            {forgotError && <div style={{ padding: '10px 12px', background: '#FEF2F2', border: '1px solid #FCA5A5', borderRadius: '8px', color: '#991B1B', fontSize: '12.5px', marginBottom: '14px' }}>{forgotError}</div>}
            {forgotNotice && <div style={{ padding: '10px 12px', background: '#ECFDF5', border: '1px solid #A7F3D0', borderRadius: '8px', color: '#065F46', fontSize: '12.5px', marginBottom: '14px' }}>{forgotNotice}</div>}

            {forgotStep === 'email' && (
              <form onSubmit={handleRequestCode} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '12px', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '4px' }}>Student Email</label>
                  <input type="email" required placeholder="you@university.edu" value={forgotEmail} onChange={e => setForgotEmail(e.target.value)} style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid #CBD5E1', fontSize: '13px', boxSizing: 'border-box' }} />
                </div>
                <button type="submit" disabled={forgotLoading} className="hero-button" style={{ height: '40px', marginTop: '4px' }}>
                  {forgotLoading ? 'Sending Code...' : 'Send Verification Code'}
                </button>
              </form>
            )}

            {forgotStep === 'code' && (
              <form onSubmit={handleResetPassword} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '12px', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '4px' }}>6-Digit Verification Code</label>
                  <input type="text" required placeholder="e.g. 639201" maxLength={6} value={forgotCode} onChange={e => setForgotCode(e.target.value)} style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid #CBD5E1', fontSize: '14px', letterSpacing: '2px', fontFamily: 'monospace', boxSizing: 'border-box' }} />
                </div>
                <div>
                  <label style={{ fontSize: '12px', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '4px' }}>New Password (min 8 chars)</label>
                  <input type="password" required placeholder="Enter new secure password" minLength={8} value={forgotNewPass} onChange={e => setForgotNewPass(e.target.value)} style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid #CBD5E1', fontSize: '13px', boxSizing: 'border-box' }} />
                </div>
                <button type="submit" disabled={forgotLoading} className="hero-button" style={{ height: '40px', marginTop: '4px' }}>
                  {forgotLoading ? 'Resetting...' : 'Save New Password & Sign In'}
                </button>
              </form>
            )}

            {forgotStep === 'done' && (
              <div style={{ textAlign: 'center', padding: '10px 0' }}>
                <p style={{ fontSize: '13.5px', color: '#166534', fontWeight: 600 }}>Your password has been updated!</p>
                <button type="button" onClick={() => setForgotOpen(false)} className="hero-button" style={{ width: '100%', height: '40px', marginTop: '10px' }}>
                  Back to Sign In
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Terms & Privacy Dialog Modal */}
      {legalModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(15, 23, 42, 0.65)', backdropFilter: 'blur(4px)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
          <div style={{ background: '#FFFFFF', borderRadius: '16px', width: '100%', maxWidth: '580px', maxHeight: '80vh', overflowY: 'auto', padding: '26px', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)', border: '1px solid #E2E8F0', position: 'relative' }}>
            <button type="button" onClick={() => setLegalModal(null)} style={{ position: 'absolute', top: '18px', right: '18px', background: 'none', border: 'none', color: '#64748B', cursor: 'pointer' }}><X size={20} /></button>
            <h2 style={{ fontSize: '19px', fontWeight: 700, margin: '0 0 12px', color: '#0F172A' }}>
              {legalModal === 'terms' ? 'StudySync Terms of Service' : 'StudySync Privacy Policy'}
            </h2>
            <div style={{ fontSize: '13px', lineHeight: 1.7, color: '#334155', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {legalModal === 'terms' ? (
                <>
                  <p><strong>1. Academic Integrity &amp; Purpose:</strong> StudySync is designed as a learning accompaniment for university students. Its GenAI agents (TutorGPT, RevisionGPT, CodeMentor) provide concept clarifications and revision tools. Students are expected to uphold university academic integrity guidelines.</p>
                  <p><strong>2. Account &amp; Data Ownership:</strong> Your study schedules, personal flashcards, and uploaded course notes remain your intellectual property. Data is partitioned per account and never shared with other students or unauthorized third parties.</p>
                  <p><strong>3. Service Availability:</strong> While we endeavor to maintain high uptime, AI model generation and execution sandboxes are provided on a best-effort basis subject to model provider rate limits.</p>
                  <p><strong>4. Termination:</strong> You can export your data or delete your account at any time through Settings &gt; Security &amp; Danger Zone.</p>
                </>
              ) : (
                <>
                  <p><strong>1. Information Collection:</strong> We collect only necessary institutional student credentials (name, email, degree/major) and learning artifacts (quiz attempts, SM-2 flashcard intervals) to provide personalized education.</p>
                  <p><strong>2. Data Isolation &amp; Security:</strong> Student study records are isolated per user account. API keys entered into the model settings remain strictly on your local browser in encrypted localStorage and are never stored on centralized database servers.</p>
                  <p><strong>3. Document Confidentiality:</strong> Uploaded syllabus notes and exam question papers are parsed locally in your workspace for personal study sessions and are not used to train public foundation models.</p>
                  <p><strong>4. FERPA &amp; Institutional Compliance:</strong> StudySync complies with educational privacy standards and allows full account deletion with permanent purging of all study logs.</p>
                </>
              )}
            </div>
            <div style={{ marginTop: '20px', paddingTop: '14px', borderTop: '1px solid #E2E8F0', display: 'flex', justifyContent: 'flex-end' }}>
              <button type="button" onClick={() => setLegalModal(null)} className="hero-button" style={{ padding: '8px 20px', fontSize: '13px' }}>
                Close &amp; Return
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  )
}

function GoogleMark() {
  return <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#4285F4" d="M21.6 12.23c0-.71-.06-1.39-.18-2.05H12v3.88h5.38a4.6 4.6 0 0 1-2 3.02v2.52h3.24c1.9-1.75 2.98-4.33 2.98-7.37Z"/><path fill="#34A853" d="M12 22c2.7 0 4.96-.9 6.62-2.4l-3.24-2.52c-.9.6-2.05.96-3.38.96-2.6 0-4.8-1.76-5.58-4.12H3.07v2.6A10 10 0 0 0 12 22Z"/><path fill="#FBBC05" d="M6.42 13.92A6 6 0 0 1 6.1 12c0-.67.12-1.32.32-1.92v-2.6H3.07A10 10 0 0 0 2 12c0 1.62.39 3.15 1.07 4.52l3.35-2.6Z"/><path fill="#EA4335" d="M12 5.96c1.47 0 2.8.51 3.83 1.52l2.88-2.88C16.95 2.98 14.7 2 12 2a10 10 0 0 0-8.93 5.48l3.35 2.6C7.2 7.72 9.4 5.96 12 5.96Z"/></svg>
}

function GitHubMark() {
  return <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 .9a11.1 11.1 0 0 0-3.51 21.64c.55.1.76-.24.76-.54v-2.1c-3.1.68-3.76-1.32-3.76-1.32-.5-1.29-1.24-1.63-1.24-1.63-1.01-.69.08-.68.08-.68 1.12.08 1.7 1.15 1.7 1.15.99 1.7 2.6 1.21 3.23.92.1-.72.39-1.21.7-1.49-2.47-.28-5.07-1.24-5.07-5.5 0-1.22.44-2.21 1.15-2.99-.12-.28-.5-1.42.11-2.95 0 0 .94-.3 3.05 1.14a10.6 10.6 0 0 1 5.55 0c2.11-1.44 3.05-1.14 3.05-1.14.61 1.53.23 2.67.11 2.95.72.78 1.15 1.77 1.15 2.99 0 4.27-2.6 5.21-5.08 5.49.4.35.75 1.02.75 2.06V22c0 .3.2.65.76.54A11.1 11.1 0 0 0 12 .9Z"/></svg>
}
