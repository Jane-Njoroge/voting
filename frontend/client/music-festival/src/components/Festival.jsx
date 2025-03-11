import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';

function Festival() {
  return (
    <View style={{ flex: 1, backgroundColor: '#800000', padding: 20 }}>
      <View style={{ alignItems: 'center', marginVertical: 30 }}>
        <Text style={{ fontSize: 28, fontWeight: 'bold', color: '#FFD700', textTransform: 'uppercase' }}>KALENJIN</Text>
        <Text style={{ color: 'white', fontSize: 18 }}>Music Festival</Text>
      </View>

      <View style={{ backgroundColor: 'rgba(255,215,0,0.1)', borderRadius: 15, padding: 15 }}>
        <Text style={{ color: 'white', fontSize: 16, marginBottom: 10 }}>🎶 15-17 Dec | Kipchoge Stadium</Text>
        <TouchableOpacity style={{ backgroundColor: '#FFD700', padding: 12, borderRadius: 25, marginTop: 15 }}>
          <Text style={{ color: '#800000', fontWeight: 'bold', textAlign: 'center' }}>Get Tickets</Text>
        </TouchableOpacity>
      </View>

      <Text style={{ color: '#FFD700', textAlign: 'center', marginTop: 30, fontStyle: 'italic' }}>Celebrating Our Sound</Text>
    </View>
  );
}

export default Festival;