import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Dimensions,
  StatusBar,
} from 'react-native';
import { useDispatch } from 'react-redux';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../types/navigation';
import { loadMockData } from '../store/slices/pluginSlice';

const { width, height } = Dimensions.get('window');

type HomeScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Home'>;

const HomeScreen: React.FC = () => {
  const dispatch = useDispatch();
  const navigation = useNavigation<HomeScreenNavigationProp>();

  useEffect(() => {
    // Load mock data on app start
    dispatch(loadMockData());
  }, [dispatch]);

  const menuItems = [
    {
      title: '🎛️ Plugin Manager',
      subtitle: 'Discover and install AI tools',
      route: 'PluginManager' as keyof RootStackParamList,
      color: '#4CAF50',
      icon: '🔌',
    },
    {
      title: '🎵 Tool Rack',
      subtitle: 'Arrange and chain your plugins',
      route: 'ToolRack' as keyof RootStackParamList,
      color: '#FF9800',
      icon: '🎚️',
    },
    {
      title: '🎚️ Procedure Chain',
      subtitle: 'Build AI workflows',
      route: 'ProcedureChain' as keyof RootStackParamList,
      color: '#2196F3',
      icon: '⚡',
    },
    {
      title: '🎤 Voice Interface',
      subtitle: 'Speak to your AI tools',
      route: 'VoiceInterface' as keyof RootStackParamList,
      color: '#9C27B0',
      icon: '🎙️',
    },
  ];

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1a1a1a" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>🧘 zenOS</Text>
        <Text style={styles.subtitle}>Mobile AI Development Platform</Text>
        <Text style={styles.tagline}>
          Where GitHub repos become VST plugins
        </Text>
      </View>

      {/* Menu Grid */}
      <ScrollView 
        style={styles.menuContainer}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.menuContent}
      >
        {menuItems.map((item, index) => (
          <TouchableOpacity
            key={index}
            style={[styles.menuItem, { backgroundColor: item.color }]}
            onPress={() => navigation.navigate(item.route)}
            activeOpacity={0.8}
          >
            <View style={styles.menuItemContent}>
              <Text style={styles.menuIcon}>{item.icon}</Text>
              <View style={styles.menuTextContainer}>
                <Text style={styles.menuTitle}>{item.title}</Text>
                <Text style={styles.menuSubtitle}>{item.subtitle}</Text>
              </View>
              <Text style={styles.menuArrow}>→</Text>
            </View>
          </TouchableOpacity>
        ))}

        {/* Quick Stats */}
        <View style={styles.statsContainer}>
          <Text style={styles.statsTitle}>Quick Stats</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>4</Text>
              <Text style={styles.statLabel}>Plugins</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>2</Text>
              <Text style={styles.statLabel}>Active</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>1</Text>
              <Text style={styles.statLabel}>Workflows</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>∞</Text>
              <Text style={styles.statLabel}>Possibilities</Text>
            </View>
          </View>
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            "In the future, every developer will be a composer,{'\n'}
            every GitHub repo will be an instrument,{'\n'}
            and every mobile device will be a stage for AI creativity."
          </Text>
          <Text style={styles.footerAuthor}>- zenOS Manifesto</Text>
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  header: {
    paddingTop: 60,
    paddingHorizontal: 20,
    paddingBottom: 30,
    alignItems: 'center',
  },
  title: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 20,
    color: '#cccccc',
    marginBottom: 5,
    textAlign: 'center',
  },
  tagline: {
    fontSize: 16,
    color: '#888888',
    textAlign: 'center',
    fontStyle: 'italic',
  },
  menuContainer: {
    flex: 1,
    paddingHorizontal: 20,
  },
  menuContent: {
    paddingBottom: 40,
  },
  menuItem: {
    borderRadius: 16,
    marginBottom: 16,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
  },
  menuItemContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
  },
  menuIcon: {
    fontSize: 32,
    marginRight: 16,
  },
  menuTextContainer: {
    flex: 1,
  },
  menuTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  menuSubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  menuArrow: {
    fontSize: 24,
    color: '#ffffff',
    fontWeight: 'bold',
  },
  statsContainer: {
    backgroundColor: '#2a2a2a',
    borderRadius: 16,
    padding: 20,
    marginTop: 20,
  },
  statsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 16,
    textAlign: 'center',
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#cccccc',
    textAlign: 'center',
  },
  footer: {
    marginTop: 30,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 14,
    color: '#888888',
    textAlign: 'center',
    lineHeight: 20,
    marginBottom: 10,
  },
  footerAuthor: {
    fontSize: 12,
    color: '#666666',
    fontStyle: 'italic',
  },
});

export default HomeScreen;
