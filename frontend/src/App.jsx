
import { useEffect, useState } from 'react'
import './App.css'
import { getPlayers } from './api'

function App() {
  const [selectedPlayer, setSelectedPlayer] = useState(null)
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [apiPlayers, setApiPlayers] = useState([])
  const [apiError, setApiError] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  const players = apiPlayers

  useEffect(() => {
    getPlayers()
      .then((data) => {
        console.log('Players received from Django:', data)

        if (!Array.isArray(data)) {
          throw new Error('Unexpected data format from the server')
        }

        setApiPlayers(data)
        setApiError('')
      })
      .catch((error) => {
        console.error('API error:', error)
        setApiError(error.message)
      })
      .finally(() => {
        setIsLoading(false)
      })
  }, [])

  const handlePageChange = (page) => {
    setCurrentPage(page)
    setSelectedPlayer(null)
  }

  const renderPlayerList = () => {
    if (isLoading) {
      return (
        <p className="sidebar-description">
          Loading players...
        </p>
      )
    }

    if (apiError) {
      return (
        <p className="sidebar-description" role="alert">
          Unable to load players. Please try again later.
        </p>
      )
    }

    if (players.length === 0) {
      return (
        <p className="sidebar-description">
          No player data available yet.
        </p>
      )
    }

    return players.map((player, index) => (
      <button
        key={player.number ?? player.id ?? index}
        className={`player-button ${
          selectedPlayer === player ? 'selected' : ''
        }`}
        onClick={() => setSelectedPlayer(player)}
      >
        <span className="player-number">
          {player.number ?? '—'}
        </span>

        <span className="player-info">
          <strong>{player.name ?? 'Name unavailable'}</strong>
          <small>{player.position ?? 'Position unavailable'}</small>
        </span>
      </button>
    ))
  }

  const renderPlayerDetails = () => {
    if (!selectedPlayer) {
      return (
        <div className="empty-state">
          <h2>Welcome to the NKU Sports Dashboard</h2>
          <p>
            Select a player from the left to view their
            performance statistics.
          </p>
        </div>
      )
    }

    return (
      <>
        <div className="player-header">
          <div className="player-avatar">
            {String(selectedPlayer.number ?? '').replace('#', '')}
          </div>

          <div>
            <h2>{selectedPlayer.name ?? 'Player details'}</h2>
            <p>
              {selectedPlayer.number ?? '—'} ·{' '}
              {selectedPlayer.position ?? 'Position unavailable'}
            </p>
          </div>
        </div>

        <h3>Season Statistics</h3>

        <div className="stats-grid">
          <div className="stat-card">
            <span>Points Per Game</span>
            <strong>{selectedPlayer.points ?? '—'}</strong>
          </div>

          <div className="stat-card">
            <span>Rebounds Per Game</span>
            <strong>{selectedPlayer.rebounds ?? '—'}</strong>
          </div>

          <div className="stat-card">
            <span>Assists Per Game</span>
            <strong>{selectedPlayer.assists ?? '—'}</strong>
          </div>
        </div>

        <div className="performance-card">
          <h3>Performance Overview</h3>
          <p>
            Additional player statistics and visualizations
            will appear here as verified data becomes available.
          </p>
        </div>
      </>
    )
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <div>
            <h1>NKU Sports Dashboard</h1>
            <p>Player Statistics &amp; Performance</p>
          </div>

          <div className="header-label">
            NKU Athletics
          </div>
        </div>
      </header>

      <nav className="dashboard-nav">
        <button
          className={`nav-button ${
            currentPage === 'dashboard' ? 'active' : ''
          }`}
          onClick={() => handlePageChange('dashboard')}
        >
          Dashboard
        </button>

        <button
          className={`nav-button ${
            currentPage === 'players' ? 'active' : ''
          }`}
          onClick={() => handlePageChange('players')}
        >
          Players
        </button>

        <button
          className={`nav-button ${
            currentPage === 'statistics' ? 'active' : ''
          }`}
          onClick={() => handlePageChange('statistics')}
        >
          Statistics
        </button>
      </nav>

      <main className="dashboard-content">
        {currentPage === 'players' ? (
          <section className="full-page">
            <div className="page-heading">
              <h2>NKU Men's Basketball Players</h2>
              <p>Roster and player information</p>
            </div>

            {isLoading ? (
              <p>Loading players...</p>
            ) : apiError ? (
              <p role="alert">
                Unable to load players. Please try again later.
              </p>
            ) : players.length === 0 ? (
              <p>No player data available yet.</p>
            ) : (
              <div className="roster-grid">
                {players.map((player, index) => (
                  <button
                    key={player.number ?? player.id ?? index}
                    className="roster-card"
                    onClick={() => {
                      setSelectedPlayer(player)
                      setCurrentPage('dashboard')
                    }}
                  >
                    <div className="roster-number">
                      {player.number ?? '—'}
                    </div>

                    <div className="roster-info">
                      <h3>{player.name ?? 'Name unavailable'}</h3>
                      <p>
                        {player.position ?? 'Position unavailable'}
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </section>
        ) : currentPage === 'statistics' ? (
          <section className="full-page">
            <div className="page-heading">
              <h2>Team Statistics</h2>
              <p>NKU Men's Basketball statistics</p>
            </div>

            <div className="stats-grid">
              <div className="stat-card">
                <span>Points Per Game</span>
                <strong>—</strong>
              </div>

              <div className="stat-card">
                <span>Rebounds Per Game</span>
                <strong>—</strong>
              </div>

              <div className="stat-card">
                <span>Assists Per Game</span>
                <strong>—</strong>
              </div>
            </div>

            <div className="performance-card">
              <h3>Team Performance</h3>
              <p>
                Team statistics will appear here when verified
                NKU data is available from the backend.
              </p>
            </div>
          </section>
        ) : (
          <>
            <aside className="sidebar">
              <h2>Players</h2>

              <p className="sidebar-description">
                Select a player to view their statistics.
              </p>

              <div className="player-list">
                {renderPlayerList()}
              </div>
            </aside>

            <section className="main-panel">
              {renderPlayerDetails()}
            </section>
          </>
        )}
      </main>
    </div>
  )
}

export default App