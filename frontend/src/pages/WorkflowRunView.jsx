import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getWorkflowRun } from '../api/client'

export default function WorkflowRunView() {
  const { id } = useParams()
  const [run, setRun] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) return
    load()
  }, [id])

  async function load() {
    setLoading(true)
    setError('')
    try {
      const data = await getWorkflowRun(id)
      setRun(data)
    } catch (e) {
      setError(e.response?.data?.error || e.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading && !run) return <p>Loading...</p>
  if (error) return <p style={{ color: 'red' }}>{error}</p>
  if (!run) return <p>Run not found.</p>

  return (
    <div>
      <h1>Workflow Run {run.id}</h1>
      <p><Link to="/">Back to Workflows</Link></p>
      <p><strong>Status:</strong> {run.status}</p>
      <p><strong>Started:</strong> {run.started_at}</p>
      {run.finished_at && <p><strong>Finished:</strong> {run.finished_at}</p>}
      <h2>Step runs (logs)</h2>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {run.step_runs?.map((sr) => (
          <li key={sr.id} style={{ border: '1px solid #ccc', marginBottom: 8, padding: 8 }}>
            <div>Step {sr.step_id} — Attempt {sr.attempt_number} — <strong>{sr.status}</strong></div>
            {sr.failure_reason && <div style={{ color: 'red' }}>{sr.failure_reason}</div>}
            {sr.llm_response != null && sr.llm_response !== '' && (
              <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12, maxHeight: 200, overflow: 'auto' }}>
                {sr.llm_response}
              </pre>
            )}
            <div style={{ fontSize: 12, color: '#666' }}>{sr.created_at}</div>
          </li>
        ))}
      </ul>
      <button type="button" onClick={load}>Refresh</button>
    </div>
  )
}
