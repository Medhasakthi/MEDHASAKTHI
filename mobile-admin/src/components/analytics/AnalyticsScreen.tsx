/**
 * Analytics Screen
 */
import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { colors, typography, spacing, borderRadius } from '../../theme';

export default function AnalyticsScreen() {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.comingSoonContainer}>
          <Icon name="analytics" size={80} color={colors.success} />
          <Text style={styles.comingSoonTitle}>Advanced Analytics</Text>
          <Text style={styles.comingSoonText}>
            Comprehensive analytics dashboard with detailed insights coming soon!
          </Text>
          
          <View style={styles.featuresList}>
            <Text style={styles.featuresTitle}>Analytics Features:</Text>
            <Text style={styles.featureItem}>• Real-time platform metrics</Text>
            <Text style={styles.featureItem}>• User engagement analytics</Text>
            <Text style={styles.featureItem}>• AI usage statistics</Text>
            <Text style={styles.featureItem}>• Revenue and billing insights</Text>
            <Text style={styles.featureItem}>• Performance benchmarking</Text>
            <Text style={styles.featureItem}>• Custom report generation</Text>
            <Text style={styles.featureItem}>• Data export capabilities</Text>
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
  content: {
    flex: 1,
    padding: spacing.lg,
  },
  comingSoonContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.xl,
    marginTop: spacing.xl,
  },
  comingSoonTitle: {
    fontSize: typography.sizes.xxl,
    fontWeight: typography.weights.bold,
    color: colors.text,
    textAlign: 'center',
    marginTop: spacing.lg,
    marginBottom: spacing.md,
  },
  comingSoonText: {
    fontSize: typography.sizes.md,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: typography.lineHeights.relaxed * typography.sizes.md,
    marginBottom: spacing.xl,
  },
  featuresList: {
    alignSelf: 'stretch',
  },
  featuresTitle: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.semibold,
    color: colors.text,
    marginBottom: spacing.md,
  },
  featureItem: {
    fontSize: typography.sizes.md,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
    lineHeight: typography.lineHeights.normal * typography.sizes.md,
  },
});
