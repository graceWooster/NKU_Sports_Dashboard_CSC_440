
const API_BASE_URL = 'http://127.0.0.1:8001'

export async function getPlayers(school = 'nku', { signal } = {}) {
  const response = await fetch(
    `${API_BASE_URL}/api/players/?school=${encodeURIComponent(school)}`,
    { signal },
  )

  if (!response.ok) {
    throw new Error('Failed to fetch players')
  }

  return response.json()
}

export async function getTeamStats(school = 'nku', { signal } = {}) {
  const response = await fetch(
    `${API_BASE_URL}/api/team-stats/?school=${encodeURIComponent(school)}`,
    { signal },
  )

  if (!response.ok) {
    throw new Error('Failed to fetch team statistics')
  }

  return response.json()
}
