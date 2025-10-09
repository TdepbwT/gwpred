import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { TrendingUp, Trophy, Target, BarChart3 } from 'lucide-react'
import axios from 'axios'

interface MatchPrediction {
  match: string
  home_team: string
  away_team: string
  home_percentage: number
  draw_percentage: number
  away_percentage: number
  fair_home_odds: number
  fair_draw_odds: number
  fair_away_odds: number
  exp_goals_home: number
  exp_goals_away: number
  most_likely_score: string
  rating_diff: number  // Changed from model_diff
}

interface GameweekPredictions {
  gameweek: number
  season: string
  predictions: MatchPrediction[]
  last_updated: string
  total_matches: number
}

interface TeamRating {
  team: string
  rating: number
  effective_rating: number
  form_boost: number
  change_from_previous?: number
  reason?: string
}

interface TeamRatingsResponse {
  season: string
  gameweek: number
  ratings: TeamRating[]
  last_updated: string
}

interface MatchResult {
  gameweek: number
  opponent: string
  is_home: boolean
  team_goals: number
  opponent_goals: number
  result: 'W' | 'L' | 'D'
  score: string
}

interface RatingChange {
  gameweek: number
  previous_rating: number
  new_rating: number
  change: number
}

interface TeamDetails {
  team: string
  current_rating: number
  effective_rating: number
  form_boost: number
  form_results: number[]
  form_description: string
  match_history: MatchResult[]
  rating_history: number[]
  rating_changes: RatingChange[]
  season: string
  current_gameweek: number
}

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'https://gwpred-backend.onrender.com'

