/**
 * Student Top App Bar Usage Example
 * This demonstrates how to use the StudentTopAppBar component
 */
import React from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
} from 'react-native';
import StudentTopAppBar from '../common/StudentTopAppBar';
import { colors, typography, spacing } from '../../theme';

const StudentTopAppBarExample: React.FC = () => {
  const handleNotificationPress = () => {
    console.log('Notification pressed');
    // Navigate to notifications screen
  };

  const handleProfilePress = () => {
    console.log('Profile pressed');
    // Navigate to profile screen
  };

  const handleBackPress = () => {
    console.log('Back pressed');
    // Navigate back
  };

  return (
    <View style={styles.container}>
      {/* Example 1: Default Student App Bar */}
      <StudentTopAppBar
        instituteName="Demo High School"
        instituteLogo="https://example.com/logo.png" // Optional
        onNotificationPress={handleNotificationPress}
        onProfilePress={handleProfilePress}
        notificationCount={5}
      />

      <ScrollView style={styles.content}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Student Top App Bar Examples</Text>
          
          <View style={styles.example}>
            <Text style={styles.exampleTitle}>1. Default Layout</Text>
            <Text style={styles.exampleDescription}>
              • Left: MEDHASAKTHI logo and name{'\n'}
              • Center: Institute logo and name{'\n'}
              • Right: Notification and profile buttons
            </Text>
          </View>

          <View style={styles.example}>
            <Text style={styles.exampleTitle}>2. With Back Button</Text>
            <Text style={styles.exampleDescription}>
              Use showBackButton=true for detail screens
            </Text>
          </View>

          <View style={styles.example}>
            <Text style={styles.exampleTitle}>3. With Custom Title</Text>
            <Text style={styles.exampleDescription}>
              Use title prop to show screen title instead of institute info
            </Text>
          </View>

          <View style={styles.example}>
            <Text style={styles.exampleTitle}>4. Notification Badge</Text>
            <Text style={styles.exampleDescription}>
              Shows unread notification count (current: 5)
            </Text>
          </View>
        </View>

        {/* Example variations */}
        <View style={styles.variations}>
          <Text style={styles.sectionTitle}>Usage Variations</Text>
          
          <View style={styles.codeBlock}>
            <Text style={styles.codeTitle}>Basic Usage:</Text>
            <Text style={styles.code}>
{`<StudentTopAppBar
  instituteName="Demo High School"
  onNotificationPress={handleNotificationPress}
  onProfilePress={handleProfilePress}
  notificationCount={5}
/>`}
            </Text>
          </View>

          <View style={styles.codeBlock}>
            <Text style={styles.codeTitle}>With Back Button:</Text>
            <Text style={styles.code}>
{`<StudentTopAppBar
  title="Exam Details"
  showBackButton={true}
  onBackPress={handleBackPress}
  onNotificationPress={handleNotificationPress}
/>`}
            </Text>
          </View>

          <View style={styles.codeBlock}>
            <Text style={styles.codeTitle}>With Institute Logo:</Text>
            <Text style={styles.code}>
{`<StudentTopAppBar
  instituteName="Demo High School"
  instituteLogo="https://example.com/logo.png"
  onNotificationPress={handleNotificationPress}
  onProfilePress={handleProfilePress}
/>`}
            </Text>
          </View>
        </View>

        <View style={styles.features}>
          <Text style={styles.sectionTitle}>Features</Text>
          
          <View style={styles.featureList}>
            <Text style={styles.feature}>✅ Responsive layout that adapts to content</Text>
            <Text style={styles.feature}>✅ Notification badge with count</Text>
            <Text style={styles.feature}>✅ Support for institute logo or default icon</Text>
            <Text style={styles.feature}>✅ Back button for navigation</Text>
            <Text style={styles.feature}>✅ Custom title support</Text>
            <Text style={styles.feature}>✅ Consistent with MEDHASAKTHI branding</Text>
            <Text style={styles.feature}>✅ Material Design icons</Text>
            <Text style={styles.feature}>✅ Safe area handling</Text>
          </View>
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    flex: 1,
    padding: spacing.lg,
  },
  section: {
    marginBottom: spacing.xl,
  },
  sectionTitle: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.bold,
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  example: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
    elevation: 2,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  exampleTitle: {
    fontSize: typography.sizes.md,
    fontWeight: typography.weights.semibold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  exampleDescription: {
    fontSize: typography.sizes.sm,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  variations: {
    marginBottom: spacing.xl,
  },
  codeBlock: {
    backgroundColor: colors.surface,
    borderRadius: 8,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderLeftWidth: 4,
    borderLeftColor: colors.primary,
  },
  codeTitle: {
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.semibold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  code: {
    fontSize: typography.sizes.xs,
    fontFamily: 'monospace',
    color: colors.textSecondary,
    lineHeight: 18,
  },
  features: {
    marginBottom: spacing.xl,
  },
  featureList: {
    gap: spacing.sm,
  },
  feature: {
    fontSize: typography.sizes.sm,
    color: colors.textSecondary,
    lineHeight: 20,
  },
});

export default StudentTopAppBarExample;
