import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  TextInput,
  ActivityIndicator,
  Alert,
  Dimensions,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../types/navigation';
import { RootState } from '../store/store';
import { 
  searchPlugins, 
  installPlugin, 
  removePlugin,
  setSearchQuery,
  setSelectedCategory 
} from '../store/slices/pluginSlice';
import PluginCard from '../components/PluginCard';
import CategoryFilter from '../components/CategoryFilter';

const { width } = Dimensions.get('window');

type PluginManagerScreenNavigationProp = StackNavigationProp<RootStackParamList, 'PluginManager'>;

const PluginManagerScreen: React.FC = () => {
  const dispatch = useDispatch();
  const navigation = useNavigation<PluginManagerScreenNavigationProp>();
  const { plugins, installedPlugins, loading, searchQuery, selectedCategory } = useSelector(
    (state: RootState) => state.plugins
  );

  const [localSearchQuery, setLocalSearchQuery] = useState('');

  const categories = [
    { id: 'all', name: 'All', icon: '🔍' },
    { id: 'text-processing', name: 'Text', icon: '📝' },
    { id: 'voice-processing', name: 'Voice', icon: '🎤' },
    { id: 'image-processing', name: 'Images', icon: '🖼️' },
    { id: 'data-analysis', name: 'Data', icon: '📊' },
    { id: 'api-integration', name: 'APIs', icon: '🔗' },
    { id: 'utilities', name: 'Tools', icon: '🛠️' },
  ];

  useEffect(() => {
    // Load initial plugins
    dispatch(searchPlugins({ query: '', category: 'all' }));
  }, [dispatch]);

  const handleSearch = () => {
    dispatch(setSearchQuery(localSearchQuery));
    dispatch(searchPlugins({ query: localSearchQuery, category: selectedCategory }));
  };

  const handleCategoryChange = (categoryId: string) => {
    dispatch(setSelectedCategory(categoryId));
    dispatch(searchPlugins({ query: localSearchQuery, category: categoryId }));
  };

  const handleInstall = async (pluginId: string) => {
    try {
      await dispatch(installPlugin(pluginId)).unwrap();
      Alert.alert('Success', 'Plugin installed successfully!');
    } catch (error) {
      Alert.alert('Error', 'Failed to install plugin');
    }
  };

  const handleRemove = async (pluginId: string) => {
    Alert.alert(
      'Remove Plugin',
      'Are you sure you want to remove this plugin?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Remove',
          style: 'destructive',
          onPress: async () => {
            try {
              await dispatch(removePlugin(pluginId)).unwrap();
              Alert.alert('Success', 'Plugin removed successfully!');
            } catch (error) {
              Alert.alert('Error', 'Failed to remove plugin');
            }
          },
        },
      ]
    );
  };

  const handlePluginPress = (pluginId: string) => {
    navigation.navigate('PluginDetails', { pluginId });
  };

  const featuredPlugins = plugins.filter(plugin => plugin.featured);
  const regularPlugins = plugins.filter(plugin => !plugin.featured);

  return (
    <View style={styles.container}>
      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search GitHub repos..."
          placeholderTextColor="#888888"
          value={localSearchQuery}
          onChangeText={setLocalSearchQuery}
          onSubmitEditing={handleSearch}
          returnKeyType="search"
        />
        <TouchableOpacity style={styles.searchButton} onPress={handleSearch}>
          <Text style={styles.searchButtonText}>🔍</Text>
        </TouchableOpacity>
      </View>

      {/* Category Filter */}
      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false}
        style={styles.categoryContainer}
        contentContainerStyle={styles.categoryContent}
      >
        {categories.map(category => (
          <CategoryFilter
            key={category.id}
            category={category}
            selected={selectedCategory === category.id}
            onSelect={() => handleCategoryChange(category.id)}
          />
        ))}
      </ScrollView>

      {/* Content */}
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#4CAF50" />
            <Text style={styles.loadingText}>Searching plugins...</Text>
          </View>
        ) : (
          <>
            {/* Featured Plugins */}
            {featuredPlugins.length > 0 && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>⭐ Featured Plugins</Text>
                {featuredPlugins.map(plugin => (
                  <PluginCard
                    key={plugin.id}
                    plugin={plugin}
                    onInstall={() => handleInstall(plugin.id)}
                    onRemove={() => handleRemove(plugin.id)}
                    onPress={() => handlePluginPress(plugin.id)}
                    featured={true}
                  />
                ))}
              </View>
            )}

            {/* Installed Plugins */}
            {installedPlugins.length > 0 && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>📦 My Plugins</Text>
                {installedPlugins.map(plugin => (
                  <PluginCard
                    key={plugin.id}
                    plugin={plugin}
                    onInstall={() => handleInstall(plugin.id)}
                    onRemove={() => handleRemove(plugin.id)}
                    onPress={() => handlePluginPress(plugin.id)}
                    installed={true}
                  />
                ))}
              </View>
            )}

            {/* Search Results */}
            {localSearchQuery && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>🔍 Search Results</Text>
                {regularPlugins.map(plugin => (
                  <PluginCard
                    key={plugin.id}
                    plugin={plugin}
                    onInstall={() => handleInstall(plugin.id)}
                    onRemove={() => handleRemove(plugin.id)}
                    onPress={() => handlePluginPress(plugin.id)}
                  />
                ))}
              </View>
            )}

            {/* All Plugins (when no search) */}
            {!localSearchQuery && regularPlugins.length > 0 && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>🔌 All Plugins</Text>
                {regularPlugins.map(plugin => (
                  <PluginCard
                    key={plugin.id}
                    plugin={plugin}
                    onInstall={() => handleInstall(plugin.id)}
                    onRemove={() => handleRemove(plugin.id)}
                    onPress={() => handlePluginPress(plugin.id)}
                  />
                ))}
              </View>
            )}

            {/* Empty State */}
            {plugins.length === 0 && !loading && (
              <View style={styles.emptyContainer}>
                <Text style={styles.emptyIcon}>🔍</Text>
                <Text style={styles.emptyTitle}>No plugins found</Text>
                <Text style={styles.emptySubtitle}>
                  Try adjusting your search or browse by category
                </Text>
              </View>
            )}
          </>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  searchContainer: {
    flexDirection: 'row',
    padding: 20,
    paddingBottom: 10,
  },
  searchInput: {
    flex: 1,
    backgroundColor: '#2a2a2a',
    borderRadius: 25,
    paddingHorizontal: 20,
    paddingVertical: 12,
    fontSize: 16,
    color: '#ffffff',
    marginRight: 10,
  },
  searchButton: {
    backgroundColor: '#4CAF50',
    borderRadius: 25,
    width: 50,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchButtonText: {
    fontSize: 20,
  },
  categoryContainer: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  categoryContent: {
    paddingRight: 20,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 50,
  },
  loadingText: {
    color: '#cccccc',
    marginTop: 16,
    fontSize: 16,
  },
  section: {
    marginBottom: 30,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 16,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 50,
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 16,
    color: '#888888',
    textAlign: 'center',
  },
});

export default PluginManagerScreen;
