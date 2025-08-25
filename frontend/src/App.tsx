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
  change_from_previous?: number
  reason?: string
}

interface TeamRatingsResponse {
  season: string
  gameweek: number
  ratings: TeamRating[]
  last_updated: string
}

const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [predictions, setPredictions] = useState<GameweekPredictions | null>(null)
  const [ratings, setRatings] = useState<TeamRatingsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'predictions' | 'ratings'>('predictions')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const [predictionsRes, ratingsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/predictions/2`),
        axios.get(`${API_BASE_URL}/ratings`)
      ])
      
      setPredictions(predictionsRes.data)
      setRatings(ratingsRes.data)
    } catch (err) {
      setError('Failed to fetch data. Make sure the backend server is running.')
      console.error('Error fetching data:', err)
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
              {predictions.predictions.map((match, index) => {
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
              })}
            </div>
          </div>
        )}

        {activeTab === 'ratings' && ratings && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold text-gray-900">Team Ratings</h2>
              <p className="text-gray-600">
                Current ratings after GW{ratings.gameweek - 1} • Last updated: {new Date(ratings.last_updated).toLocaleString()}
              </p>
            </div>

            <div className="grid gap-4">
              {ratings.ratings.map((team, index) => (
                <Card key={team.team} className="hover:shadow-lg transition-shadow">
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
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${getTeamColor(team.rating)}`}>
                        {team.rating > 0 ? '+' : ''}{team.rating}
                      </div>
                      <div className="text-sm text-gray-500">Rating</div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
