/**
 * Support Screen
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

export default function SupportScreen() {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.comingSoonContainer}>
          <Icon name="support-agent" size={80} color={colors.info} />
          <Text style={styles.comingSoonTitle}>Support Management</Text>
          <Text style={styles.comingSoonText}>
            Advanced support ticket management system coming soon!
          </Text>
          
          <View style={styles.featuresList}>
            <Text style={styles.featuresTitle}>Support Features:</Text>
            <Text style={styles.featureItem}>• Ticket management dashboard</Text>
            <Text style={styles.featureItem}>• Priority-based ticket sorting</Text>
            <Text style={styles.featureItem}>• Real-time chat support</Text>
            <Text style={styles.featureItem}>• Knowledge base integration</Text>
            <Text style={styles.featureItem}>• Automated ticket routing</Text>
            <Text style={styles.featureItem}>• Performance metrics</Text>
            <Text style={styles.featureItem}>• Customer satisfaction tracking</Text>
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
