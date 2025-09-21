import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { Provider } from 'react-redux';
import { StatusBar } from 'react-native';
import { store } from './src/store/store';

// Screens
import HomeScreen from './src/screens/HomeScreen';
import PluginManagerScreen from './src/screens/PluginManagerScreen';
import ToolRackScreen from './src/screens/ToolRackScreen';
import ProcedureChainScreen from './src/screens/ProcedureChainScreen';
import VoiceInterfaceScreen from './src/screens/VoiceInterfaceScreen';
import PluginDetailsScreen from './src/screens/PluginDetailsScreen';

// Types
type RootStackParamList = {
  Home: undefined;
  PluginManager: undefined;
  ToolRack: undefined;
  ProcedureChain: undefined;
  VoiceInterface: undefined;
  PluginDetails: { pluginId: string };
};

const Stack = createStackNavigator<RootStackParamList>();

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <NavigationContainer>
        <StatusBar barStyle="light-content" backgroundColor="#1a1a1a" />
        <Stack.Navigator
          initialRouteName="Home"
          screenOptions={{
            headerStyle: {
              backgroundColor: '#1a1a1a',
            },
            headerTintColor: '#ffffff',
            headerTitleStyle: {
              fontWeight: 'bold',
              fontSize: 18,
            },
            headerBackTitleVisible: false,
          }}
        >
          <Stack.Screen 
            name="Home" 
            component={HomeScreen}
            options={{ 
              title: '🧘 zenOS',
              headerShown: false 
            }}
          />
          <Stack.Screen 
            name="PluginManager" 
            component={PluginManagerScreen}
            options={{ title: '🎛️ Plugin Manager' }}
          />
          <Stack.Screen 
            name="ToolRack" 
            component={ToolRackScreen}
            options={{ title: '🎵 Tool Rack' }}
          />
          <Stack.Screen 
            name="ProcedureChain" 
            component={ProcedureChainScreen}
            options={{ title: '🎚️ Procedure Chain' }}
          />
          <Stack.Screen 
            name="VoiceInterface" 
            component={VoiceInterfaceScreen}
            options={{ title: '🎤 Voice Interface' }}
          />
          <Stack.Screen 
            name="PluginDetails" 
            component={PluginDetailsScreen}
            options={{ title: 'Plugin Details' }}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </Provider>
  );
};

export default App;
