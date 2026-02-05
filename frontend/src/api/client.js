import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: { 'Content-Type': 'application/json' },
})

export async function listWorkflows() {
  const { data } = await client.get('/workflows')
  return data.workflows
}

export async function createWorkflow({ name, description }) {
  const { data } = await client.post('/workflows', { name, description })
  return data
}

export async function addStep(workflowId, step) {
  const { data } = await client.post(`/workflows/${workflowId}/steps`, step)
  return data
}

export async function runWorkflow(workflowId) {
  const { data } = await client.post(`/workflows/${workflowId}/run`)
  return data
}

export async function getWorkflowRun(runId) {
  const { data } = await client.get(`/workflow-runs/${runId}`)
  return data
}