function App() {
  const [predictions, setPredictions] = useState<GameweekPredictions | null>(null)
  const [ratings, setRatings] = useState<TeamRatingsResponse | null>(null)
  const [teamDetails, setTeamDetails] = useState<TeamDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'predictions' | 'ratings' | 'team'>('predictions')
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      console.log('API_BASE_URL:', API_BASE_URL) // Debug log
      
      // First get available gameweeks
      const availableRes = await axios.get(`${API_BASE_URL}/predictions`)
      const currentGameweek = availableRes.data.current_gameweek
      
      const [predictionsRes, ratingsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/predictions/${currentGameweek}`),
        axios.get(`${API_BASE_URL}/ratings`)
      ])
      
      console.log('Predictions response:', predictionsRes.data) // Debug log
      console.log('Ratings response:', ratingsRes.data) // Debug log
      
      // Additional debugging
      if (predictionsRes.data) {
        console.log('Predictions structure:', {
          hasGameweek: 'gameweek' in predictionsRes.data,
          hasPredictions: 'predictions' in predictionsRes.data,
          predictionsArray: Array.isArray(predictionsRes.data.predictions),
          predictionsLength: predictionsRes.data.predictions?.length || 0
        })
      }
      
      setPredictions(predictionsRes.data)
      setRatings(ratingsRes.data)
    } catch (err) {
      console.error('Full error object:', err) // Enhanced error logging
      if (axios.isAxiosError(err)) {
        console.error('Axios error details:', {
          message: err.message,
          status: err.response?.status,
          statusText: err.response?.statusText,
          data: err.response?.data,
          url: err.config?.url
        })
        setError(`API Error: ${err.response?.status || 'Network'} - ${err.message}`)
      } else {
        setError('Failed to fetch data. Please check your internet connection.')
      }
    } finally {
      setLoading(false)
    }
  }

  const fetchTeamDetails = async (teamName: string) => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await axios.get(`${API_BASE_URL}/team/${encodeURIComponent(teamName)}`)
      setTeamDetails(response.data)
      setSelectedTeam(teamName)
      setActiveTab('team')
    } catch (err) {
      console.error('Error fetching team details:', err)
      if (axios.isAxiosError(err)) {
        setError(`Failed to fetch team details: ${err.response?.status || 'Network'} - ${err.message}`)
      } else {
        setError('Failed to fetch team details. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const getOutcomeColor = (percentage: number, isHighest: boolean) => {
    if (isHighest && percentage > 60) return 'text-green-600 font-bold'
    if (isHighest && percentage > 40) return 'text-blue-600 font-semibold'
    return 'text-gray-600'
  }

  const getTeamColor = (rating: number) => {
    if (rating > 1.0) return 'text-green-600 font-bold'
    if (rating > 0.5) return 'text-blue-600 font-semibold'
    if (rating > 0) return 'text-gray-700'
    if (rating > -0.3) return 'text-orange-600'
    return 'text-red-600'
  }

  const getResultColor = (result: 'W' | 'L' | 'D') => {
    switch (result) {
      case 'W': return 'text-green-600 font-bold'
      case 'L': return 'text-red-600 font-bold'
      case 'D': return 'text-gray-600 font-semibold'
      default: return 'text-gray-600'
    }
  }

  const getFormResultIcon = (result: number) => {
    if (result === 1) return '🟢' // Win
    if (result === 0.5) return '🟡' // Draw
    return '🔴' // Loss
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading Premier League predictions...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-red-600">Error</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={fetchData} className="w-full">
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Trophy className="h-8 w-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">
                Premier League Predictions
              </h1>
            </div>
            <div className="text-sm text-gray-500">
              Season {predictions?.season} • GW{predictions?.gameweek}
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('predictions')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'predictions'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Target className="h-4 w-4" />
                <span>Match Predictions</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('ratings')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'ratings'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center space-x-2">
                <BarChart3 className="h-4 w-4" />
                <span>Team Ratings</span>
              </div>
            </button>
            {selectedTeam && (
              <button
                onClick={() => setActiveTab('team')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'team'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Trophy className="h-4 w-4" />
                  <span>{selectedTeam}</span>
                </div>
              </button>
            )}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'predictions' && predictions && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold text-gray-900">Gameweek {predictions.gameweek} Predictions</h2>
              <p className="text-gray-600">
                {predictions.total_matches} matches • Last updated: {new Date(predictions.last_updated).toLocaleString()}
              </p>
            </div>

            <div className="grid gap-6">
              {predictions.predictions && predictions.predictions.length > 0 ? predictions.predictions.map((match, index) => {
                const outcomes = [
                  { type: 'Home', percentage: match.home_percentage, odds: match.fair_home_odds },
                  { type: 'Draw', percentage: match.draw_percentage, odds: match.fair_draw_odds },
                  { type: 'Away', percentage: match.away_percentage, odds: match.fair_away_odds }
                ]
                const highestOutcome = outcomes.reduce((max, outcome) => 
                  outcome.percentage > max.percentage ? outcome : max
                )

                return (
                  <Card key={index} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <CardTitle className="text-xl">
                        {match.home_team} vs {match.away_team}
                      </CardTitle>
                      <CardDescription>
                        Most likely score: <span className="font-semibold">{match.most_likely_score}</span>
                        {' • '}
                        Expected goals: {match.exp_goals_home} - {match.exp_goals_away}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-3 gap-4 mb-4">
                        {outcomes.map((outcome) => (
                          <div key={outcome.type} className="text-center">
                            <div className={`text-2xl font-bold ${getOutcomeColor(
                              outcome.percentage, 
                              outcome.type === highestOutcome.type
                            )}`}>
                              {outcome.percentage}%
                            </div>
                            <div className="text-sm text-gray-500">
                              {outcome.type}
                            </div>
                            <div className="text-xs text-gray-400">
                              Odds: {outcome.odds}
                            </div>
                          </div>
                        ))}
                      </div>
                      
                      <div className="flex justify-between items-center text-sm text-gray-500">
                        <span>Rating difference: {match.rating_diff > 0 ? '+' : ''}{match.rating_diff}</span>
                        <TrendingUp className="h-4 w-4" />
                      </div>
                    </CardContent>
                  </Card>
                )
              }) : (
                <div className="text-center py-8">
                  <p className="text-gray-500">No predictions available</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'ratings' && ratings && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold text-gray-900">Team Ratings</h2>
              <p className="text-gray-600">
                Current ratings after GW{ratings.gameweek} • Last updated: {new Date(ratings.last_updated).toLocaleString()}
              </p>
            </div>

            <div className="grid gap-4">
              {ratings.ratings.map((team, index) => (
                <Card 
                  key={team.team} 
                  className="hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => fetchTeamDetails(team.team)}
                >
                  <CardContent className="flex items-center justify-between p-6">
                    <div className="flex items-center space-x-4">
                      <div className="text-2xl font-bold text-gray-400">
                        #{index + 1}
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold">{team.team}</h3>
                        {team.reason && (
                          <p className="text-sm text-gray-500">{team.reason}</p>
                        )}
                        <div className="flex items-center space-x-2 mt-1">
                          <span className="text-xs text-gray-400">
                            Base: {team.rating > 0 ? '+' : ''}{team.rating.toFixed(2)}
                          </span>
                          <span className="text-xs text-blue-600">
                            Form: {team.form_boost > 0 ? '+' : ''}{team.form_boost.toFixed(2)}
                          </span>
                          <span className="text-xs font-semibold text-green-600">
                            Effective: {team.effective_rating > 0 ? '+' : ''}{team.effective_rating.toFixed(2)}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${getTeamColor(team.effective_rating)}`}>
                        {team.effective_rating > 0 ? '+' : ''}{team.effective_rating.toFixed(2)}
                      </div>
                      <div className="text-sm text-gray-500">Effective Rating</div>
                      <div className="text-xs text-blue-600 mt-1">
                        Click for details →
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'team' && teamDetails && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold text-gray-900">{teamDetails.team}</h2>
              <p className="text-gray-600">
                Season {teamDetails.season} • Current Gameweek: {teamDetails.current_gameweek}
              </p>
            </div>

            {/* Team Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Current Rating</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-center">
                    <div className={`${getTeamColor(teamDetails.effective_rating)}`}>
                      {teamDetails.effective_rating > 0 ? '+' : ''}{teamDetails.effective_rating.toFixed(2)}
                    </div>
                    <div className="text-sm text-gray-500 mt-1">Effective Rating</div>
                  </div>
                  <div className="mt-4 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Base Rating:</span>
                      <span>{teamDetails.current_rating > 0 ? '+' : ''}{teamDetails.current_rating.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Form Boost:</span>
                      <span className={teamDetails.form_boost > 0 ? 'text-green-600' : 'text-red-600'}>
                        {teamDetails.form_boost > 0 ? '+' : ''}{teamDetails.form_boost.toFixed(2)}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Current Form</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600 mb-2">
                      {teamDetails.form_description}
                    </div>
                    <div className="flex justify-center space-x-1">
                      {teamDetails.form_results.map((result, index) => (
                        <span key={index} className="text-2xl">
                          {getFormResultIcon(result)}
                        </span>
                      ))}
                    </div>
                    <div className="text-sm text-gray-500 mt-2">
                      Last 5 games
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Rating Changes</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {teamDetails.rating_changes.length > 0 ? (
                      teamDetails.rating_changes.slice(0, 3).map((change, index) => (
                        <div key={index} className="flex justify-between items-center text-sm">
                          <span>GW{change.gameweek}:</span>
                          <span className={change.change > 0 ? 'text-green-600' : 'text-red-600'}>
                            {change.change > 0 ? '+' : ''}{change.change.toFixed(2)}
                          </span>
                        </div>
                      ))
                    ) : (
                      <div className="text-sm text-gray-500">No rating changes yet</div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Match History */}
            <div className="mb-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Match History</h3>
              <div className="grid gap-4">
                {teamDetails.match_history.map((match, index) => (
                  <Card key={index}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="text-lg font-bold text-gray-400">
                            GW{match.gameweek}
                          </div>
                          <div className="text-center">
                            <div className="font-semibold">
                              {match.is_home ? teamDetails.team : match.opponent}
                            </div>
                            <div className="text-sm text-gray-500">
                              {match.is_home ? 'Home' : 'Away'}
                            </div>
                          </div>
                          <div className="text-2xl font-bold">
                            {match.score}
                          </div>
                          <div className="text-center">
                            <div className="font-semibold">
                              {match.is_home ? match.opponent : teamDetails.team}
                            </div>
                            <div className="text-sm text-gray-500">
                              {match.is_home ? 'Away' : 'Home'}
                            </div>
                          </div>
                        </div>
                        <div className={`text-2xl font-bold ${getResultColor(match.result)}`}>
                          {match.result}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* Rating History Chart */}
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Rating History</h3>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    {teamDetails.rating_history.map((rating, index) => (
                      <div key={index} className="text-center">
                        <div className="text-sm text-gray-500 mb-1">GW{index + 1}</div>
                        <div className={`text-lg font-bold ${getTeamColor(rating)}`}>
                          {rating > 0 ? '+' : ''}{rating.toFixed(2)}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
