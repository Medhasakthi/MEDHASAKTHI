import React, { useState, useEffect } from 'react';
import {
  UsersIcon,
  AcademicCapIcon,
  ChartBarIcon,
  BookOpenIcon,
  ClockIcon,
  TrophyIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

// Import splash screen components
import PageSplashScreen from './PageSplashScreen';
import { useRouteSplashScreen } from '../hooks/useSplashScreen';

interface TeacherStats {
  total_students: number;
  classes_handled: number;
  subjects_taught: number;
  recent_exams: number;
  average_class_performance: number;
  total_messages_sent: number;
}

interface ClassInfo {
  class_id: string;
  class_name: string;
  section: string;
  subject: string;
  total_students: number;
  average_performance: number;
  recent_activity: string;
}

interface StudentPerformance {
  student_id: string;
  student_name: string;
  class_section: string;
  average_score: number;
  total_exams: number;
  last_exam_score?: number;
  improvement_trend: 'up' | 'down' | 'stable';
}

interface TeacherProfile {
  teacher_id: string;
  name: string;
  employee_id: string;
  department: string;
  subjects: string[];
  classes_assigned: string[];
  is_class_teacher: boolean;
  class_teacher_of?: string;
  institute_name: string;
}

const TeacherDashboard: React.FC = () => {
  const [stats, setStats] = useState<TeacherStats | null>(null);
  const [classes, setClasses] = useState<ClassInfo[]>([]);
  const [topPerformers, setTopPerformers] = useState<StudentPerformance[]>([]);
  const [needsAttention, setNeedsAttention] = useState<StudentPerformance[]>([]);
  const [profile, setProfile] = useState<TeacherProfile | null>(null);
  const [loading, setLoading] = useState(true);

  // Page splash screen for teacher dashboard
  const splash = useRouteSplashScreen('teacher-dashboard', 2000);
  const [activeTab, setActiveTab] = useState<'overview' | 'classes' | 'students' | 'analytics' | 'profile'>('overview');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch teacher dashboard data
      const dashboardResponse = await fetch('/api/v1/teacher/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const dashboardData = await dashboardResponse.json();
      
      if (dashboardData.status === 'success') {
        setStats(dashboardData.data.statistics);
        setClasses(dashboardData.data.assigned_classes);
        setTopPerformers(dashboardData.data.top_performers);
        setNeedsAttention(dashboardData.data.needs_attention);
        setProfile(dashboardData.data.teacher_info);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return '📈';
      case 'down': return '📉';
      default: return '➡️';
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up': return 'text-green-600';
      case 'down': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  // Show splash screen on first visit to teacher dashboard
  if (splash.isVisible) {
    return (
      <PageSplashScreen
        title="Teacher Dashboard"
        subtitle="Empowering Education Excellence"
        icon={<AcademicCapIcon className="w-8 h-8" />}
        color="#0d47a1"
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
              <h1 className="text-2xl font-bold text-gray-900">Teacher Dashboard</h1>
              {profile && (
                <p className="text-sm text-gray-600">
                  Welcome back, {profile.name} - {profile.department}
                  {profile.is_class_teacher && profile.class_teacher_of && (
                    <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                      Class Teacher: {profile.class_teacher_of}
                    </span>
                  )}
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
              { id: 'classes', name: 'My Classes', icon: AcademicCapIcon },
              { id: 'students', name: 'Students', icon: UsersIcon },
              { id: 'analytics', name: 'Analytics', icon: DocumentTextIcon },
              { id: 'profile', name: 'Profile', icon: BookOpenIcon }
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
                    <UsersIcon className="h-8 w-8 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Total Students</p>
                    <p className="text-2xl font-semibold text-gray-900">{stats.total_students}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <AcademicCapIcon className="h-8 w-8 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Classes</p>
                    <p className="text-2xl font-semibold text-gray-900">{stats.classes_handled}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <BookOpenIcon className="h-8 w-8 text-purple-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Subjects</p>
                    <p className="text-2xl font-semibold text-gray-900">{stats.subjects_taught}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <ChartBarIcon className="h-8 w-8 text-yellow-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Avg Performance</p>
                    <p className="text-2xl font-semibold text-gray-900">{stats.average_class_performance}%</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <ChatBubbleLeftRightIcon className="h-6 w-6 text-blue-600 mr-3" />
                  <span className="text-sm font-medium">Send Message to Class</span>
                </button>
                <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <DocumentTextIcon className="h-6 w-6 text-green-600 mr-3" />
                  <span className="text-sm font-medium">Create Assignment</span>
                </button>
                <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <TrophyIcon className="h-6 w-6 text-yellow-600 mr-3" />
                  <span className="text-sm font-medium">View Results</span>
                </button>
              </div>
            </div>

            {/* Student Performance Overview */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Top Performers */}
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">Top Performers</h3>
                </div>
                <div className="p-6">
                  {topPerformers.length > 0 ? (
                    <div className="space-y-4">
                      {topPerformers.slice(0, 5).map((student, index) => (
                        <div key={student.student_id} className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className="flex-shrink-0">
                              <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                                <span className="text-sm font-medium text-yellow-800">#{index + 1}</span>
                              </div>
                            </div>
                            <div className="ml-3">
                              <p className="text-sm font-medium text-gray-900">{student.student_name}</p>
                              <p className="text-xs text-gray-500">{student.class_section}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-medium text-gray-900">{student.average_score}%</p>
                            <p className={`text-xs ${getTrendColor(student.improvement_trend)}`}>
                              {getTrendIcon(student.improvement_trend)}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-center py-4">No performance data available</p>
                  )}
                </div>
              </div>

              {/* Students Needing Attention */}
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">Needs Attention</h3>
                </div>
                <div className="p-6">
                  {needsAttention.length > 0 ? (
                    <div className="space-y-4">
                      {needsAttention.slice(0, 5).map((student) => (
                        <div key={student.student_id} className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-900">{student.student_name}</p>
                            <p className="text-xs text-gray-500">{student.class_section}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-medium text-red-600">{student.average_score}%</p>
                            <button className="text-xs text-blue-600 hover:text-blue-800">
                              Send Message
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-center py-4">All students performing well!</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Classes Tab */}
        {activeTab === 'classes' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {classes.map((classInfo) => (
                <div key={classInfo.class_id} className="bg-white rounded-lg shadow p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      {classInfo.class_name} {classInfo.section}
                    </h3>
                    <span className="text-sm text-gray-500">{classInfo.subject}</span>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Students:</span>
                      <span className="text-sm font-medium">{classInfo.total_students}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Avg Performance:</span>
                      <span className="text-sm font-medium">{classInfo.average_performance}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Recent Activity:</span>
                      <span className="text-sm text-gray-500">{classInfo.recent_activity}</span>
                    </div>
                  </div>
                  
                  <div className="mt-4 flex space-x-2">
                    <button className="flex-1 bg-blue-600 text-white text-sm py-2 px-3 rounded hover:bg-blue-700">
                      View Details
                    </button>
                    <button className="flex-1 bg-gray-100 text-gray-700 text-sm py-2 px-3 rounded hover:bg-gray-200">
                      Send Message
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Students Tab */}
        {activeTab === 'students' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-lg font-medium text-gray-900">All Students</h3>
              <div className="flex space-x-2">
                <input
                  type="text"
                  placeholder="Search students..."
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm"
                />
                <select className="px-3 py-2 border border-gray-300 rounded-md text-sm">
                  <option value="">All Classes</option>
                  {classes.map((cls) => (
                    <option key={cls.class_id} value={cls.class_id}>
                      {cls.class_name} {cls.section}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Student
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Class
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Average Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total Exams
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Trend
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {[...topPerformers, ...needsAttention].map((student) => (
                    <tr key={student.student_id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{student.student_name}</div>
                        <div className="text-sm text-gray-500">{student.student_id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {student.class_section}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {student.average_score}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {student.total_exams}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-sm ${getTrendColor(student.improvement_trend)}`}>
                          {getTrendIcon(student.improvement_trend)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <button className="text-blue-600 hover:text-blue-900 mr-4">
                          View Profile
                        </button>
                        <button className="text-green-600 hover:text-green-900">
                          Send Message
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Analytics</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Class Performance Trends</h4>
                  <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                    <span className="text-gray-500">Chart will be rendered here</span>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Subject-wise Performance</h4>
                  <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                    <span className="text-gray-500">Chart will be rendered here</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Profile Tab */}
        {activeTab === 'profile' && profile && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Teacher Profile</h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Teacher ID</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.teacher_id}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Employee ID</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.employee_id}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Full Name</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Department</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.department}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Subjects</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.subjects.join(', ')}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Classes Assigned</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.classes_assigned.join(', ')}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Class Teacher</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {profile.is_class_teacher ? `Yes - ${profile.class_teacher_of}` : 'No'}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Institute</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.institute_name}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TeacherDashboard;
