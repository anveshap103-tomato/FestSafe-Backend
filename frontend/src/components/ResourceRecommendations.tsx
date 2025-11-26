import { useQuery } from 'react-query'
import { api } from '../services/api'

interface Recommendation {
  id: string
  recommended_staffing: { doctors: number; nurses: number }
  recommended_supplies: any
  confidence: number
  status: string
}

interface ResourceRecommendationsProps {
  hospitalId: string
}

export default function ResourceRecommendations({ hospitalId }: ResourceRecommendationsProps) {
  const { data: recommendations, isLoading } = useQuery<Recommendation[]>(
    ['recommendations', hospitalId],
    async () => {
      const response = await api.get(`/recommendations?hospital_id=${hospitalId}`)
      return response.data
    },
    { enabled: !!hospitalId }
  )

  if (isLoading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="text-center py-4">Loading recommendations...</div>
      </div>
    )
  }

  const latest = recommendations?.[0]

  if (!latest) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Recommendations</h2>
        <p className="text-sm text-gray-500">No recommendations available</p>
      </div>
    )
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-lg font-medium text-gray-900 mb-4">Recommendations</h2>
      <div className="space-y-4">
        <div>
          <h3 className="text-sm font-medium text-gray-700">Staffing</h3>
          <dl className="mt-2 space-y-1">
            <div className="flex justify-between">
              <dt className="text-sm text-gray-600">Doctors</dt>
              <dd className="text-sm font-medium">{latest.recommended_staffing.doctors}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm text-gray-600">Nurses</dt>
              <dd className="text-sm font-medium">{latest.recommended_staffing.nurses}</dd>
            </div>
          </dl>
        </div>

        <div>
          <h3 className="text-sm font-medium text-gray-700">Supplies</h3>
          <dl className="mt-2 space-y-1">
            {Object.entries(latest.recommended_supplies).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <dt className="text-sm text-gray-600 capitalize">{key.replace('_', ' ')}</dt>
                <dd className="text-sm font-medium">{String(value)}</dd>
              </div>
            ))}
          </dl>
        </div>

        <div>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-gray-700">Confidence</span>
            <span className="text-sm font-medium text-gray-900">
              {(latest.confidence * 100).toFixed(1)}%
            </span>
          </div>
        </div>

        <div>
          <span
            className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
              latest.status === 'approved'
                ? 'bg-green-100 text-green-800'
                : latest.status === 'rejected'
                ? 'bg-red-100 text-red-800'
                : 'bg-yellow-100 text-yellow-800'
            }`}
          >
            {latest.status}
          </span>
        </div>
      </div>
    </div>
  )
}


