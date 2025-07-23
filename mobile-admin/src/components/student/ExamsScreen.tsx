/**
 * Student Exams Screen
 */
import React from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { colors, typography, spacing } from '../../theme';

interface ExamCardProps {
  title: string;
  subject: string;
  date: string;
  duration: string;
  status: 'upcoming' | 'ongoing' | 'completed';
  onPress?: () => void;
}

const ExamCard: React.FC<ExamCardProps> = ({
  title,
  subject,
  date,
  duration,
  status,
  onPress,
}) => {
  const getStatusColor = () => {
    switch (status) {
      case 'upcoming':
        return colors.warning;
      case 'ongoing':
        return colors.success;
      case 'completed':
        return colors.textSecondary;
      default:
        return colors.textSecondary;
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'upcoming':
        return 'schedule';
      case 'ongoing':
        return 'play-circle-filled';
      case 'completed':
        return 'check-circle';
      default:
        return 'help';
    }
  };

  return (
    <TouchableOpacity
      style={styles.examCard}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.examHeader}>
        <View style={styles.examInfo}>
          <Text style={styles.examTitle}>{title}</Text>
          <Text style={styles.examSubject}>{subject}</Text>
        </View>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor() }]}>
          <Icon name={getStatusIcon()} size={16} color={colors.white} />
        </View>
      </View>
      
      <View style={styles.examDetails}>
        <View style={styles.examDetail}>
          <Icon name="event" size={16} color={colors.textSecondary} />
          <Text style={styles.examDetailText}>{date}</Text>
        </View>
        <View style={styles.examDetail}>
          <Icon name="timer" size={16} color={colors.textSecondary} />
          <Text style={styles.examDetailText}>{duration}</Text>
        </View>
      </View>
      
      <View style={styles.examActions}>
        <Text style={[styles.statusText, { color: getStatusColor() }]}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </Text>
        {status === 'upcoming' && (
          <TouchableOpacity style={styles.actionButton}>
            <Text style={styles.actionButtonText}>Prepare</Text>
          </TouchableOpacity>
        )}
        {status === 'ongoing' && (
          <TouchableOpacity style={[styles.actionButton, styles.startButton]}>
            <Text style={[styles.actionButtonText, styles.startButtonText]}>Start</Text>
          </TouchableOpacity>
        )}
      </View>
    </TouchableOpacity>
  );
};

const ExamsScreen: React.FC = () => {
  const exams = [
    {
      id: '1',
      title: 'Mathematics Final Exam',
      subject: 'Mathematics',
      date: 'Today, 2:00 PM',
      duration: '2 hours',
      status: 'ongoing' as const,
    },
    {
      id: '2',
      title: 'Physics Quiz',
      subject: 'Physics',
      date: 'Tomorrow, 10:00 AM',
      duration: '1 hour',
      status: 'upcoming' as const,
    },
    {
      id: '3',
      title: 'Chemistry Test',
      subject: 'Chemistry',
      date: 'Dec 25, 9:00 AM',
      duration: '1.5 hours',
      status: 'upcoming' as const,
    },
    {
      id: '4',
      title: 'Biology Assessment',
      subject: 'Biology',
      date: 'Dec 20, 11:00 AM',
      duration: '2 hours',
      status: 'completed' as const,
    },
  ];

  const handleExamPress = (examId: string) => {
    console.log(`Exam ${examId} pressed`);
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Text style={styles.title}>Your Exams</Text>
        <Text style={styles.subtitle}>Manage your upcoming and completed exams</Text>
      </View>

      <View style={styles.examsList}>
        {exams.map((exam) => (
          <ExamCard
            key={exam.id}
            title={exam.title}
            subject={exam.subject}
            date={exam.date}
            duration={exam.duration}
            status={exam.status}
            onPress={() => handleExamPress(exam.id)}
          />
        ))}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    padding: spacing.lg,
    backgroundColor: colors.surface,
    marginBottom: spacing.md,
  },
  title: {
    fontSize: typography.sizes.xl,
    fontWeight: typography.weights.bold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: typography.sizes.sm,
    color: colors.textSecondary,
  },
  examsList: {
    padding: spacing.lg,
    gap: spacing.md,
  },
  examCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    elevation: 2,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  examHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.sm,
  },
  examInfo: {
    flex: 1,
  },
  examTitle: {
    fontSize: typography.sizes.md,
    fontWeight: typography.weights.semibold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  examSubject: {
    fontSize: typography.sizes.sm,
    color: colors.textSecondary,
  },
  statusBadge: {
    width: 32,
    height: 32,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  examDetails: {
    flexDirection: 'row',
    gap: spacing.lg,
    marginBottom: spacing.sm,
  },
  examDetail: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  examDetailText: {
    fontSize: typography.sizes.sm,
    color: colors.textSecondary,
  },
  examActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statusText: {
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.medium,
  },
  actionButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: colors.primary,
  },
  actionButtonText: {
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.medium,
    color: colors.primary,
  },
  startButton: {
    backgroundColor: colors.primary,
  },
  startButtonText: {
    color: colors.white,
  },
});

export default ExamsScreen;
