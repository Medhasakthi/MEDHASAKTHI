/**
 * Student Dashboard Screen
 */
import React from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { colors, typography, spacing } from '../../theme';

const { width } = Dimensions.get('window');

interface DashboardCardProps {
  title: string;
  value: string | number;
  icon: string;
  color: string;
  onPress?: () => void;
}

const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  value,
  icon,
  color,
  onPress,
}) => (
  <TouchableOpacity
    style={[styles.card, { borderLeftColor: color }]}
    onPress={onPress}
    activeOpacity={0.7}
  >
    <View style={styles.cardContent}>
      <View style={styles.cardLeft}>
        <Text style={styles.cardTitle}>{title}</Text>
        <Text style={styles.cardValue}>{value}</Text>
      </View>
      <View style={[styles.cardIcon, { backgroundColor: color }]}>
        <Icon name={icon} size={24} color={colors.white} />
      </View>
    </View>
  </TouchableOpacity>
);

interface QuickActionProps {
  title: string;
  icon: string;
  color: string;
  onPress?: () => void;
}

const QuickAction: React.FC<QuickActionProps> = ({
  title,
  icon,
  color,
  onPress,
}) => (
  <TouchableOpacity
    style={styles.quickAction}
    onPress={onPress}
    activeOpacity={0.7}
  >
    <View style={[styles.quickActionIcon, { backgroundColor: color }]}>
      <Icon name={icon} size={28} color={colors.white} />
    </View>
    <Text style={styles.quickActionTitle}>{title}</Text>
  </TouchableOpacity>
);

const StudentDashboardScreen: React.FC = () => {
  const handleCardPress = (type: string) => {
    console.log(`${type} card pressed`);
  };

  const handleQuickAction = (action: string) => {
    console.log(`${action} action pressed`);
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Welcome Section */}
      <View style={styles.welcomeSection}>
        <Text style={styles.welcomeText}>Welcome back!</Text>
        <Text style={styles.studentName}>John Doe</Text>
        <Text style={styles.subtitle}>Ready to continue your learning journey?</Text>
      </View>

      {/* Stats Cards */}
      <View style={styles.statsSection}>
        <Text style={styles.sectionTitle}>Your Progress</Text>
        <View style={styles.statsGrid}>
          <DashboardCard
            title="Completed Exams"
            value="12"
            icon="quiz"
            color={colors.success}
            onPress={() => handleCardPress('completed-exams')}
          />
          <DashboardCard
            title="Pending Exams"
            value="3"
            icon="pending-actions"
            color={colors.warning}
            onPress={() => handleCardPress('pending-exams')}
          />
          <DashboardCard
            title="Average Score"
            value="85%"
            icon="trending-up"
            color={colors.primary}
            onPress={() => handleCardPress('average-score')}
          />
          <DashboardCard
            title="Rank"
            value="#5"
            icon="emoji-events"
            color={colors.secondary}
            onPress={() => handleCardPress('rank')}
          />
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.quickActionsSection}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.quickActionsGrid}>
          <QuickAction
            title="Take Exam"
            icon="play-circle-filled"
            color={colors.primary}
            onPress={() => handleQuickAction('take-exam')}
          />
          <QuickAction
            title="View Results"
            icon="assessment"
            color={colors.success}
            onPress={() => handleQuickAction('view-results')}
          />
          <QuickAction
            title="Study Materials"
            icon="menu-book"
            color={colors.info}
            onPress={() => handleQuickAction('study-materials')}
          />
          <QuickAction
            title="Schedule"
            icon="event"
            color={colors.warning}
            onPress={() => handleQuickAction('schedule')}
          />
        </View>
      </View>

      {/* Recent Activity */}
      <View style={styles.recentSection}>
        <Text style={styles.sectionTitle}>Recent Activity</Text>
        <View style={styles.activityList}>
          <View style={styles.activityItem}>
            <View style={[styles.activityIcon, { backgroundColor: colors.success }]}>
              <Icon name="check-circle" size={20} color={colors.white} />
            </View>
            <View style={styles.activityContent}>
              <Text style={styles.activityTitle}>Mathematics Quiz Completed</Text>
              <Text style={styles.activityTime}>2 hours ago • Score: 92%</Text>
            </View>
          </View>
          
          <View style={styles.activityItem}>
            <View style={[styles.activityIcon, { backgroundColor: colors.info }]}>
              <Icon name="info" size={20} color={colors.white} />
            </View>
            <View style={styles.activityContent}>
              <Text style={styles.activityTitle}>Physics Exam Scheduled</Text>
              <Text style={styles.activityTime}>Tomorrow at 10:00 AM</Text>
            </View>
          </View>
          
          <View style={styles.activityItem}>
            <View style={[styles.activityIcon, { backgroundColor: colors.warning }]}>
              <Icon name="assignment" size={20} color={colors.white} />
            </View>
            <View style={styles.activityContent}>
              <Text style={styles.activityTitle}>Chemistry Assignment Due</Text>
              <Text style={styles.activityTime}>In 3 days</Text>
            </View>
          </View>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  welcomeSection: {
    padding: spacing.lg,
    backgroundColor: colors.surface,
    marginBottom: spacing.md,
  },
  welcomeText: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.medium,
    color: colors.textSecondary,
  },
  studentName: {
    fontSize: typography.sizes.xl,
    fontWeight: typography.weights.bold,
    color: colors.textPrimary,
    marginVertical: spacing.xs,
  },
  subtitle: {
    fontSize: typography.sizes.sm,
    color: colors.textSecondary,
  },
  statsSection: {
    padding: spacing.lg,
  },
  sectionTitle: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.semibold,
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  statsGrid: {
    gap: spacing.md,
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    borderLeftWidth: 4,
    elevation: 2,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  cardContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  cardLeft: {
    flex: 1,
  },
  cardTitle: {
    fontSize: typography.sizes.sm,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  cardValue: {
    fontSize: typography.sizes.xl,
    fontWeight: typography.weights.bold,
    color: colors.textPrimary,
  },
  cardIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  quickActionsSection: {
    padding: spacing.lg,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    gap: spacing.md,
  },
  quickAction: {
    width: (width - spacing.lg * 2 - spacing.md) / 2,
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    alignItems: 'center',
    elevation: 2,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  quickActionIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.sm,
  },
  quickActionTitle: {
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.medium,
    color: colors.textPrimary,
    textAlign: 'center',
  },
  recentSection: {
    padding: spacing.lg,
  },
  activityList: {
    gap: spacing.md,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    elevation: 1,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
  activityIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  activityContent: {
    flex: 1,
  },
  activityTitle: {
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.medium,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  activityTime: {
    fontSize: typography.sizes.xs,
    color: colors.textSecondary,
  },
});

export default StudentDashboardScreen;
