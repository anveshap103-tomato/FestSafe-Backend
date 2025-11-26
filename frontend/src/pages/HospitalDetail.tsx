import { useParams, Link } from 'react-router-dom'
import { useQuery } from 'react-query'
import { api } from '../services/api'
import ForecastChart from '../components/ForecastChart'
import ResourceRecommendations from '../components/ResourceRecommendations'

interface Hospital {
  id: string
  name: string
  bed_count: number
  icu_count: number
  doctors_count: number
  nurses_count: number
}

interface Forecast {
  id: string
  predicted_arrivals: number
  confidence: number
  risk_category: string
  forecast_horizon: number
}

export default function HospitalDetail() {
  const { id } = useParams<{ id: string }>()

  const { data: hospital, isLoading: hospitalLoading } = useQuery<Hospital>(
    ['hospital', id],
    async () => {
      const response = await api.get(`/hospitals/${id}`)
      return response.data
    },
    { enabled: !!id }
  )

  const { data: forecasts, isLoading: forecastsLoading } = useQuery<Forecast[]>(
    ['forecasts', id],
    async () => {
      const response = await api.get(`/forecasts/hospital/${id}?window=24h`)
      return response.data
    },
    { enabled: !!id }
  )

  if (hospitalLoading) {
    return <div className="text-center py-12">Loading hospital details...</div>
  }

  if (!hospital) {
    return <div className="text-center py-12">Hospital not found</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{hospital.name}</h1>
          <p className="mt-2 text-sm text-gray-600">Hospital details and forecasts</p>
        </div>
        <Link
          to="/"
          className="text-sm text-primary-600 hover:text-primary-900"
        >
          ← Back to Dashboard
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Current Metrics</h2>
            <dl className="grid grid-cols-2 gap-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">Total Beds</dt>
                <dd className="mt-1 text-2xl font-semibold text-gray-900">
                  {hospital.bed_count}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">ICU Beds</dt>
                <dd className="mt-1 text-2xl font-semibold text-gray-900">
                  {hospital.icu_count}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Doctors</dt>
                <dd className="mt-1 text-2xl font-semibold text-gray-900">
                  {hospital.doctors_count || 'N/A'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Nurses</dt>
                <dd className="mt-1 text-2xl font-semibold text-gray-900">
                  {hospital.nurses_count || 'N/A'}
                </dd>
              </div>
            </dl>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Forecast</h2>
            {forecastsLoading ? (
              <div className="text-center py-8">Loading forecasts...</div>
            ) : (
              <ForecastChart forecasts={forecasts || []} />
            )}
          </div>
        </div>

        <div>
          <ResourceRecommendations hospitalId={id!} />
        </div>
      </div>
    </div>
  )
}


