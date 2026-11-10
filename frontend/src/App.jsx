import { useEffect, useMemo, useState } from 'react'
import './App.css'
import { getPlayers, getTeamStats } from './api'

const PLAYER_STATS = [
  { key: 'games_played', label: 'Games' },
  { key: 'minutes', label: 'Minutes' },
  { key: 'field_goal_percentage', label: 'FG%' },
  { key: 'three_point_percentage', label: '3PT%' },
  { key: 'free_throw_percentage', label: 'FT%' },
  { key: 'offensive_rebounds', label: 'Off. rebounds' },
  { key: 'defensive_rebounds', label: 'Def. rebounds' },
  { key: 'rebounds', label: 'Rebounds' },
  { key: 'assists', label: 'Assists' },
  { key: 'steals', label: 'Steals' },
  { key: 'blocks', label: 'Blocks' },
  { key: 'points', label: 'Points' },
]

const TEAM_STATS = [
  { key: 'points_per_game', label: 'Points per game' },
  { key: 'rebounds_per_game', label: 'Rebounds per game' },
  { key: 'assists_per_game', label: 'Assists per game' },
  { key: 'field_goal_percentage', label: 'Field goal percentage' },
  { key: 'three_point_percentage', label: 'Three-point percentage' },
  { key: 'free_throw_percentage', label: 'Free-throw percentage' },
]

const EMPTY_PLAYERS = []

const LEADERS = [
  { key: 'points', label: 'Scoring leader', unit: 'PTS' },
  { key: 'rebounds', label: 'Rebounding leader', unit: 'REB' },
  { key: 'assists', label: 'Assist leader', unit: 'AST' },
]


const SCHOOLS = [
  { id: 'detroit', name: 'Detroit Mercy', dataAvailable: true },
  { id: 'nku', name: 'Northern Kentucky', dataAvailable: true },
  { id: 'gbp', name: 'Green Bay', dataAvailable: true },
  { id: 'csu', name: 'Cleveland State', dataAvailable: true },
  { id: 'iui', name: 'IU Indianapolis', dataAvailable: true },
  { id: 'mke', name: 'Milwaukee', dataAvailable: true },
  { id: 'niu', name: 'Northern Illinois', dataAvailable: true },
  { id: 'oakland', name: 'Oakland', dataAvailable: true },
  { id: 'rmu', name: 'Robert Morris', dataAvailable: true },
  { id: 'wsu', name: 'Wright State', dataAvailable: true },
  { id: 'pfu', name: 'Purdue Fort Wayne', dataAvailable: true },
  { id: 'ysu', name: 'Youngstown State', dataAvailable: true },
]


function formatStat(value, key) {
  if (value === null || value === undefined || value === '') {
    return '—'
  }

  const numericValue = Number(value)
  if (!Number.isFinite(numericValue)) {
    return '—'
  }

  if (key.endsWith('_percentage')) {
    return `${(numericValue * 100).toFixed(1)}%`
  }

  return Number.isInteger(numericValue)
    ? String(numericValue)
    : numericValue.toFixed(1)
}

function StatSelector({ title, stats, selectedStats, onChange }) {
  const toggleStat = (key) => {
    onChange((current) =>
      current.includes(key)
        ? current.filter((item) => item !== key)
        : [...current, key],
    )
  }

  return (
    <section
      className="stat-visibility-panel"
      style={{
        margin: '1rem 0',
        padding: '1rem',
        border: '1px solid #d8dee8',
        borderRadius: '10px',
        background: '#ffffff',
      }}
    >
      <h3 style={{ marginTop: 0 }}>{title}</h3>
      <div
        className="stat-checkboxes"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: '0.65rem 1rem',
        }}
      >
        {stats.map(({ key, label }) => (
          <label
            key={key}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          >
            <input
              type="checkbox"
              checked={selectedStats.includes(key)}
              onChange={() => toggleStat(key)}
            />
            {label}
          </label>
        ))}
      </div>
      <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
        <button type="button" onClick={() => onChange(stats.map((stat) => stat.key))}>
          Select All
        </button>
        <button type="button" onClick={() => onChange([])}>
          Clear All
        </button>
      </div>
      <p className="data-note" style={{ marginBottom: 0 }}>
        {selectedStats.length} of {stats.length} statistics selected.
      </p>
    </section>
  )
}

