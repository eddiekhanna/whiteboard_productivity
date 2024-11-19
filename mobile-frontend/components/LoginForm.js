import React from 'react';
import { View, Text, TextInput, Button, StyleSheet } from 'react-native';

function LoginForm ({ username, setUsername, password, setPassword, handleLogin}) {
    return (
        <View style={styles.container}> 
            <Text style={styles.heading}>Whiteboard Productivity</Text>
            <TextInput placeholder="Username"  value={username} onChangeText={setUsername}/>
            <TextInput placeholder="Password"  value={password} onChangeText={setPassword}/>
            <Button title="Login" onPress={handleLogin}/>
        </View>
    );
}

export default LoginForm;

////////////// STYLE SHEET /////////////////////
const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: '#fff',
      alignItems: 'center',
      justifyContent: 'center',
    },
    heading: {
        fontSize: 36,
        fontFamily: 'Comic Sans MS',
        fontWeight: 'bold', 
      },
  });

