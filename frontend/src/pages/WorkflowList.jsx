import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { createWorkflow, listWorkflows, runWorkflow } from '../api/client'

export default function WorkflowList() {
  const [workflows, setWorkflows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [runningId, setRunningId] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    load()
  }, [])

  async function load() {
    setLoading(true)
    setError('')
    try {
      const list = await listWorkflows()
      setWorkflows(list)
    } catch (e) {
      setError(e.response?.data?.error || e.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleCreate(e) {
    e.preventDefault()
    if (!name.trim()) return
    setError('')
    try {
      const w = await createWorkflow({ name: name.trim(), description: description.trim() || undefined })
      setWorkflows((prev) => [...prev, w])
      setName('')
      setDescription('')
      setShowForm(false)
      navigate(`/workflows/${w.id}/edit`)
    } catch (e) {
      setError(e.response?.data?.error || e.message)
    }
  }

  async function handleRun(workflowId) {
    setRunningId(workflowId)
    setError('')
    try {
      const run = await runWorkflow(workflowId)
      navigate(`/workflow-runs/${run.id}`)
    } catch (e) {
      setError(e.response?.data?.error || e.message)
    } finally {
      setRunningId(null)
    }
  }

  if (loading) return <p>Loading...</p>
  if (error) return <p style={{ color: 'red' }}>{error}</p>

  return (
    <div>
      <h1>Workflows</h1>
      {!showForm ? (
        <button type="button" onClick={() => setShowForm(true)}>New Workflow</button>
      ) : (
        <form onSubmit={handleCreate}>
          <div>
            <label>Name</label>
            <input value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          <div>
            <label>Description</label>
            <input value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>
          <button type="submit">Create</button>
          <button type="button" onClick={() => { setShowForm(false); setName(''); setDescription('') }}>Cancel</button>
        </form>
      )}
      <ul>
        {workflows.map((w) => (
          <li key={w.id}>
            <Link to={`/workflows/${w.id}/edit`}>{w.name}</Link>
            {w.description && <span> — {w.description}</span>}
            <button type="button" onClick={() => handleRun(w.id)} disabled={runningId !== null}>
              {runningId === w.id ? 'Running...' : 'Run'}
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