function LoadingMessage({ message }) {
  return (
    <div className="empty-state" role="status" aria-live="polite">
      <p>{message}</p>
    </div>
  )
}

function ErrorMessage({ message, onRetry }) {
  return (
    <div className="empty-state" role="alert">
      <h3>Something went wrong</h3>
      <p>{message}</p>
      <button type="button" onClick={onRetry}>Try Again</button>
    </div>
  )
}

function EmptyMessage({ title, message }) {
  return (
    <div className="empty-state" role="status">
      <h3>{title}</h3>
      <p>{message}</p>
    </div>
  )
}

function App() {
  const [selectedPlayer, setSelectedPlayer] = useState(null)
  const [selectedSchoolId, setSelectedSchoolId] = useState('nku')
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [playerData, setPlayerData] = useState({
    schoolId: 'nku',
    players: [],
    error: '',
    loading: true,
  })
  const [teamData, setTeamData] = useState({
    schoolId: 'nku',
    stats: null,
    error: '',
    loading: true,
  })
  const [playerSearch, setPlayerSearch] = useState('')
  const [minimumGames, setMinimumGames] = useState('0')
  const [sortKey, setSortKey] = useState('points')
  const [sortDirection, setSortDirection] = useState('desc')
  const [comparisonNumbers, setComparisonNumbers] = useState(['', ''])
  const [visiblePlayerStats, setVisiblePlayerStats] = useState(
    PLAYER_STATS.map((stat) => stat.key),
  )
  const [visibleTeamStats, setVisibleTeamStats] = useState(
    TEAM_STATS.map((stat) => stat.key),
  )
  const [retryCount, setRetryCount] = useState(0)

  const handleRetry = () => {
    setPlayerData((current) => ({
      ...current,
      schoolId: selectedSchoolId,
      error: '',
      loading: true,
    }))
    setTeamData((current) => ({
      ...current,
      schoolId: selectedSchoolId,
      error: '',
      loading: true,
    }))
    setRetryCount((count) => count + 1)
  }

  const selectedSchool = SCHOOLS.find(
    (school) => school.id === selectedSchoolId,
  )
  const players = playerData.schoolId === selectedSchoolId
    ? playerData.players
    : EMPTY_PLAYERS
  const apiError = playerData.schoolId === selectedSchoolId
    ? playerData.error
    : ''
  const isLoading = selectedSchool.dataAvailable &&
    (playerData.schoolId !== selectedSchoolId || playerData.loading)
  const teamStats = teamData.schoolId === selectedSchoolId
    ? teamData.stats
    : null
  const teamStatsError = teamData.schoolId === selectedSchoolId
    ? teamData.error
    : ''
  const isTeamStatsLoading = selectedSchool.dataAvailable &&
    (teamData.schoolId !== selectedSchoolId || teamData.loading)
  const filteredPlayers = useMemo(() => {
    const query = playerSearch.trim().toLocaleLowerCase()
    return players
      .filter((player) => {
        const matchesSearch =
          !query ||
          String(player.name ?? '').toLocaleLowerCase().includes(query) ||
          String(player.number ?? '').includes(query)
        const matchesGames =
          Number(player.games_played ?? 0) >= Number(minimumGames)
        return matchesSearch && matchesGames
      })
      .sort((a, b) => {
        const aValue = a[sortKey]
        const bValue = b[sortKey]
        const comparison =
          sortKey === 'name'
            ? String(aValue ?? '').localeCompare(String(bValue ?? ''))
            : Number(aValue ?? 0) - Number(bValue ?? 0)
        return sortDirection === 'asc' ? comparison : -comparison
      })
  }, [players, playerSearch, minimumGames, sortKey, sortDirection])

  const comparisonPlayers = comparisonNumbers.map(
    (number) => players.find((player) => String(player.number) === number) ?? null,
  )

  useEffect(() => {
    const controller = new AbortController()

    if (!selectedSchool.dataAvailable) {
      return () => controller.abort()
    }

    getPlayers(selectedSchoolId, { signal: controller.signal })
      .then((data) => {
        if (!Array.isArray(data)) {
          throw new Error('Unexpected data format from the server')
        }

        setPlayerData({
          schoolId: selectedSchoolId,
          players: data,
          error: '',
          loading: false,
        })
      })
      .catch((error) => {
        if (controller.signal.aborted) {
          return
        }
        console.error('API error:', error)
        setPlayerData({
          schoolId: selectedSchoolId,
          players: [],
          error: error.message,
          loading: false,
        })
      })

    getTeamStats(selectedSchoolId, { signal: controller.signal })
      .then((data) => {
        if (!data || typeof data !== 'object' || Array.isArray(data)) {
          throw new Error('Unexpected team statistics format from the server')
        }

        setTeamData({
          schoolId: selectedSchoolId,
          stats: data,
          error: '',
          loading: false,
        })
      })
      .catch((error) => {
        if (controller.signal.aborted) {
          return
        }
        console.error('Team statistics API error:', error)
        setTeamData({
          schoolId: selectedSchoolId,
          stats: null,
          error: error.message,
          loading: false,
        })
      })

    return () => controller.abort()
  }, [selectedSchool.dataAvailable, selectedSchoolId, retryCount])

  const handlePageChange = (page) => {
    setCurrentPage(page)
    setSelectedPlayer(null)
  }

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDirection((direction) => direction === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortDirection(key === 'name' ? 'asc' : 'desc')
    }
  }

  const renderPlayerList = () => {
    if (isLoading) {
      return <p className="sidebar-description">Loading players...</p>
    }

    if (apiError) {
      return (
        <div className="sidebar-description" role="alert">
          <p>Unable to load the player roster.</p>
          <button type="button" onClick={handleRetry}>Try Again</button>
        </div>
      )
    }

    if (players.length === 0) {
      return <p className="sidebar-description">No player data is available for this school yet.</p>
    }

    return players.map((player, index) => (
      <button
        key={player.number ?? player.id ?? index}
        className={`player-button ${
          selectedPlayer === player ? 'selected' : ''
        }`}
        onClick={() => setSelectedPlayer(player)}
      >
        <span className="player-number">{player.number ?? '—'}</span>
        <span className="player-info">
          <strong>{player.name ?? 'Name unavailable'}</strong>
          <small>{player.games_played ?? '—'} games played</small>
        </span>
      </button>
    ))
  }

  const renderPlayerDetails = () => {
    if (isLoading) {
      return <LoadingMessage message={`Loading ${selectedSchool.name} player data...`} />
    }

    if (apiError) {
      return (
        <ErrorMessage
          message="We couldn't retrieve the player roster. Check that the Django backend is running, then try again."
          onRetry={handleRetry}
        />
      )
    }

    if (players.length === 0) {
      return (
        <EmptyMessage
          title="No player data available"
          message={`There are currently no player records to display for ${selectedSchool.name}.`}
        />
      )
    }

    if (!selectedPlayer) {
      return (
        <div className="empty-state">
          <h2>Welcome to the {selectedSchool.name} dashboard</h2>
          <p>
            Select a player from the left to view their performance statistics.
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
            <p>{selectedPlayer.number ?? '—'} · {selectedPlayer.games_played ?? '—'} games</p>
          </div>
        </div>

        <h3>Season Statistics</h3>
        <div className="stats-grid player-stat-grid">
          {PLAYER_STATS.filter(({ key }) => visiblePlayerStats.includes(key)).map(({ key, label }) => (
            <div className="stat-card" key={key}>
              <span>{label}</span>
              <strong>{formatStat(selectedPlayer[key], key)}</strong>
            </div>
          ))}
        </div>
        <p className="data-note">Per-game averages and shooting percentages from the season workbook.</p>
      </>
    )
  }

  const renderPlayersPage = () => {
    if (isLoading) {
      return <LoadingMessage message={`Loading ${selectedSchool.name} players...`} />
    }

    if (apiError) {
      return (
        <ErrorMessage
          message="We couldn't retrieve the player list. Check that the Django backend is running, then try again."
          onRetry={handleRetry}
        />
      )
    }

    if (players.length === 0) {
      return (
        <EmptyMessage
          title="No players found"
          message={`No player records are currently available for ${selectedSchool.name}.`}
        />
      )
    }

    return (
      <>
        <div className="player-controls">
          <label>
            Search players
            <input
              type="search"
              placeholder="Name or jersey number"
              value={playerSearch}
              onChange={(event) => setPlayerSearch(event.target.value)}
            />
          </label>
          <label>
            Minimum games played
            <select
              value={minimumGames}
              onChange={(event) => setMinimumGames(event.target.value)}
            >
              <option value="0">All players</option>
              <option value="10">10+ games</option>
              <option value="20">20+ games</option>
              <option value="30">30+ games</option>
            </select>
          </label>
        </div>

        <StatSelector
          title="Customize Player Statistics"
          stats={PLAYER_STATS}
          selectedStats={visiblePlayerStats}
          onChange={setVisiblePlayerStats}
        />

        <div className="table-scroll">
          <table className="player-stats-table">
            <thead>
              <tr>
                <th scope="col" aria-sort={sortKey === 'number' ? (sortDirection === 'asc' ? 'ascending' : 'descending') : 'none'}>
                  <button className="sort-button" onClick={() => handleSort('number')}>#</button>
                </th>
                <th scope="col" aria-sort={sortKey === 'name' ? (sortDirection === 'asc' ? 'ascending' : 'descending') : 'none'}>
                  <button className="sort-button" onClick={() => handleSort('name')}>Player</button>
                </th>
                {PLAYER_STATS.filter(({ key }) => visiblePlayerStats.includes(key)).map(({ key, label }) => (
                  <th
                    scope="col"
                    key={key}
                    aria-sort={sortKey === key ? (sortDirection === 'asc' ? 'ascending' : 'descending') : 'none'}
                  >
                    <button className="sort-button" onClick={() => handleSort(key)}>{label}</button>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredPlayers.map((player, index) => (
                <tr
                  key={player.number ?? player.id ?? index}
                >
                  <td>{player.number ?? '—'}</td>
                  <th scope="row">
                    <button
                      className="player-name-button"
                      onClick={() => {
                        setSelectedPlayer(player)
                        setCurrentPage('dashboard')
                      }}
                    >
                      {player.name ?? 'Name unavailable'}
                    </button>
                  </th>
                  {PLAYER_STATS.filter(({ key }) => visiblePlayerStats.includes(key)).map(({ key }) => (
                    <td key={key}>{formatStat(player[key], key)}</td>
                  ))}
                </tr>
              ))}
              {filteredPlayers.length === 0 && (
                <tr>
                  <td colSpan={PLAYER_STATS.filter(({ key }) => visiblePlayerStats.includes(key)).length + 2}>No players match your search or minimum-games filter. Try changing or clearing the filters.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <p className="data-note">Showing {filteredPlayers.length} of {players.length} players. Select a row to open that player's details.</p>

        <section className="comparison-section">
          <div className="page-heading">
            <h2>Compare Players</h2>
            <p>Compare season averages using the available roster statistics.</p>
          </div>
          <div className="comparison-selectors">
            {comparisonNumbers.map((number, index) => (
              <label key={index}>
                Player {index + 1}
                <select
                  value={number}
                  onChange={(event) => {
                    setComparisonNumbers((current) =>
                      current.map((value, playerIndex) =>
                        playerIndex === index ? event.target.value : value,
                      ),
                    )
                  }}
                >
                  <option value="">Choose a player</option>
                  {players.map((player) => (
                    <option key={player.number} value={String(player.number)}>
                      #{player.number} {player.name}
                    </option>
                  ))}
                </select>
              </label>
            ))}
          </div>
          {comparisonPlayers.every(Boolean) ? (
            <div className="table-scroll">
              <table className="player-stats-table comparison-table">
                <thead>
                  <tr>
                    <th scope="col">Statistic</th>
                    {comparisonPlayers.map((player) => (
                      <th scope="col" key={player.number}>{player.name}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {PLAYER_STATS.filter(({ key }) => visiblePlayerStats.includes(key)).map(({ key, label }) => (
                    <tr key={key}>
                      <th scope="row">{label}</th>
                      {comparisonPlayers.map((player) => (
                        <td key={player.number}>{formatStat(player[key], key)}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="data-note">Choose two players to see their stats side by side.</p>
          )}
        </section>
      </>
    )
  }

  const renderStatisticsPage = () => {
    if (isTeamStatsLoading) {
      return <LoadingMessage message={`Loading ${selectedSchool.name} team statistics...`} />
    }

    if (teamStatsError) {
      return (
        <ErrorMessage
          message="We couldn't retrieve team statistics. Check that the Django backend is running, then try again."
          onRetry={handleRetry}
        />
      )
    }

    if (!teamStats) {
      return (
        <EmptyMessage
          title="No team statistics available"
          message={`There are currently no team statistics to display for ${selectedSchool.name}.`}
        />
      )
    }

    const leaders = LEADERS.map((leader) => ({
      ...leader,
      player: players.reduce((best, player) =>
        !best || Number(player[leader.key] ?? 0) > Number(best[leader.key] ?? 0)
          ? player
          : best,
      null),
    }))

    return (
      <>
        <StatSelector
          title="Customize Team Statistics"
          stats={TEAM_STATS}
          selectedStats={visibleTeamStats}
          onChange={setVisibleTeamStats}
        />
        <div className="stats-grid">
          {TEAM_STATS.filter(({ key }) => visibleTeamStats.includes(key)).map(({ key, label }) => (
            <div className="stat-card" key={key}>
              <span>{label}</span>
              <strong>{formatStat(teamStats[key], key)}</strong>
            </div>
          ))}
        </div>
        <section className="leaderboard-section">
          <div className="page-heading">
            <h2>Player Leaders</h2>
            <p>Season leaders among players in the workbook.</p>
          </div>
          <div className="leaderboard-grid">
            {leaders.map(({ key, label, player, unit }) => (
              <article className="leader-card" key={key}>
                <span>{label}</span>
                {player ? (
                  <>
                    <h3>{player.name}</h3>
                    <p>#{player.number} · {formatStat(player[key], key)} {unit}</p>
                  </>
                ) : (
                  <p>No player data available.</p>
                )}
              </article>
            ))}
          </div>
        </section>
        <p className="data-note">Team averages and player leaders are based on the season statistics in your workbook.</p>
      </>
    )
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <div>
            <h1>Horizon League Basketball Dashboard</h1>
            <p>Player Statistics &amp; Performance</p>
          </div>
          <div className="header-tools">
            <label className="school-picker">
              School
              <select
                aria-label="Select a school"
                value={selectedSchoolId}
                onChange={(event) => {
                  setSelectedSchoolId(event.target.value)
                  setSelectedPlayer(null)
                }}
              >
                {SCHOOLS.map((school) => (
                  <option key={school.id} value={school.id}>
                    {school.name}{school.dataAvailable ? ' — data available' : ' — data not available'}
                  </option>
                ))}
              </select>
            </label>
            <div className="header-label">{selectedSchool.name}</div>
          </div>
        </div>
      </header>

      <nav className="dashboard-nav">
        <button
          className={`nav-button ${currentPage === 'dashboard' ? 'active' : ''}`}
          onClick={() => handlePageChange('dashboard')}
        >
          Dashboard
        </button>
        <button
          className={`nav-button ${currentPage === 'players' ? 'active' : ''}`}
          onClick={() => handlePageChange('players')}
        >
          Players
        </button>
        <button
          className={`nav-button ${currentPage === 'statistics' ? 'active' : ''}`}
          onClick={() => handlePageChange('statistics')}
        >
          Statistics
        </button>
      </nav>

      <main className="dashboard-content">
        {selectedSchool.dataAvailable !== true ? (
          <section className="full-page">
            <div className="school-unavailable" role="status">
              <h2>{selectedSchool.name} statistics are not available yet</h2>
              <p>
                The scraper configuration includes {selectedSchool.name}, but
                this project currently has statistics data only for Northern
                Kentucky. Select Northern Kentucky to view the available
                roster and season stats.
              </p>
            </div>
          </section>
        ) : currentPage === 'players' ? (
          <section className="full-page">
            <div className="page-heading">
              <h2>{selectedSchool.name} Men's Basketball Players</h2>
              <p>Search, filter, sort, and compare the available player season stats.</p>
            </div>
            {renderPlayersPage()}
          </section>
        ) : currentPage === 'statistics' ? (
          <section className="full-page">
            <div className="page-heading">
              <h2>Team Statistics</h2>
              <p>{selectedSchool.name} men's basketball season averages and player leaders.</p>
            </div>
            {renderStatisticsPage()}
          </section>
        ) : (
          <>
            <aside className="sidebar">
              <h2>Players</h2>
              <p className="sidebar-description">Select a player to view their statistics.</p>
              <div className="player-list">{renderPlayerList()}</div>
            </aside>
            <section className="main-panel">{renderPlayerDetails()}</section>
          </>
        )}
      </main>
    </div>
  )
}

export default App
