import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Image,
  Dimensions,
} from 'react-native';
import { Plugin } from '../types/plugin';

const { width } = Dimensions.get('window');

interface PluginCardProps {
  plugin: Plugin;
  onInstall: () => void;
  onRemove: () => void;
  onPress: () => void;
  featured?: boolean;
  installed?: boolean;
}

const PluginCard: React.FC<PluginCardProps> = ({
  plugin,
  onInstall,
  onRemove,
  onPress,
  featured = false,
  installed = false,
}) => {
  const {
    name,
    description,
    author,
    stars,
    category,
    tags,
    screenshots,
  } = plugin;

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
    <TouchableOpacity 
      style={[
        styles.card, 
        featured && styles.featuredCard,
        installed && styles.installedCard
      ]}
      onPress={onPress}
      activeOpacity={0.8}
    >
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.titleContainer}>
          <Text style={styles.categoryIcon}>
            {getCategoryIcon(category)}
          </Text>
          <View style={styles.titleTextContainer}>
            <Text style={styles.name} numberOfLines={1}>
              {name}
            </Text>
            <Text style={styles.author}>by {author}</Text>
          </View>
        </View>
        <View style={styles.statsContainer}>
          <Text style={styles.stars}>⭐ {stars}</Text>
          {featured && <Text style={styles.featuredBadge}>FEATURED</Text>}
          {installed && <Text style={styles.installedBadge}>INSTALLED</Text>}
        </View>
      </View>

      {/* Screenshot */}
      {screenshots && screenshots[0] && (
        <Image 
          source={{ uri: screenshots[0] }} 
          style={styles.screenshot}
          resizeMode="cover"
        />
      )}

      {/* Content */}
      <View style={styles.content}>
        <Text style={styles.description} numberOfLines={2}>
          {description}
        </Text>
        
        {/* Tags */}
        <View style={styles.tags}>
          {tags.slice(0, 3).map(tag => (
            <View 
              key={tag} 
              style={[
                styles.tag, 
                { backgroundColor: getCategoryColor(category) }
              ]}
            >
              <Text style={styles.tagText}>{tag}</Text>
            </View>
          ))}
        </View>
      </View>

      {/* Actions */}
      <View style={styles.actions}>
        <TouchableOpacity 
          style={styles.previewButton}
          onPress={onPress}
        >
          <Text style={styles.previewText}>👁️ Preview</Text>
        </TouchableOpacity>
        
        {installed ? (
          <TouchableOpacity 
            style={styles.removeButton}
            onPress={onRemove}
          >
            <Text style={styles.removeText}>🗑️ Remove</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity 
            style={styles.installButton}
            onPress={onInstall}
          >
            <Text style={styles.installText}>📦 Install</Text>
          </TouchableOpacity>
        )}
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#2a2a2a',
    borderRadius: 12,
    marginBottom: 16,
    overflow: 'hidden',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
  },
  featuredCard: {
    borderWidth: 2,
    borderColor: '#FFD700',
  },
  installedCard: {
    borderWidth: 2,
    borderColor: '#4CAF50',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    padding: 16,
    paddingBottom: 8,
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  categoryIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  titleTextContainer: {
    flex: 1,
  },
  name: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 2,
  },
  author: {
    fontSize: 14,
    color: '#888888',
  },
  statsContainer: {
    alignItems: 'flex-end',
  },
  stars: {
    fontSize: 14,
    color: '#FFD700',
    marginBottom: 4,
  },
  featuredBadge: {
    fontSize: 10,
    color: '#FFD700',
    fontWeight: 'bold',
    backgroundColor: 'rgba(255, 215, 0, 0.2)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  installedBadge: {
    fontSize: 10,
    color: '#4CAF50',
    fontWeight: 'bold',
    backgroundColor: 'rgba(76, 175, 80, 0.2)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  screenshot: {
    width: '100%',
    height: 120,
    backgroundColor: '#1a1a1a',
  },
  content: {
    padding: 16,
    paddingTop: 8,
  },
  description: {
    fontSize: 14,
    color: '#cccccc',
    lineHeight: 20,
    marginBottom: 12,
  },
  tags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  tag: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 8,
    marginBottom: 4,
  },
  tagText: {
    fontSize: 12,
    color: '#ffffff',
    fontWeight: '500',
  },
  actions: {
    flexDirection: 'row',
    padding: 16,
    paddingTop: 0,
  },
  previewButton: {
    flex: 1,
    backgroundColor: '#333333',
    paddingVertical: 12,
    borderRadius: 8,
    marginRight: 8,
    alignItems: 'center',
  },
  previewText: {
    color: '#ffffff',
    fontWeight: 'bold',
    fontSize: 14,
  },
  installButton: {
    flex: 1,
    backgroundColor: '#4CAF50',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  installText: {
    color: '#ffffff',
    fontWeight: 'bold',
    fontSize: 14,
  },
  removeButton: {
    flex: 1,
    backgroundColor: '#f44336',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  removeText: {
    color: '#ffffff',
    fontWeight: 'bold',
    fontSize: 14,
  },
});

export default PluginCard;
