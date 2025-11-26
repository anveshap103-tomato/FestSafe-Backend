import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface Forecast {
  id: string
  predicted_arrivals: number
  confidence: number
  risk_category: string
  forecast_horizon: number
  forecast_timestamp: string
}

interface ForecastChartProps {
  forecasts: Forecast[]
}

export default function ForecastChart({ forecasts }: ForecastChartProps) {
  const data = forecasts.map((f) => ({
    time: new Date(f.forecast_timestamp).toLocaleTimeString(),
    arrivals: f.predicted_arrivals,
    confidence: f.confidence * 100,
  }))

  if (data.length === 0) {
    return <div className="text-center py-8 text-gray-500">No forecast data available</div>
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="arrivals" stroke="#3b82f6" name="Predicted Arrivals" />
        <Line type="monotone" dataKey="confidence" stroke="#10b981" name="Confidence %" />
      </LineChart>
    </ResponsiveContainer>
  )
}


