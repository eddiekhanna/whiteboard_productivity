import { StatusBar } from 'expo-status-bar';
import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet } from 'react-native';
import LoginContainer from './containers/LoginContainer';

export default function App() {

  return (
    <View style={styles.container}>
      <LoginContainer />
    </View>
  );
}

////////////// STYLE SHEET /////////////////////
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'white', // Change this to 'white' or another desired color
    justifyContent: 'center',
    alignItems: 'center',
  },
});
