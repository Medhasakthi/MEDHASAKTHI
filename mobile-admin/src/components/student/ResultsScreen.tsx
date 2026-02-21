/**
 * Student Results Screen
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

interface ResultCardProps {
  examTitle: string;
  subject: string;
  score: number;
  totalMarks: number;
  percentage: number;
  grade: string;
  date: string;
  onPress?: () => void;
}

const ResultCard: React.FC<ResultCardProps> = ({
  examTitle,
  subject,
  score,
  totalMarks,
  percentage,
  grade,
  date,
  onPress,
}) => {
  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A+':
      case 'A':
        return colors.success;
      case 'B+':
      case 'B':
        return colors.primary;
      case 'C+':
      case 'C':
        return colors.warning;
      default:
        return colors.error;
    }
  };

  return (
    <TouchableOpacity
      style={styles.resultCard}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.resultHeader}>
        <View style={styles.resultInfo}>
          <Text style={styles.examTitle}>{examTitle}</Text>
          <Text style={styles.subject}>{subject}</Text>
          <Text style={styles.date}>{date}</Text>
        </View>
        <View style={[styles.gradeBadge, { backgroundColor: getGradeColor(grade) }]}>
          <Text style={styles.gradeText}>{grade}</Text>
        </View>
      </View>
      
      <View style={styles.scoreSection}>
        <View style={styles.scoreItem}>
          <Text style={styles.scoreLabel}>Score</Text>
          <Text style={styles.scoreValue}>{score}/{totalMarks}</Text>
        </View>
        <View style={styles.scoreItem}>
          <Text style={styles.scoreLabel}>Percentage</Text>
          <Text style={styles.scoreValue}>{percentage}%</Text>
        </View>
      </View>
      
      <View style={styles.progressBar}>
        <View 
          style={[
            styles.progressFill, 
            { 
              width: `${percentage}%`,
              backgroundColor: getGradeColor(grade)
            }
          ]} 
        />
      </View>
    </TouchableOpacity>
  );
};

const ResultsScreen: React.FC = () => {
  const results = [
    {
      id: '1',
      examTitle: 'Mathematics Final Exam',
      subject: 'Mathematics',
      score: 92,
      totalMarks: 100,
      percentage: 92,
      grade: 'A+',
      date: 'Dec 20, 2024',
    },
    {
      id: '2',
      examTitle: 'Physics Quiz',
      subject: 'Physics',
      score: 85,
      totalMarks: 100,
      percentage: 85,
      grade: 'A',
      date: 'Dec 18, 2024',
    },
    {
      id: '3',
      examTitle: 'Chemistry Test',
      subject: 'Chemistry',
      score: 78,
      totalMarks: 100,
      percentage: 78,
      grade: 'B+',
      date: 'Dec 15, 2024',
    },
    {
      id: '4',
      examTitle: 'Biology Assessment',
      subject: 'Biology',
      score: 88,
      totalMarks: 100,
      percentage: 88,
      grade: 'A',
      date: 'Dec 12, 2024',
    },
  ];

  const overallStats = {
    averageScore: 85.75,
    totalExams: 4,
    highestScore: 92,
    lowestScore: 78,
  };

  const handleResultPress = (resultId: string) => {
    console.log(`Result ${resultId} pressed`);
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Your Results</Text>
        <Text style={styles.subtitle}>Track your academic performance</Text>
      </View>

      {/* Overall Statistics */}
      <View style={styles.statsSection}>
        <Text style={styles.sectionTitle}>Overall Performance</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Icon name="trending-up" size={24} color={colors.primary} />
            <Text style={styles.statValue}>{overallStats.averageScore}%</Text>
            <Text style={styles.statLabel}>Average Score</Text>
          </View>
          <View style={styles.statCard}>
            <Icon name="quiz" size={24} color={colors.success} />
            <Text style={styles.statValue}>{overallStats.totalExams}</Text>
            <Text style={styles.statLabel}>Total Exams</Text>
          </View>
          <View style={styles.statCard}>
            <Icon name="star" size={24} color={colors.warning} />
            <Text style={styles.statValue}>{overallStats.highestScore}%</Text>
            <Text style={styles.statLabel}>Highest Score</Text>
          </View>
          <View style={styles.statCard}>
            <Icon name="show-chart" size={24} color={colors.info} />
            <Text style={styles.statValue}>{overallStats.lowestScore}%</Text>
            <Text style={styles.statLabel}>Lowest Score</Text>
          </View>
        </View>
      </View>

      {/* Results List */}
      <View style={styles.resultsSection}>
        <Text style={styles.sectionTitle}>Recent Results</Text>
        <View style={styles.resultsList}>
          {results.map((result) => (
            <ResultCard
              key={result.id}
              examTitle={result.examTitle}
              subject={result.subject}
              score={result.score}
              totalMarks={result.totalMarks}
              percentage={result.percentage}
              grade={result.grade}
              date={result.date}
              onPress={() => handleResultPress(result.id)}
            />
          ))}
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
  statsSection: {
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  sectionTitle: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.semibold,
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    justifyContent: 'space-between',
  },
  statCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    alignItems: 'center',
    width: '48%',
    elevation: 2,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  statValue: {
    fontSize: typography.sizes.xl,
    fontWeight: typography.weights.bold,
    color: colors.textPrimary,
    marginVertical: spacing.xs,
  },
  statLabel: {
    fontSize: typography.sizes.xs,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  resultsSection: {
    padding: spacing.lg,
  },
  resultsList: {
    gap: spacing.md,
  },
  resultCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    elevation: 2,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.sm,
  },
  resultInfo: {
    flex: 1,
  },
  examTitle: {
    fontSize: typography.sizes.md,
    fontWeight: typography.weights.semibold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  subject: {
    fontSize: typography.sizes.sm,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  date: {
    fontSize: typography.sizes.xs,
    color: colors.textSecondary,
  },
  gradeBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 6,
    minWidth: 40,
    alignItems: 'center',
  },
  gradeText: {
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.bold,
    color: colors.white,
  },
  scoreSection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  scoreItem: {
    alignItems: 'center',
  },
  scoreLabel: {
    fontSize: typography.sizes.xs,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  scoreValue: {
    fontSize: typography.sizes.md,
    fontWeight: typography.weights.semibold,
    color: colors.textPrimary,
  },
  progressBar: {
    height: 6,
    backgroundColor: colors.border,
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 3,
  },
});

export default ResultsScreen;
