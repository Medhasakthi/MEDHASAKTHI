/**
 * Dashboard Screen for Mobile Admin App
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';
import { LineChart, PieChart } from 'react-native-chart-kit';

import { apiService } from '../../services/ApiService';
import { PlatformAnalytics, InstituteStats } from '../../types';
import { colors, typography, spacing, borderRadius } from '../../theme';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';

const { width: screenWidth } = Dimensions.get('window');

interface DashboardScreenProps {
  navigation: any;
}

export default function DashboardScreen({ navigation }: DashboardScreenProps) {
  const [analytics, setAnalytics] = useState<PlatformAnalytics | null>(null);
  const [instituteStats, setInstituteStats] = useState<InstituteStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useFocusEffect(
    useCallback(() => {
      loadDashboardData();
    }, [])
  );

  const loadDashboardData = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }
      setError(null);

      const [analyticsData, statsData] = await Promise.all([
        apiService.getPlatformAnalytics('30d'),
        apiService.getInstituteStats(),
      ]);

      setAnalytics(analyticsData);
      setInstituteStats(statsData);
    } catch (error: any) {
      setError(error.message || 'Failed to load dashboard data');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  const handleRefresh = () => {
    loadDashboardData(true);
  };

  const StatCard = ({ 
    title, 
    value, 
    icon, 
    color, 
    trend, 
    onPress 
  }: {
    title: string;
    value: string | number;
    icon: string;
    color: string;
    trend?: string;
    onPress?: () => void;
  }) => (
    <TouchableOpacity
      style={[styles.statCard, { borderLeftColor: color }]}
      onPress={onPress}
      disabled={!onPress}
    >
      <View style={styles.statCardHeader}>
        <View style={[styles.statIcon, { backgroundColor: color }]}>
          <Icon name={icon} size={24} color={colors.white} />
        </View>
        <View style={styles.statContent}>
          <Text style={styles.statValue}>
            {typeof value === 'number' ? value.toLocaleString() : value}
          </Text>
          <Text style={styles.statTitle}>{title}</Text>
          {trend && (
            <Text style={[styles.statTrend, { color }]}>{trend}</Text>
          )}
        </View>
      </View>
    </TouchableOpacity>
  );

  const QuickAction = ({ 
    title, 
    icon, 
    color, 
    onPress 
  }: {
    title: string;
    icon: string;
    color: string;
    onPress: () => void;
  }) => (
    <TouchableOpacity style={styles.quickAction} onPress={onPress}>
      <LinearGradient
        colors={[color, `${color}CC`]}
        style={styles.quickActionGradient}
      >
        <Icon name={icon} size={32} color={colors.white} />
        <Text style={styles.quickActionText}>{title}</Text>
      </LinearGradient>
    </TouchableOpacity>
  );

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <ErrorMessage
        message={error}
        onRetry={() => loadDashboardData()}
      />
    );
  }

  const chartConfig = {
    backgroundColor: colors.surface,
    backgroundGradientFrom: colors.surface,
    backgroundGradientTo: colors.surface,
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(102, 126, 234, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(51, 51, 51, ${opacity})`,
    style: {
      borderRadius: borderRadius.md,
    },
    propsForDots: {
      r: '4',
      strokeWidth: '2',
      stroke: colors.primary,
    },
  };

  const userGrowthData = {
    labels: analytics?.user_growth.slice(-7).map(item => 
      new Date(item.date).toLocaleDateString('en', { month: 'short', day: 'numeric' })
    ) || [],
    datasets: [{
      data: analytics?.user_growth.slice(-7).map(item => item.new_users) || [],
      color: (opacity = 1) => `rgba(102, 126, 234, ${opacity})`,
      strokeWidth: 2,
    }],
  };

  const institutePieData = [
    {
      name: 'Active',
      population: instituteStats?.active_institutes || 0,
      color: colors.success,
      legendFontColor: colors.text,
      legendFontSize: 12,
    },
    {
      name: 'Pending',
      population: instituteStats?.pending_verification || 0,
      color: colors.warning,
      legendFontColor: colors.text,
      legendFontSize: 12,
    },
    {
      name: 'Inactive',
      population: (instituteStats?.total_institutes || 0) - (instituteStats?.active_institutes || 0) - (instituteStats?.pending_verification || 0),
      color: colors.error,
      legendFontColor: colors.text,
      legendFontSize: 12,
    },
  ];

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl
          refreshing={isRefreshing}
          onRefresh={handleRefresh}
          colors={[colors.primary]}
        />
      }
    >
      {/* Header */}
      <LinearGradient
        colors={colors.gradientPrimary}
        style={styles.header}
      >
        <Text style={styles.headerTitle}>Platform Overview</Text>
        <Text style={styles.headerSubtitle}>
          Real-time insights and management
        </Text>
      </LinearGradient>

      {/* Stats Cards */}
      <View style={styles.statsContainer}>
        <StatCard
          title="Total Institutes"
          value={instituteStats?.total_institutes || 0}
          icon="school"
          color={colors.primary}
          trend={`+${instituteStats?.monthly_growth || 0}% this month`}
          onPress={() => navigation.navigate('Institutes')}
        />
        
        <StatCard
          title="Active Users"
          value={analytics?.overview.total_users || 0}
          icon="people"
          color={colors.success}
          trend="+12% this week"
          onPress={() => navigation.navigate('Analytics')}
        />
        
        <StatCard
          title="AI Questions Generated"
          value={analytics?.overview.total_questions_generated || 0}
          icon="psychology"
          color={colors.secondary}
          trend={`${analytics?.ai_usage.success_rate.toFixed(1) || 0}% success rate`}
        />
        
        <StatCard
          title="Monthly Revenue"
          value={`$${(analytics?.revenue.monthly_recurring_revenue || 0).toLocaleString()}`}
          icon="attach-money"
          color={colors.warning}
          trend="+8% vs last month"
        />
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.quickActionsGrid}>
          <QuickAction
            title="Add Institute"
            icon="add-business"
            color={colors.primary}
            onPress={() => navigation.navigate('AddInstitute')}
          />
          <QuickAction
            title="View Support"
            icon="support-agent"
            color={colors.info}
            onPress={() => navigation.navigate('Support')}
          />
          <QuickAction
            title="System Config"
            icon="settings"
            color={colors.secondary}
            onPress={() => navigation.navigate('SystemConfig')}
          />
          <QuickAction
            title="Analytics"
            icon="analytics"
            color={colors.success}
            onPress={() => navigation.navigate('Analytics')}
          />
        </View>
      </View>

      {/* User Growth Chart */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>User Growth (Last 7 Days)</Text>
        <View style={styles.chartContainer}>
          <LineChart
            data={userGrowthData}
            width={screenWidth - 40}
            height={200}
            chartConfig={chartConfig}
            bezier
            style={styles.chart}
          />
        </View>
      </View>

      {/* Institute Distribution */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Institute Status Distribution</Text>
        <View style={styles.chartContainer}>
          <PieChart
            data={institutePieData}
            width={screenWidth - 40}
            height={200}
            chartConfig={chartConfig}
            accessor="population"
            backgroundColor="transparent"
            paddingLeft="15"
            style={styles.chart}
          />
        </View>
      </View>

      {/* System Health */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>System Health</Text>
        <View style={styles.healthContainer}>
          <View style={styles.healthItem}>
            <Text style={styles.healthLabel}>Platform Uptime</Text>
            <Text style={[styles.healthValue, { color: colors.success }]}>
              {analytics?.overview.platform_uptime.toFixed(2) || 0}%
            </Text>
          </View>
          <View style={styles.healthItem}>
            <Text style={styles.healthLabel}>API Response Time</Text>
            <Text style={[styles.healthValue, { color: colors.info }]}>
              {analytics?.overview.api_response_time || 0}ms
            </Text>
          </View>
          <View style={styles.healthItem}>
            <Text style={styles.healthLabel}>Error Rate</Text>
            <Text style={[styles.healthValue, { color: colors.warning }]}>
              {analytics?.system_health.error_rate.toFixed(2) || 0}%
            </Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    padding: spacing.xl,
    paddingTop: spacing.xxl,
  },
  headerTitle: {
    fontSize: typography.sizes.xxl,
    fontWeight: typography.weights.bold,
    color: colors.white,
  },
  headerSubtitle: {
    fontSize: typography.sizes.md,
    color: colors.white,
    opacity: 0.9,
    marginTop: spacing.xs,
  },
  statsContainer: {
    padding: spacing.lg,
    gap: spacing.md,
  },
  statCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    borderLeftWidth: 4,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statCardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statIcon: {
    width: 48,
    height: 48,
    borderRadius: borderRadius.round,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  statContent: {
    flex: 1,
  },
  statValue: {
    fontSize: typography.sizes.xl,
    fontWeight: typography.weights.bold,
    color: colors.text,
  },
  statTitle: {
    fontSize: typography.sizes.sm,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  statTrend: {
    fontSize: typography.sizes.xs,
    fontWeight: typography.weights.medium,
    marginTop: spacing.xs,
  },
  section: {
    padding: spacing.lg,
  },
  sectionTitle: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.semibold,
    color: colors.text,
    marginBottom: spacing.md,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
  },
  quickAction: {
    width: (screenWidth - spacing.lg * 3) / 2,
    borderRadius: borderRadius.lg,
    overflow: 'hidden',
  },
  quickActionGradient: {
    padding: spacing.lg,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 100,
  },
  quickActionText: {
    color: colors.white,
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.medium,
    marginTop: spacing.sm,
    textAlign: 'center',
  },
  chartContainer: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    alignItems: 'center',
  },
  chart: {
    borderRadius: borderRadius.md,
  },
  healthContainer: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
  },
  healthItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  healthLabel: {
    fontSize: typography.sizes.md,
    color: colors.textSecondary,
  },
  healthValue: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.semibold,
  },
});
