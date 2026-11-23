import React, { useState } from 'react'
import './App.css'

export default function App() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    dob: '',
    age: '',
    aadhaar: '',
    parent_pan: '',
    password: ''
  })

  // PLANTED V6: Pre-ticked bundled consent box
  const [agreed, setAgreed] = useState(true)
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'age' ? (value ? parseInt(value, 10) : '') : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setStatus(null)

    try {
      const res = await fetch('http://localhost:8000/api/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })

      const data = await res.json()
      if (res.ok) {
        // PLANTED V13: synthetic, planted for the scanner demo. Personal data kept in browser storage.
        try {
          const { name, dob, aadhaar } = formData
          localStorage.setItem('tutornest_student', JSON.stringify({ name, dob, aadhaar }))
        } catch {
          /* storage may be blocked, signup must still work */
        }
        setStatus({
          type: 'success',
          message: `Account created for ${data.name}! Student ID: ${data.id}`
        })
      } else {
        setStatus({
          type: 'error',
          message: data.detail || 'Signup failed'
        })
      }
    } catch (err) {
      setStatus({
        type: 'error',
        message: 'Could not connect to TutorNest API at http://localhost:8000'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="tutornest-page">
      <header className="tutornest-header">
        <div className="brand">
          <span className="brand-logo">📚</span>
          <h2>TutorNest</h2>
        </div>
        <nav>
          <a href="http://localhost:8000/notice" target="_blank" rel="noreferrer">
            Privacy Notice
          </a>
        </nav>
      </header>

      <main className="tutornest-main">
        <div className="signup-card">
          <div className="card-header">
            <h3>Student Registration</h3>
            <p>Connect with expert tutors for academic excellence</p>
          </div>

          {status && (
            <div className={`status-banner ${status.type}`}>
              {status.message}
            </div>
          )}

          <form onSubmit={handleSubmit} className="signup-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="name">Full Name</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  required
                  placeholder="e.g. Aarav Sharma"
                  value={formData.name}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email Address</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  required
                  placeholder="student@example.test"
                  value={formData.email}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="phone">Phone Number</label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  required
                  placeholder="98XXXXXXXX"
                  value={formData.phone}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label htmlFor="dob">Date of Birth</label>
                <input
                  type="date"
                  id="dob"
                  name="dob"
                  required
                  value={formData.dob}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="age">Age</label>
                <input
                  type="number"
                  id="age"
                  name="age"
                  required
                  min="5"
                  max="100"
                  placeholder="e.g. 16"
                  value={formData.age}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label htmlFor="aadhaar">Aadhaar Number (12 digits)</label>
                <input
                  type="text"
                  id="aadhaar"
                  name="aadhaar"
                  required
                  maxLength={12}
                  placeholder="12 digit Aadhaar"
                  value={formData.aadhaar}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="parent_pan">Parent PAN (for minors under 18)</label>
                <input
                  type="text"
                  id="parent_pan"
                  name="parent_pan"
                  maxLength={10}
                  placeholder="ABCDE1234F"
                  value={formData.parent_pan}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">Account Password</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  required
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* PLANTED V6 */}
            <div className="consent-row">
              <label htmlFor="consent" className="consent-checkbox-label">
                <input
                  type="checkbox"
                  id="consent"
                  checked={agreed}
                  onChange={(e) => setAgreed(e.target.checked)}
                />
                <span>I agree to the Terms and to marketing messages</span>
              </label>
              <div className="notice-subtext">
                By registering, you acknowledge our{' '}
                <a href="http://localhost:8000/notice" target="_blank" rel="noreferrer">
                  Privacy Notice
                </a>
                .
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || !agreed}
              className="submit-btn"
            >
              {loading ? 'Creating Account...' : 'Complete Registration'}
            </button>
          </form>
        </div>
      </main>

      <footer className="tutornest-footer">
        <p>© 2026 TutorNest Learning Technologies Pvt. Ltd. All rights reserved.</p>
      </footer>
    </div>
  )
}
