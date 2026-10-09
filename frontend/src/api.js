
const API_BASE_URL = 'http://127.0.0.1:8001'

export async function getPlayers() {
  const response = await fetch(`${API_BASE_URL}/api/players/`)

  if (!response.ok) {
    throw new Error('Failed to fetch players')
  }

  return response.json()
}
