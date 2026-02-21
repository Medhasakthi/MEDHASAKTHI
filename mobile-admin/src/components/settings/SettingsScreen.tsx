/**
 * Settings Screen
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

export default function SettingsScreen() {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.comingSoonContainer}>
          <Icon name="settings" size={80} color={colors.secondary} />
          <Text style={styles.comingSoonTitle}>System Settings</Text>
          <Text style={styles.comingSoonText}>
            Comprehensive system configuration and settings management coming soon!
          </Text>
          
          <View style={styles.featuresList}>
            <Text style={styles.featuresTitle}>Settings Features:</Text>
            <Text style={styles.featureItem}>• Platform configuration</Text>
            <Text style={styles.featureItem}>• User management settings</Text>
            <Text style={styles.featureItem}>• Security configurations</Text>
            <Text style={styles.featureItem}>• Email and notification settings</Text>
            <Text style={styles.featureItem}>• AI model configurations</Text>
            <Text style={styles.featureItem}>• Billing and subscription settings</Text>
            <Text style={styles.featureItem}>• System maintenance tools</Text>
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
