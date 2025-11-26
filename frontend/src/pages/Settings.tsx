export default function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-sm text-gray-600">Configure system settings and integrations</p>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Integrations</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">AQI API Key</label>
            <input
              type="text"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="Enter AQI API key"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Weather API Key</label>
            <input
              type="text"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="Enter Weather API key"
            />
          </div>
          <button className="rounded-md bg-primary-600 py-2 px-4 text-sm font-semibold text-white hover:bg-primary-500">
            Save
          </button>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Thresholds</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Low Risk Threshold</label>
            <input
              type="number"
              defaultValue={5}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">High Risk Threshold</label>
            <input
              type="number"
              defaultValue={15}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>
          <button className="rounded-md bg-primary-600 py-2 px-4 text-sm font-semibold text-white hover:bg-primary-500">
            Save
          </button>
        </div>
      </div>
    </div>
  )
}


