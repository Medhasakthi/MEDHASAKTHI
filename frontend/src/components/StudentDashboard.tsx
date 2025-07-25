import React, { useState, useEffect } from 'react';
import {
  School as AcademicCapIcon,
  BarChart as ChartBarIcon,
  Description as DocumentTextIcon,
  Person as UserIcon,
  Schedule as ClockIcon,
  EmojiEvents as TrophyIcon,
  Warning as ExclamationTriangleIcon
} from '@mui/icons-material';

// Import splash screen components
import PageSplashScreen from './PageSplashScreen';
import { useRouteSplashScreen } from '../hooks/useSplashScreen';

interface StudentStats {
  total_exams_registered: number;
  exams_completed: number;
  average_score: number;
  certificates_earned: number;
  current_rank: number;
  improvement_percentage: number;
}

interface ExamRegistration {
  id: string;
  exam_name: string;
  exam_date: string;
  exam_time: string;
  status: string;
  score?: number;
  result?: string;
  certificate_available: boolean;
}

interface StudentProfile {
  student_id: string;
  name: string;
  class_level: string;
  section: string;
  institute_name: string;
  email: string;
  phone?: string;
  guardian_email?: string;
}

const StudentDashboard: React.FC = () => {
  const [stats, setStats] = useState<StudentStats | null>(null);
  const [recentExams, setRecentExams] = useState<ExamRegistration[]>([]);
  const [upcomingExams, setUpcomingExams] = useState<ExamRegistration[]>([]);
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Page splash screen
  const splash = useRouteSplashScreen('student-dashboard', 2000);
  const [activeTab, setActiveTab] = useState<'overview' | 'exams' | 'results' | 'profile'>('overview');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch dashboard data
      const dashboardResponse = await fetch('/api/v1/student/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const dashboardData = await dashboardResponse.json();
      
      if (dashboardData.status === 'success') {
        setStats(dashboardData.data.statistics);
        setRecentExams(dashboardData.data.recent_exams);
        setUpcomingExams(dashboardData.data.upcoming_exams);
        setProfile(dashboardData.data.student_info);
      }
    } catch (error) {
      // Handle dashboard data fetch error in production
      setError('Failed to load dashboard data. Please refresh the page.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'registered': return 'text-blue-600 bg-blue-100';
      case 'upcoming': return 'text-yellow-600 bg-yellow-100';
      case 'missed': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getResultColor = (result: string) => {
    switch (result?.toLowerCase()) {
      case 'pass': return 'text-green-600';
      case 'fail': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  // Show splash screen on first visit to dashboard
  if (splash.isVisible) {
    return (
      <PageSplashScreen
        title="Student Dashboard"
        subtitle="Your Learning Journey Awaits"
        icon={<AcademicCapIcon className="w-8 h-8" />}
        color="#1976d2"
        onComplete={splash.hide}
      />
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Student Dashboard</h1>
              {profile && (
                <p className="text-sm text-gray-600">
                  Welcome back, {profile.name} - {profile.class_level} {profile.section}
                </p>
              )}
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                {profile?.institute_name}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', name: 'Overview', icon: ChartBarIcon },
              { id: 'exams', name: 'My Exams', icon: DocumentTextIcon },
              { id: 'results', name: 'Results', icon: TrophyIcon },
              { id: 'profile', name: 'Profile', icon: UserIcon }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center`}
              >
                <tab.icon className="h-5 w-5 mr-2" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Overview Tab */}
        {activeTab === 'overview' && stats && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <DocumentTextIcon className="h-8 w-8 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Total Exams</p>
                    <p className="text-2xl font-semibold text-gray-900">{stats.total_exams_registered}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <AcademicCapIcon className="h-8 w-8 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Completed</p>
                    <p className="text-2xl font-semibold text-gray-900">{stats.exams_completed}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <ChartBarIcon className="h-8 w-8 text-purple-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Average Score</p>
                    <p className="text-2xl font-semibold text-gray-900">{stats.average_score}%</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <TrophyIcon className="h-8 w-8 text-yellow-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Certificates</p>
                    <p className="text-2xl font-semibold text-gray-900">{stats.certificates_earned}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Recent Exams */}
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">Recent Exams</h3>
                </div>
                <div className="p-6">
                  {recentExams.length > 0 ? (
                    <div className="space-y-4">
                      {recentExams.slice(0, 5).map((exam) => (
                        <div key={exam.id} className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-900">{exam.exam_name}</p>
                            <p className="text-xs text-gray-500">{exam.exam_date}</p>
                          </div>
                          <div className="text-right">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(exam.status)}`}>
                              {exam.status}
                            </span>
                            {exam.score && (
                              <p className="text-sm font-medium text-gray-900 mt-1">{exam.score}%</p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-center py-4">No recent exams</p>
                  )}
                </div>
              </div>

              {/* Upcoming Exams */}
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">Upcoming Exams</h3>
                </div>
                <div className="p-6">
                  {upcomingExams.length > 0 ? (
                    <div className="space-y-4">
                      {upcomingExams.slice(0, 5).map((exam) => (
                        <div key={exam.id} className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-900">{exam.exam_name}</p>
                            <p className="text-xs text-gray-500">{exam.exam_date} at {exam.exam_time}</p>
                          </div>
                          <div>
                            <ClockIcon className="h-5 w-5 text-yellow-500" />
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-center py-4">No upcoming exams</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Exams Tab */}
        {activeTab === 'exams' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">My Exam Registrations</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Exam Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date & Time
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {[...recentExams, ...upcomingExams].map((exam) => (
                    <tr key={exam.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {exam.exam_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {exam.exam_date} {exam.exam_time && `at ${exam.exam_time}`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(exam.status)}`}>
                          {exam.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {exam.status === 'upcoming' && (
                          <button className="text-blue-600 hover:text-blue-900">
                            Take Exam
                          </button>
                        )}
                        {exam.certificate_available && (
                          <button className="text-green-600 hover:text-green-900 ml-4">
                            Download Certificate
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Results Tab */}
        {activeTab === 'results' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Exam Results</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Exam Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Result
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Certificate
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {recentExams.filter(exam => exam.score !== undefined).map((exam) => (
                    <tr key={exam.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {exam.exam_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {exam.exam_date}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {exam.score}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-sm font-medium ${getResultColor(exam.result || '')}`}>
                          {exam.result?.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {exam.certificate_available ? (
                          <button className="text-green-600 hover:text-green-900">
                            Download
                          </button>
                        ) : (
                          <span className="text-gray-400">Not Available</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Profile Tab */}
        {activeTab === 'profile' && profile && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Student Profile</h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Student ID</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.student_id}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Full Name</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Class</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.class_level} {profile.section}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Institute</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.institute_name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Email</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.email}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Phone</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.phone || 'Not provided'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Guardian Email</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.guardian_email || 'Not provided'}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentDashboard;
