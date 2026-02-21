/**
 * Institutes Management Screen
 */
import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { colors, typography, spacing, borderRadius } from '../../theme';

interface InstitutesScreenProps {
  navigation: any;
}

export default function InstitutesScreen({ navigation }: InstitutesScreenProps) {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.comingSoonContainer}>
          <Icon name="school" size={80} color={colors.primary} />
          <Text style={styles.comingSoonTitle}>Institute Management</Text>
          <Text style={styles.comingSoonText}>
            Comprehensive institute management features coming soon!
          </Text>
          
          <View style={styles.featuresList}>
            <Text style={styles.featuresTitle}>Planned Features:</Text>
            <Text style={styles.featureItem}>• Institute registration and verification</Text>
            <Text style={styles.featureItem}>• Subscription management</Text>
            <Text style={styles.featureItem}>• User analytics per institute</Text>
            <Text style={styles.featureItem}>• Billing and payment tracking</Text>
            <Text style={styles.featureItem}>• Performance monitoring</Text>
            <Text style={styles.featureItem}>• Support ticket integration</Text>
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
