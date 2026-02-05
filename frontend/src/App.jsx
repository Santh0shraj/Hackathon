import { Link, Route, Routes } from 'react-router-dom'
import WorkflowBuilder from './pages/WorkflowBuilder'
import WorkflowList from './pages/WorkflowList'
import WorkflowRunView from './pages/WorkflowRunView'

function App() {
  return (
    <div>
      <nav>
        <Link to="/">Workflows</Link> | <Link to="/workflows/new">New Workflow</Link>
      </nav>
      <Routes>
        <Route path="/" element={<WorkflowList />} />
        <Route path="/workflows/new" element={<WorkflowBuilder />} />
        <Route path="/workflows/:id/edit" element={<WorkflowBuilder />} />
        <Route path="/workflow-runs/:id" element={<WorkflowRunView />} />
      </Routes>
    </div>
  )
}

export default App
