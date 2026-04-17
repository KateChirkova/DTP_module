"use client"

import { useEffect, useState } from 'react'

interface AccidentData {
  count: number
}

export default function Home() {
  const [count, setCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        setError(null)
        const response = await fetch('http://localhost:8080/api/v1/accidents', {
          cache: 'no-store'  // Отключаем кэш
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }

        const data: AccidentData = await response.json()
        setCount(data.count || 0)
      } catch (err) {
        console.error('Backend error:', err)
        setError('Backend недоступен (порт 8080)')
      } finally {
        setLoading(false)
      }
    }

    loadData()
    const intervalId = setInterval(loadData, 2000)
    return () => clearInterval(intervalId)
  }, [])

  return (
    <div style={{
      minHeight: '100vh',
      padding: '4rem 2rem',
      background: 'linear-gradient(135deg, #fee2e2 0%, #fed7aa 100%)',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <h1 style={{
        fontSize: '4rem',
        fontWeight: '900',
        textAlign: 'center',
        marginBottom: '3rem',
        backgroundImage: 'linear-gradient(135deg, #dc2626, #f97316)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        textShadow: '0 0 30px rgba(220, 38, 38, 0.3)'
      }}>
        🚗 DTP Akaito Live
      </h1>

      <div style={{
        maxWidth: '500px',
        margin: '0 auto',
        padding: '3rem 2rem',
        background: 'rgba(255, 255, 255, 0.95)',
        borderRadius: '2rem',
        boxShadow: '0 25px 50px rgba(0,0,0,0.15)',
        textAlign: 'center'
      }}>
        {loading ? (
          <div style={{ fontSize: '1.5rem', color: '#6b7280' }}>
            Загрузка...
          </div>
        ) : error ? (
          <div style={{
            fontSize: '1.2rem',
            color: '#dc2626',
            background: '#fee2e2',
            padding: '1rem',
            borderRadius: '1rem'
          }}>
            {error}
          </div>
        ) : (
          <>
            <div style={{
              fontSize: '6rem',
              fontWeight: '900',
              color: '#dc2626',
              marginBottom: '1rem',
              textShadow: '0 10px 20px rgba(220, 38, 38, 0.2)'
            }}>
              {count}
            </div>
            <div style={{
              fontSize: '1.5rem',
              color: '#6b7280',
              marginBottom: '2rem'
            }}>
              Активных ДТП в Москве
            </div>
          </>
        )}
      </div>
    </div>
  )
}