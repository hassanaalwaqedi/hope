/// Chat API Service
/// 
/// Handles communication with the backend chat API.
/// All data comes from real Gemini API calls - no mocks.
library;

import 'dart:convert';
import 'package:http/http.dart' as http;

/// Configuration for the chat API
class ChatConfig {
  // Production Azure backend
  static const String baseUrl = 'https://hope-api-b3bxa3htdkd3guhc.swedencentral-01.azurewebsites.net/api/v1';
  
  // For local development, uncomment this:
  // static const String baseUrl = 'http://localhost:8000/api/v1';
  
  static const Duration timeout = Duration(seconds: 10);
}

/// Response from starting a chat session
class ChatSessionResponse {
  final String sessionId;
  final String language;
  final String createdAt;

  ChatSessionResponse({
    required this.sessionId,
    required this.language,
    required this.createdAt,
  });

  factory ChatSessionResponse.fromJson(Map<String, dynamic> json) {
    return ChatSessionResponse(
      sessionId: json['session_id'] as String,
      language: json['language'] as String,
      createdAt: json['created_at'] as String,
    );
  }
}

/// Response from sending a chat message
class ChatMessageResponse {
  final String textAnswer;
  final List<String> safetyFlags;
  final double confidenceScore;
  final bool escalated;
  final String sessionId;
  final String? messageId;
  final int latencyMs;
  final bool aiCalled;

  ChatMessageResponse({
    required this.textAnswer,
    required this.safetyFlags,
    required this.confidenceScore,
    required this.escalated,
    required this.sessionId,
    this.messageId,
    required this.latencyMs,
    required this.aiCalled,
  });

  factory ChatMessageResponse.fromJson(Map<String, dynamic> json) {
    return ChatMessageResponse(
      textAnswer: json['text_answer'] as String,
      safetyFlags: List<String>.from(json['safety_flags'] ?? []),
      confidenceScore: (json['confidence_score'] as num).toDouble(),
      escalated: json['escalated'] as bool,
      sessionId: json['session_id'] as String,
      messageId: json['message_id'] as String?,
      latencyMs: json['latency_ms'] as int,
      aiCalled: json['ai_called'] as bool,
    );
  }
}

/// Service for interacting with the chat API
class ChatApiService {
  final http.Client _client;

  ChatApiService({http.Client? client}) : _client = client ?? http.Client();

  /// Start a new chat session
  Future<ChatSessionResponse> startSession({
    String language = 'fr',
    String? userId,
  }) async {
    final response = await _client
        .post(
          Uri.parse('${ChatConfig.baseUrl}/chat/session/start'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({
            'language': language,
            if (userId != null) 'user_id': userId,
          }),
        )
        .timeout(ChatConfig.timeout);

    if (response.statusCode == 200) {
      return ChatSessionResponse.fromJson(jsonDecode(response.body));
    } else if (response.statusCode == 503) {
      throw ChatServiceUnavailableException(
        'AI chat is not available - service not configured',
      );
    } else {
      throw ChatApiException(
        'Failed to start session: ${response.statusCode}',
        response.statusCode,
      );
    }
  }

  /// Send a message to the AI
  Future<ChatMessageResponse> sendMessage({
    required String sessionId,
    required String text,
    String? imageBase64,
    String language = 'fr',
  }) async {
    final response = await _client
        .post(
          Uri.parse('${ChatConfig.baseUrl}/chat/message'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({
            'session_id': sessionId,
            'text': text,
            if (imageBase64 != null) 'image': imageBase64,
            'language': language,
          }),
        )
        .timeout(ChatConfig.timeout);

    if (response.statusCode == 200) {
      return ChatMessageResponse.fromJson(jsonDecode(response.body));
    } else if (response.statusCode == 503) {
      throw ChatServiceUnavailableException(
        'AI chat is not available',
      );
    } else if (response.statusCode == 404) {
      throw ChatSessionNotFoundException('Session not found');
    } else {
      throw ChatApiException(
        'Failed to send message: ${response.statusCode}',
        response.statusCode,
      );
    }
  }

  /// Get session history
  Future<Map<String, dynamic>> getHistory(String sessionId) async {
    final response = await _client
        .get(
          Uri.parse('${ChatConfig.baseUrl}/chat/history/$sessionId'),
          headers: {'Content-Type': 'application/json'},
        )
        .timeout(ChatConfig.timeout);

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else if (response.statusCode == 404) {
      throw ChatSessionNotFoundException('Session not found');
    } else {
      throw ChatApiException(
        'Failed to get history: ${response.statusCode}',
        response.statusCode,
      );
    }
  }

  void dispose() {
    _client.close();
  }
}

/// Exception for API errors
class ChatApiException implements Exception {
  final String message;
  final int statusCode;

  ChatApiException(this.message, this.statusCode);

  @override
  String toString() => 'ChatApiException: $message (status: $statusCode)';
}

/// Exception when service is unavailable
class ChatServiceUnavailableException implements Exception {
  final String message;

  ChatServiceUnavailableException(this.message);

  @override
  String toString() => 'ChatServiceUnavailableException: $message';
}

/// Exception when session is not found
class ChatSessionNotFoundException implements Exception {
  final String message;

  ChatSessionNotFoundException(this.message);

  @override
  String toString() => 'ChatSessionNotFoundException: $message';
}
