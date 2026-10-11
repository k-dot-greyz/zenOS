import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  Alert,
} from 'react-native';
import { useRoute, RouteProp } from '@react-navigation/native';
import { RootStackParamList } from '../types/navigation';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';

type PluginDetailsScreenRouteProp = RouteProp<RootStackParamList, 'PluginDetails'>;

const PluginDetailsScreen: React.FC = () => {
  const route = useRoute<PluginDetailsScreenRouteProp>();
  const { pluginId } = route.params;
  const { plugins, installedPlugins } = useSelector((state: RootState) => state.plugins);
  
  const plugin = [...plugins, ...installedPlugins].find(p => p.id === pluginId);
  
  if (!plugin) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Plugin not found</Text>
      </View>
    );
  }

  const isInstalled = installedPlugins.some(p => p.id === pluginId);

  const handleInstall = () => {
    Alert.alert('Install Plugin', `Install ${plugin.name}?`);
  };

  const handleRemove = () => {
    Alert.alert('Remove Plugin', `Remove ${plugin.name}?`);
  };

  const getCategoryIcon = (category: string) => {
    const icons: { [key: string]: string } = {
      'text-processing': '📝',
      'voice-processing': '🎤',
      'image-processing': '🖼️',
      'data-analysis': '📊',
      'api-integration': '🔗',
      'utilities': '🛠️',
    };
    return icons[category] || '🔌';
  };

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      'text-processing': '#4CAF50',
      'voice-processing': '#FF9800',
      'image-processing': '#9C27B0',
      'data-analysis': '#2196F3',
      'api-integration': '#00BCD4',
      'utilities': '#795548',
    };
    return colors[category] || '#666666';
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.titleContainer}>
          <Text style={styles.categoryIcon}>
            {getCategoryIcon(plugin.category)}
          </Text>
          <View style={styles.titleTextContainer}>
            <Text style={styles.name}>{plugin.name}</Text>
            <Text style={styles.author}>by {plugin.author}</Text>
          </View>
        </View>
        <View style={styles.statsContainer}>
          <Text style={styles.stars}>⭐ {plugin.stars}</Text>
          <Text style={styles.forks}>🍴 {plugin.forks}</Text>
        </View>
      </View>

      {/* Screenshots */}
      {plugin.screenshots && plugin.screenshots[0] && (
        <Image 
          source={{ uri: plugin.screenshots[0] }} 
          style={styles.screenshot}
          resizeMode="cover"
        />
      )}

      {/* Description */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Description</Text>
        <Text style={styles.description}>{plugin.description}</Text>
      </View>

      {/* Details */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Details</Text>
        <View style={styles.detailsGrid}>
          <View style={styles.detailItem}>
            <Text style={styles.detailLabel}>Version</Text>
            <Text style={styles.detailValue}>{plugin.version}</Text>
          </View>
          <View style={styles.detailItem}>
            <Text style={styles.detailLabel}>Category</Text>
            <Text style={[styles.detailValue, { color: getCategoryColor(plugin.category) }]}>
              {plugin.category}
            </Text>
          </View>
          <View style={styles.detailItem}>
            <Text style={styles.detailLabel}>Repository</Text>
            <Text style={styles.detailValue}>{plugin.repository}</Text>
          </View>
          <View style={styles.detailItem}>
            <Text style={styles.detailLabel}>Last Updated</Text>
            <Text style={styles.detailValue}>
              {new Date(plugin.lastUpdated).toLocaleDateString()}
            </Text>
          </View>
        </View>
      </View>

      {/* Tags */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Tags</Text>
        <View style={styles.tags}>
          {plugin.tags.map(tag => (
            <View 
              key={tag} 
              style={[
                styles.tag, 
                { backgroundColor: getCategoryColor(plugin.category) }
              ]}
            >
              <Text style={styles.tagText}>{tag}</Text>
            </View>
          ))}
        </View>
      </View>

      {/* Features */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Features</Text>
        <View style={styles.featuresList}>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>🔧</Text>
            <Text style={styles.featureText}>Configurable settings</Text>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>📱</Text>
            <Text style={styles.featureText}>Mobile optimized</Text>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureText}>🎤 Voice input support</Text>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureText}>⚡ Real-time processing</Text>
          </View>
        </View>
      </View>

      {/* Actions */}
      <View style={styles.actions}>
        {isInstalled ? (
          <TouchableOpacity 
            style={styles.removeButton}
            onPress={handleRemove}
          >
            <Text style={styles.removeButtonText}>🗑️ Remove Plugin</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity 
            style={styles.installButton}
            onPress={handleInstall}
          >
            <Text style={styles.installButtonText}>📦 Install Plugin</Text>
          </TouchableOpacity>
        )}
        
        <TouchableOpacity style={styles.configureButton}>
          <Text style={styles.configureButtonText}>⚙️ Configure</Text>
        </TouchableOpacity>
      </View>

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>
          This plugin is part of the zenOS ecosystem.{'\n'}
          Visit the repository for more information and updates.
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1a1a1a',
  },
  errorText: {
    color: '#f44336',
    fontSize: 18,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    padding: 20,
    paddingTop: 10,
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  categoryIcon: {
    fontSize: 32,
    marginRight: 16,
  },
  titleTextContainer: {
    flex: 1,
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  author: {
    fontSize: 16,
    color: '#888888',
  },
  statsContainer: {
    alignItems: 'flex-end',
  },
  stars: {
    fontSize: 16,
    color: '#FFD700',
    marginBottom: 4,
  },
  forks: {
    fontSize: 16,
    color: '#888888',
  },
  screenshot: {
    width: '100%',
    height: 200,
    backgroundColor: '#1a1a1a',
  },
  section: {
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#333333',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 12,
  },
  description: {
    fontSize: 16,
    color: '#cccccc',
    lineHeight: 24,
  },
  detailsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  detailItem: {
    width: '50%',
    marginBottom: 12,
  },
  detailLabel: {
    fontSize: 14,
    color: '#888888',
    marginBottom: 4,
  },
  detailValue: {
    fontSize: 16,
    color: '#ffffff',
    fontWeight: '500',
  },
  tags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  tag: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 8,
    marginBottom: 8,
  },
  tagText: {
    fontSize: 14,
    color: '#ffffff',
    fontWeight: '500',
  },
  featuresList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '50%',
    marginBottom: 12,
  },
  featureIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  featureText: {
    fontSize: 14,
    color: '#cccccc',
    flex: 1,
  },
  actions: {
    padding: 20,
  },
  installButton: {
    backgroundColor: '#4CAF50',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  installButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  removeButton: {
    backgroundColor: '#f44336',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  removeButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  configureButton: {
    backgroundColor: '#333333',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  configureButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  footer: {
    padding: 20,
    paddingBottom: 40,
  },
  footerText: {
    fontSize: 14,
    color: '#888888',
    textAlign: 'center',
    lineHeight: 20,
  },
});

export default PluginDetailsScreen;
