import { useState } from 'react'
import { useQuery, useMutation } from 'react-query'
import { api } from '../services/api'

interface AgentAction {
  agent_type: string
  action: any
  reasoning_trace: string[]
  confidence: number
}

interface ActionPlan {
  recommended_staffing: { doctors: number; nurses: number }
  recommended_supplies: any
  confidence: number
  messages_for_public: string[]
  suggested_triage_templates: any[]
  evidence: any[]
  agent_actions: AgentAction[]
}

export default function AgentConsole() {
  const [selectedHospital, setSelectedHospital] = useState('')
  const [result, setResult] = useState<ActionPlan | null>(null)

  const { data: hospitals } = useQuery('hospitals', async () => {
    const response = await api.get('/hospitals')
    return response.data
  })

  const askAgentsMutation = useMutation(
    async (data: any) => {
      const response = await api.post('/agents/ask', data)
      return response.data
    },
    {
      onSuccess: (data) => {
        setResult(data.action_plan)
      },
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedHospital) return

    askAgentsMutation.mutate({
      observation: {
        hospital_id: selectedHospital,
        current_metrics: {
          current_patients: 50,
          new_arrivals: 5,
        },
        environmental_context: {
          aqi: 75,
          temperature: 25,
          humidity: 60,
        },
      },
    })
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Agent Console</h1>
        <p className="mt-2 text-sm text-gray-600">
          Multi-agent decision-making system
        </p>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Select Hospital
            </label>
            <select
              value={selectedHospital}
              onChange={(e) => setSelectedHospital(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              <option value="">Select a hospital</option>
              {hospitals?.map((h: any) => (
                <option key={h.id} value={h.id}>
                  {h.name}
                </option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            disabled={!selectedHospital || askAgentsMutation.isLoading}
            className="w-full rounded-md bg-primary-600 py-2 px-4 text-sm font-semibold text-white hover:bg-primary-500 disabled:opacity-50"
          >
            {askAgentsMutation.isLoading ? 'Processing...' : 'Run Agents'}
          </button>
        </form>
      </div>

      {result && (
        <div className="space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Action Plan</h2>
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium text-gray-700">Recommended Staffing</h3>
                <p className="mt-1 text-sm text-gray-600">
                  Doctors: {result.recommended_staffing.doctors}, Nurses:{' '}
                  {result.recommended_staffing.nurses}
                </p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-700">Confidence</h3>
                <p className="mt-1 text-sm text-gray-600">
                  {(result.confidence * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Agent Actions</h2>
            <div className="space-y-4">
              {result.agent_actions.map((action, idx) => (
                <div key={idx} className="border-l-4 border-primary-500 pl-4">
                  <h3 className="text-sm font-medium text-gray-900">
                    {action.agent_type} Agent
                  </h3>
                  <p className="mt-1 text-sm text-gray-600">
                    Confidence: {(action.confidence * 100).toFixed(1)}%
                  </p>
                  <div className="mt-2">
                    <h4 className="text-xs font-medium text-gray-700">Reasoning:</h4>
                    <ul className="mt-1 list-disc list-inside text-xs text-gray-600">
                      {action.reasoning_trace.map((trace, i) => (
                        <li key={i}>{trace}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}


