import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { addStep, createWorkflow, listWorkflows, runWorkflow } from '../api/client'

const COMPLETION_TYPES = ['', 'contains', 'regex', 'json', 'python_function']
const CONTEXT_STRATEGIES = ['full', 'code_only', 'summary']

export default function WorkflowBuilder() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [workflow, setWorkflow] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Create workflow (when on /workflows/new)
  const [createName, setCreateName] = useState('')
  const [createDescription, setCreateDescription] = useState('')
  const [creating, setCreating] = useState(false)

  // Add step form
  const [showStepForm, setShowStepForm] = useState(false)
  const [stepOrder, setStepOrder] = useState(1)
  const [modelName, setModelName] = useState('')
  const [promptTemplate, setPromptTemplate] = useState('')
  const [completionType, setCompletionType] = useState('')
  const [completionValue, setCompletionValue] = useState('')
  const [retryLimit, setRetryLimit] = useState(0)
  const [contextStrategy, setContextStrategy] = useState('full')

  const [steps, setSteps] = useState([])
  const [running, setRunning] = useState(false)

  const workflowId = id ? parseInt(id, 10) : (workflow ? workflow.id : null)
  const isNew = !id && !workflow

  useEffect(() => {
    if (id) load()
    else if (!workflow) setLoading(false)
  }, [id])

  async function load() {
    if (!workflowId) return
    setLoading(true)
    setError('')
    try {
      const list = await listWorkflows()
      const w = list.find((x) => x.id === workflowId)
      setWorkflow(w || null)
      setStepOrder(1)
      setSteps([])
    } catch (e) {
      setError(e.response?.data?.error || e.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleCreateWorkflow(e) {
    e.preventDefault()
    if (!createName.trim()) return
    setCreating(true)
    setError('')
    try {
      const w = await createWorkflow({
        name: createName.trim(),
        description: createDescription.trim() || undefined,
      })
      setWorkflow(w)
      setCreateName('')
      setCreateDescription('')
      setStepOrder(1)
      setSteps([])
      navigate(`/workflows/${w.id}/edit`, { replace: true })
    } catch (e) {
      setError(e.response?.data?.error || e.message)
    } finally {
      setCreating(false)
    }
  }

  async function handleAddStep(e) {
    e.preventDefault()
    const wid = workflow?.id || workflowId
    if (!wid || !modelName.trim() || !promptTemplate.trim()) return
    setError('')
    try {
      const step = await addStep(wid, {
        step_order: stepOrder,
        model_name: modelName.trim(),
        prompt_template: promptTemplate.trim(),
        completion_type: completionType || undefined,
        completion_value: completionValue || undefined,
        retry_limit: parseInt(retryLimit, 10) || 0,
        context_strategy: contextStrategy,
      })
      setSteps((prev) => [...prev, step])
      setStepOrder((prev) => prev + 1)
      setModelName('')
      setPromptTemplate('')
      setCompletionType('')
      setCompletionValue('')
      setRetryLimit(0)
      setContextStrategy('full')
      setShowStepForm(false)
    } catch (e) {
      setError(e.response?.data?.error || e.message)
    }
  }

  async function handleRun() {
    const wid = workflow?.id || workflowId
    if (!wid) return
    setRunning(true)
    setError('')
    try {
      const run = await runWorkflow(wid)
      navigate(`/workflow-runs/${run.id}`)
    } catch (e) {
      setError(e.response?.data?.error || e.message)
    } finally {
      setRunning(false)
    }
  }

  if (loading) return <p>Loading...</p>
  if (id && !workflow) return <p>Workflow not found.</p>

  // New workflow: show create form first
  if (isNew) {
    return (
      <div>
        <h1>New Workflow</h1>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <form onSubmit={handleCreateWorkflow}>
          <div>
            <label>Name</label>
            <input
              value={createName}
              onChange={(e) => setCreateName(e.target.value)}
              required
              placeholder="Workflow name"
            />
          </div>
          <div>
            <label>Description</label>
            <input
              value={createDescription}
              onChange={(e) => setCreateDescription(e.target.value)}
              placeholder="Optional description"
            />
          </div>
          <button type="submit" disabled={creating}>
            {creating ? 'Creating...' : 'Create Workflow'}
          </button>
        </form>
      </div>
    )
  }

  // Existing workflow: show name, add steps, run
  return (
    <div>
      <h1>{workflow?.name ?? 'Workflow'}</h1>
      {workflow?.description && <p>{workflow.description}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <button type="button" onClick={() => setShowStepForm(!showStepForm)}>
        {showStepForm ? 'Cancel' : 'Add Step'}
      </button>
      <button type="button" onClick={handleRun} disabled={running}>
        {running ? 'Running...' : 'Run Workflow'}
      </button>

      {showStepForm && (
        <form onSubmit={handleAddStep} style={{ marginTop: 16, maxWidth: 560 }}>
          <h2>Add step</h2>
          <div>
            <label>Model</label>
            <input
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
              required
              placeholder="e.g. gpt-4"
            />
          </div>
          <div>
            <label>Prompt (use {'{previous_output}'} for prior step)</label>
            <textarea
              value={promptTemplate}
              onChange={(e) => setPromptTemplate(e.target.value)}
              required
              rows={4}
              placeholder="Prompt template..."
            />
          </div>
          <div>
            <label>Completion type</label>
            <select
              value={completionType}
              onChange={(e) => setCompletionType(e.target.value)}
            >
              {COMPLETION_TYPES.map((t) => (
                <option key={t || 'none'} value={t}>
                  {t || 'none'}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label>Completion value</label>
            <input
              value={completionValue}
              onChange={(e) => setCompletionValue(e.target.value)}
              placeholder="String or regex; ignored for json/python_function"
            />
          </div>
          <div>
            <label>Retry limit</label>
            <input
              type="number"
              min={0}
              value={retryLimit}
              onChange={(e) => setRetryLimit(parseInt(e.target.value, 10) || 0)}
            />
          </div>
          <div>
            <label>Context strategy</label>
            <select
              value={contextStrategy}
              onChange={(e) => setContextStrategy(e.target.value)}
            >
              {CONTEXT_STRATEGIES.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          <button type="submit">Add Step</button>
        </form>
      )}

      <h2>Steps</h2>
      {steps.length === 0 ? (
        <p>No steps yet. Add steps above and they will be saved to the backend.</p>
      ) : (
        <ul>
          {steps.map((s) => (
            <li key={s.id}>
              Step {s.step_order}: {s.model_name} — completion: {s.completion_type || 'none'}
              {s.retry_limit > 0 && `, retries: ${s.retry_limit}`}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
