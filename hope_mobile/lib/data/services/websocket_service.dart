/// WebSocket Service - Connects to HOPE backend for AI responses
import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

enum ConnectionState { disconnected, connecting, connected, reconnecting }

class WebSocketService {
  static const String _defaultHost = 'localhost';
  static const int _defaultPort = 8000;
  static const String _panicEndpoint = '/ws/panic';
  
  WebSocketChannel? _channel;
  ConnectionState _state = ConnectionState.disconnected;
  Timer? _reconnectTimer;
  Timer? _heartbeatTimer;
  int _reconnectAttempts = 0;
  static const int _maxReconnectAttempts = 5;
  
  final _messageController = StreamController<Map<String, dynamic>>.broadcast();
  final _stateController = StreamController<ConnectionState>.broadcast();
  final _messageQueue = <Map<String, dynamic>>[];
  
  String? _currentSessionId;
  String? _userId;
  
  Stream<Map<String, dynamic>> get messages => _messageController.stream;
  Stream<ConnectionState> get connectionState => _stateController.stream;
  ConnectionState get state => _state;
  bool get isConnected => _state == ConnectionState.connected;

  Future<void> connect({
    String host = _defaultHost,
    int port = _defaultPort,
    String? userId,
  }) async {
    if (_state == ConnectionState.connecting) return;
    
    _userId = userId ?? 'user_${DateTime.now().millisecondsSinceEpoch}';
    _updateState(ConnectionState.connecting);
    
    try {
      final uri = Uri.parse('ws://$host:$port$_panicEndpoint?user_id=$_userId');
      _channel = WebSocketChannel.connect(uri);
      
      await _channel!.ready;
      _updateState(ConnectionState.connected);
      _reconnectAttempts = 0;
      
      // Listen to incoming messages
      _channel!.stream.listen(
        _handleMessage,
        onError: _handleError,
        onDone: _handleDisconnect,
      );
      
      // Start heartbeat
      _startHeartbeat();
      
      // Send queued messages
      _flushMessageQueue();
      
    } catch (e) {
      _handleError(e);
    }
  }

  void _handleMessage(dynamic data) {
    try {
      final message = jsonDecode(data as String) as Map<String, dynamic>;
      
      // Handle session ID assignment
      if (message['type'] == 'session_started') {
        _currentSessionId = message['session_id'] as String?;
      }
      
      // Handle heartbeat response
      if (message['type'] == 'pong') {
        return; // Don't forward heartbeats
      }
      
      _messageController.add(message);
    } catch (e) {
      // Ignore parse errors
    }
  }

  void _handleError(dynamic error) {
    _updateState(ConnectionState.disconnected);
    _scheduleReconnect();
  }

  void _handleDisconnect() {
    _updateState(ConnectionState.disconnected);
    _stopHeartbeat();
    _scheduleReconnect();
  }

  void _scheduleReconnect() {
    if (_reconnectAttempts >= _maxReconnectAttempts) {
      return; // Give up after max attempts
    }
    
    _reconnectTimer?.cancel();
    _updateState(ConnectionState.reconnecting);
    
    final delay = Duration(seconds: (2 << _reconnectAttempts).clamp(2, 30));
    _reconnectTimer = Timer(delay, () {
      _reconnectAttempts++;
      connect();
    });
  }

  void _startHeartbeat() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      sendMessage({'type': 'ping'});
    });
  }

  void _stopHeartbeat() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = null;
  }

  void _updateState(ConnectionState newState) {
    _state = newState;
    _stateController.add(newState);
  }

  void _flushMessageQueue() {
    for (final message in _messageQueue) {
      _sendImmediate(message);
    }
    _messageQueue.clear();
  }

  void _sendImmediate(Map<String, dynamic> message) {
    if (_channel != null && _state == ConnectionState.connected) {
      _channel!.sink.add(jsonEncode(message));
    }
  }

  /// Send a message to the backend
  void sendMessage(Map<String, dynamic> message) {
    message['session_id'] = _currentSessionId;
    message['user_id'] = _userId;
    message['timestamp'] = DateTime.now().toIso8601String();
    
    if (_state == ConnectionState.connected) {
      _sendImmediate(message);
    } else {
      _messageQueue.add(message);
    }
  }

  /// Start a panic session
  void startPanicSession({double? initialIntensity}) {
    sendMessage({
      'type': 'panic_start',
      'intensity': initialIntensity ?? 5.0,
      'message': 'User initiated panic session',
    });
  }

  /// Send user message during panic session
  void sendPanicMessage(String text, {double? intensity}) {
    sendMessage({
      'type': 'user_message',
      'text': text,
      'intensity': intensity,
    });
  }

  /// Report intensity change
  void reportIntensity(double intensity) {
    sendMessage({
      'type': 'intensity_update',
      'intensity': intensity,
    });
  }

  /// End panic session
  void endPanicSession({String outcome = 'resolved'}) {
    sendMessage({
      'type': 'panic_end',
      'outcome': outcome,
    });
  }

  /// Disconnect from server
  Future<void> disconnect() async {
    _reconnectTimer?.cancel();
    _stopHeartbeat();
    await _channel?.sink.close();
    _channel = null;
    _updateState(ConnectionState.disconnected);
  }

  void dispose() {
    disconnect();
    _messageController.close();
    _stateController.close();
  }
}
