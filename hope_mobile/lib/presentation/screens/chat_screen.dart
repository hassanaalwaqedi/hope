/// HOPE Chat Screen
/// 
/// Redesigned chat interface that feels like a calm human conversation.
/// NOT a typical chatbot - feels supportive, warm, and safe.
/// 
/// Design principles:
/// - Soft, rounded message bubbles
/// - Thoughtful spacing and grouping
/// - Human-like typing indicator
/// - AI presence that feels supportive, not robotic
/// - Dynamic online/offline mode switching

import 'dart:async';
import 'dart:convert';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../../core/theme/app_theme.dart';
import '../../core/theme/hope_icons.dart';
import '../../core/network/connectivity_service.dart';
import '../../data/services/chat_api_service.dart';

/// Message model for display
class ChatDisplayMessage {
  String id; // Mutable for streaming updates
  String content; // Mutable for streaming updates
  final bool isUser;
  final DateTime timestamp;
  final String? imageBase64;
  bool isError;

  ChatDisplayMessage({
    required this.id,
    required this.content,
    required this.isUser,
    required this.timestamp,
    this.imageBase64,
    this.isError = false,
  });
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> with TickerProviderStateMixin {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final ChatApiService _chatService = ChatApiService();
  final ImagePicker _imagePicker = ImagePicker();
  final FocusNode _focusNode = FocusNode();
  
  List<ChatDisplayMessage> _messages = [];
  String? _sessionId;
  bool _isLoading = false;
  bool _isTyping = false;
  String? _pendingImageBase64;
  String? _errorMessage;
  bool _serviceAvailable = true;
  
  // Real-time connectivity monitoring
  StreamSubscription<ConnectivityStatus>? _connectivitySubscription;
  NetworkStatus _networkStatus = NetworkStatus.unknown;
  
  // Supported languages
  static const Map<String, String> _supportedLanguages = {
    'en': 'English',
    'fr': 'Français',
    'ar': 'العربية',
    'de': 'Deutsch',
    'it': 'Italiano', 
    'ko': '한국어',
    'sv': 'Svenska',
    'tr': 'Türkçe',
  };
  
  String _language = 'en';

  @override
  void initState() {
    super.initState();
    _initializeConnectivity();
    _initializeSession();
  }

  @override
  void dispose() {
    _connectivitySubscription?.cancel();
    _messageController.dispose();
    _scrollController.dispose();
    _focusNode.dispose();
    _chatService.dispose();
    super.dispose();
  }
  
  /// Initialize connectivity monitoring
  Future<void> _initializeConnectivity() async {
    // Initialize the global connectivity service
    await connectivityService.initialize();
    
    // Subscribe to connectivity changes
    _connectivitySubscription = connectivityService.statusStream.listen(
      _handleConnectivityChange,
    );
    
    // Set initial status
    _networkStatus = connectivityService.currentStatus.status;
  }
  
  /// Handle connectivity status changes
  void _handleConnectivityChange(ConnectivityStatus status) {
    final wasOffline = _networkStatus != NetworkStatus.online;
    final isNowOnline = status.status == NetworkStatus.online;
    
    setState(() {
      _networkStatus = status.status;
      _serviceAvailable = status.canUseOnlineChat;
      
      if (status.canUseOnlineChat) {
        _errorMessage = null;
      } else if (status.status == NetworkStatus.offline) {
        _errorMessage = _language == 'fr'
            ? 'Pas de connexion internet'
            : 'No internet connection';
      } else {
        _errorMessage = _language == 'fr'
            ? 'Mode hors-ligne: réponses limitées'
            : 'Offline mode: limited responses';
      }
    });
    
    // If we came back online and have an offline session, try to get a real one
    if (wasOffline && isNowOnline && _sessionId?.startsWith('offline_') == true) {
      _tryReconnect();
    }
  }
  
  /// Try to reconnect and get a real session
  Future<void> _tryReconnect() async {
    try {
      final session = await _chatService.startSession(language: _language);
      setState(() {
        _sessionId = session.sessionId;
        _serviceAvailable = true;
        _errorMessage = null;
      });
      
      // Notify user of reconnection
      _addMessage(ChatDisplayMessage(
        id: 'reconnect_${DateTime.now().millisecondsSinceEpoch}',
        content: _language == 'fr' 
            ? '✓ Connexion rétablie - réponses complètes disponibles'
            : '✓ Connected - full AI responses available',
        isUser: false,
        timestamp: DateTime.now(),
      ));
      
      connectivityService.notifyApiSuccess();
    } catch (e) {
      // Stay in offline mode, will retry on next connectivity change
      connectivityService.notifyApiFailure();
    }
  }

  Future<void> _initializeSession() async {
    setState(() => _isLoading = true);
    
    // Check connectivity first
    final status = await connectivityService.checkConnectivity();
    
    // If offline, go straight to offline mode
    if (!status.hasInternet) {
      _startOfflineSession();
      return;
    }
    
    // Try to start online session
    try {
      final session = await _chatService.startSession(language: _language);
      
      // Success - notify connectivity service
      connectivityService.notifyApiSuccess();
      
      setState(() {
        _sessionId = session.sessionId;
        _isLoading = false;
        _serviceAvailable = true;
        _errorMessage = null;
      });
      
      // Welcome message with delay for natural feel
      await Future.delayed(const Duration(milliseconds: 500));
      _addMessage(ChatDisplayMessage(
        id: 'welcome',
        content: _language == 'fr' 
            ? 'Bonjour, je suis là pour t\'écouter. Comment te sens-tu aujourd\'hui?'
            : 'Hello, I\'m here to listen. How are you feeling today?',
        isUser: false,
        timestamp: DateTime.now(),
      ));
    } on ChatServiceUnavailableException {
      // API unavailable - notify and go offline
      connectivityService.notifyApiFailure();
      _startOfflineSession();
    } catch (e) {
      // Any error - notify and go offline
      connectivityService.notifyApiFailure();
      _startOfflineSession();
    }
  }
  
  /// Start offline session with supportive messaging
  void _startOfflineSession() {
    setState(() {
      _sessionId = 'offline_${DateTime.now().millisecondsSinceEpoch}';
      _isLoading = false;
      _serviceAvailable = false;
      _errorMessage = _language == 'fr'
          ? 'Mode hors-ligne: réponses limitées'
          : 'Offline mode: limited responses';
    });
    
    // Add welcome message
    Future.delayed(const Duration(milliseconds: 500), () {
      _addMessage(ChatDisplayMessage(
        id: 'welcome',
        content: _language == 'fr' 
            ? 'Bonjour, je suis là pour t\'écouter. (Mode hors-ligne)'
            : 'Hello, I\'m here to listen. (Offline mode)',
        isUser: false,
        timestamp: DateTime.now(),
      ));
    });
  }

  void _addMessage(ChatDisplayMessage message) {
    setState(() {
      _messages.add(message);
    });
    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: HopeAnimations.normal,
          curve: HopeAnimations.easeOut,
        );
      }
    });
  }

  Future<void> _sendMessage() async {
    final text = _messageController.text.trim();
    if (text.isEmpty && _pendingImageBase64 == null) return;
    if (_sessionId == null) return;
    
    final userMessage = ChatDisplayMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: text,
      isUser: true,
      timestamp: DateTime.now(),
      imageBase64: _pendingImageBase64,
    );
    _addMessage(userMessage);
    
    _messageController.clear();
    final imageToSend = _pendingImageBase64;
    setState(() {
      _pendingImageBase64 = null;
      _isTyping = true;
    });
    
    // Check current connectivity - always try online first if network available
    final currentStatus = connectivityService.currentStatus;
    final shouldTryOnline = currentStatus.hasInternet && 
                            !_sessionId!.startsWith('offline_');
    
    if (shouldTryOnline) {
      try {
        // Create an empty message bubble for streaming
        final streamingMessage = ChatDisplayMessage(
          id: 'streaming_${DateTime.now().millisecondsSinceEpoch}',
          content: '',
          isUser: false,
          timestamp: DateTime.now(),
        );
        _addMessage(streamingMessage);
        setState(() => _isTyping = false);
        
        // Stream tokens into the bubble
        await for (final event in _chatService.sendMessageStream(
          sessionId: _sessionId!,
          text: text.isEmpty ? 'Analyze this image' : text,
          imageBase64: imageToSend,
          language: _language,
        )) {
          final type = event['type'] as String;
          
          if (type == 'token') {
            setState(() {
              streamingMessage.content += event['text'] as String;
            });
            _scrollToBottom();
          } else if (type == 'done') {
            connectivityService.notifyApiSuccess();
            if (!_serviceAvailable) {
              setState(() {
                _serviceAvailable = true;
                _errorMessage = null;
              });
            }
            // Update message id with the real one from the server
            if (event['message_id'] != null) {
              streamingMessage.id = event['message_id'];
            }
            if (event['escalated'] == true) {
              _showCrisisDialog();
            }
          } else if (type == 'error') {
            setState(() {
              streamingMessage.content = _language == 'fr'
                  ? 'Désolé, une erreur est survenue. Veuillez réessayer.'
                  : 'Sorry, an error occurred. Please try again.';
              streamingMessage.isError = true;
            });
          }
        }
        
        return;
      } catch (e) {
        // Streaming failed — remove the empty streaming bubble if still empty
        if (_messages.isNotEmpty && !_messages.last.isUser && _messages.last.content.isEmpty) {
          setState(() => _messages.removeLast());
        }
        
        connectivityService.notifyApiFailure();
        debugPrint('ChatScreen: Streaming failed, falling back to offline: $e');
        setState(() => _isTyping = true);
      }
    }
    
    // Offline response (either truly offline or API failed)
    final offlineResponses = _getOfflineResponses(_language);
    final randomResponse = offlineResponses[math.Random().nextInt(offlineResponses.length)];
    
    await Future.delayed(Duration(
      milliseconds: 1000 + math.Random().nextInt(500),
    ));
    
    _addMessage(ChatDisplayMessage(
      id: 'response_${DateTime.now().millisecondsSinceEpoch}',
      content: randomResponse,
      isUser: false,
      timestamp: DateTime.now(),
    ));
    
    // Update UI to show offline mode if not already
    if (_serviceAvailable && !currentStatus.canUseOnlineChat) {
      setState(() {
        _serviceAvailable = false;
        _errorMessage = _language == 'fr'
            ? 'Mode hors-ligne: réponses limitées'
            : 'Offline mode: limited responses';
      });
    }
    
    setState(() => _isTyping = false);
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final XFile? image = await _imagePicker.pickImage(
        source: source,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );
      
      if (image != null) {
        final bytes = await image.readAsBytes();
        final base64Image = base64Encode(bytes);
        setState(() {
          _pendingImageBase64 = base64Image;
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to pick image: $e')),
      );
    }
  }

  List<String> _getOfflineResponses(String lang) {
    switch (lang) {
      case 'ar':
        return [
          'أنا أسمعك. من الشجاعة أن تشارك ذلك.',
          'خذ لحظة للتنفس. أنت بأمان هنا.',
          'ما تشعر به مهم. لست وحدك.',
          'شكراً لثقتك بي. أنا هنا من أجلك.',
          'من الطبيعي أن تشعر هكذا. أنت تبذل قصارى جهدك.',
        ];
      case 'de':
        return [
          'Ich höre dich. Es ist mutig, das zu teilen.',
          'Nimm dir einen Moment zum Atmen. Du bist hier sicher.',
          'Was du fühlst, ist wichtig. Du bist nicht allein.',
          'Danke, dass du mir vertraust. Ich bin für dich da.',
          'Es ist okay, so zu fühlen. Du machst das Beste.',
        ];
      case 'fr':
        return [
          'Je t\'entends. C\'est courageux de partager ça.',
          'Prends un moment pour respirer. Tu es en sécurité ici.',
          'Ce que tu ressens est valide. Tu n\'es pas seul(e).',
          'Merci de me faire confiance. Je suis là pour toi.',
          'C\'est normal de se sentir ainsi. Tu fais de ton mieux.',
        ];
      case 'it':
        return [
          'Ti ascolto. È coraggioso condividere questo.',
          'Prenditi un momento per respirare. Sei al sicuro qui.',
          'Quello che senti è valido. Non sei solo/a.',
          'Grazie per la tua fiducia. Sono qui per te.',
          'È normale sentirsi così. Stai facendo del tuo meglio.',
        ];
      case 'ko':
        return [
          '당신의 이야기를 듣고 있어요. 이것을 나누는 건 용기 있는 일이에요.',
          '잠시 숨을 쉬세요. 여기서 당신은 안전해요.',
          '당신이 느끼는 것은 중요해요. 혼자가 아니에요.',
          '저를 믿어주셔서 감사합니다. 제가 곁에 있을게요.',
          '그렇게 느끼는 것은 괜찮아요. 최선을 다하고 있어요.',
        ];
      case 'sv':
        return [
          'Jag hör dig. Det är modigt att dela detta.',
          'Ta ett ögonblick att andas. Du är trygg här.',
          'Det du känner är giltigt. Du är inte ensam.',
          'Tack för att du litar på mig. Jag finns här för dig.',
          'Det är okej att känna så. Du gör ditt bästa.',
        ];
      case 'tr':
        return [
          'Seni duyuyorum. Bunu paylaşmak cesaret istiyor.',
          'Nefes almak için bir an dur. Burada güvendesin.',
          'Hissettiklerin önemli. Yalnız değilsin.',
          'Bana güvendiğin için teşekkür ederim. Senin için buradayım.',
          'Böyle hissetmek normal. Elinden gelenin en iyisini yapıyorsun.',
        ];
      case 'en':
      default:
        return [
          'I hear you. It\'s brave to share that.',
          'Take a moment to breathe. You\'re safe here.',
          'What you\'re feeling is valid. You\'re not alone.',
          'Thank you for trusting me. I\'m here for you.',
          'It\'s okay to feel this way. You\'re doing your best.',
        ];
    }
  }

  void _showImagePicker() {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        decoration: BoxDecoration(
          color: isDark ? HopeColors.onyx : HopeColors.surface,
          borderRadius: const BorderRadius.vertical(
            top: Radius.circular(HopeSpacing.radiusXl),
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(HopeSpacing.md),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Handle
                Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: isDark ? HopeColors.shadow : HopeColors.mist,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                const SizedBox(height: HopeSpacing.lg),
                ListTile(
                  leading: Container(
                    padding: const EdgeInsets.all(HopeSpacing.sm),
                    decoration: BoxDecoration(
                      color: HopeColors.sage.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(HopeSpacing.radiusSm),
                    ),
                    child: Icon(Icons.camera_alt_rounded, color: HopeColors.sage),
                  ),
                  title: Text(_language == 'fr' ? 'Appareil photo' : 'Camera'),
                  onTap: () {
                    Navigator.pop(context);
                    _pickImage(ImageSource.camera);
                  },
                ),
                const SizedBox(height: HopeSpacing.sm),
                ListTile(
                  leading: Container(
                    padding: const EdgeInsets.all(HopeSpacing.sm),
                    decoration: BoxDecoration(
                      color: HopeColors.teal.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(HopeSpacing.radiusSm),
                    ),
                    child: Icon(Icons.photo_library_rounded, color: HopeColors.teal),
                  ),
                  title: Text(_language == 'fr' ? 'Galerie' : 'Gallery'),
                  onTap: () {
                    Navigator.pop(context);
                    _pickImage(ImageSource.gallery);
                  },
                ),
                const SizedBox(height: HopeSpacing.md),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showCrisisDialog() {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: isDark ? HopeColors.onyx : HopeColors.surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(HopeSpacing.radiusXl),
        ),
        title: Row(
          children: [
            HopeIcons.butterfly(
              size: 24,
              color: HopeColors.coral,
            ),
            const SizedBox(width: HopeSpacing.sm),
            Text(_language == 'fr' ? 'Ressources d\'aide' : 'Help Resources'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _language == 'fr'
                  ? 'Je vois que tu traverses un moment difficile. Des professionnels sont là pour t\'aider:'
                  : 'I see you\'re going through a difficult time. Professionals are here to help:',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: HopeSpacing.md),
            if (_language == 'fr') ...[
              _buildCrisisLine('3114', 'Prévention du suicide (24h/24)'),
              _buildCrisisLine('112', 'Urgences européennes'),
              _buildCrisisLine('15', 'SAMU'),
            ] else ...[
              _buildCrisisLine('112', 'European Emergency'),
              _buildCrisisLine('', 'Contact your local crisis line'),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              _language == 'fr' ? 'Compris' : 'Understood',
              style: TextStyle(
                color: Theme.of(context).colorScheme.primary,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCrisisLine(String number, String description) {
    return Padding(
      padding: const EdgeInsets.only(bottom: HopeSpacing.sm),
      child: Row(
        children: [
          if (number.isNotEmpty) ...[
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: HopeSpacing.sm,
                vertical: HopeSpacing.xs,
              ),
              decoration: BoxDecoration(
                color: HopeColors.success.withOpacity(0.15),
                borderRadius: BorderRadius.circular(HopeSpacing.radiusSm),
              ),
              child: Text(
                number,
                style: TextStyle(
                  color: HopeColors.success,
                  fontWeight: FontWeight.w600,
                  fontSize: 13,
                ),
              ),
            ),
            const SizedBox(width: HopeSpacing.sm),
          ],
          Expanded(
            child: Text(
              description,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return Scaffold(
      backgroundColor: isDark ? HopeColors.charcoal : HopeColors.cream,
      appBar: AppBar(
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(HopeSpacing.radiusSm),
              ),
              child: HopeIcons.butterfly(
                size: 18,
                color: Theme.of(context).colorScheme.primary,
              ),
            ),
            const SizedBox(width: HopeSpacing.sm),
            const Text('HOPE'),
          ],
        ),
        actions: [
          // Language selector
          PopupMenuButton<String>(
            onSelected: (lang) {
              setState(() => _language = lang);
            },
            itemBuilder: (context) => _supportedLanguages.entries
                .map((e) => PopupMenuItem(
                      value: e.key,
                      child: Row(
                        children: [
                          if (_language == e.key)
                            Icon(Icons.check_rounded, 
                                 color: Theme.of(context).colorScheme.primary,
                                 size: 18),
                          if (_language != e.key)
                            const SizedBox(width: 18),
                          const SizedBox(width: 8),
                          Text(e.value),
                        ],
                      ),
                    ))
                .toList(),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    _language.toUpperCase(),
                    style: TextStyle(
                      fontWeight: FontWeight.w600,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                  Icon(Icons.arrow_drop_down,
                       color: Theme.of(context).colorScheme.primary),
                ],
              ),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          // Service unavailable banner
          if (!_serviceAvailable)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(HopeSpacing.md),
              color: HopeColors.amber.withOpacity(0.15),
              child: Row(
                children: [
                  Icon(Icons.cloud_off_rounded, color: HopeColors.amber, size: 20),
                  const SizedBox(width: HopeSpacing.sm),
                  Expanded(
                    child: Text(
                      _errorMessage ?? 'Service unavailable',
                      style: TextStyle(color: HopeColors.amber),
                    ),
                  ),
                ],
              ),
            ),
          
          // Loading state
          if (_isLoading)
            const Expanded(
              child: Center(
                child: _LoadingIndicator(),
              ),
            )
          else
            // Chat messages
            Expanded(
              child: ListView.builder(
                controller: _scrollController,
                padding: const EdgeInsets.all(HopeSpacing.md),
                itemCount: _messages.length + (_isTyping ? 1 : 0),
                itemBuilder: (context, index) {
                  if (index == _messages.length && _isTyping) {
                    return const _TypingIndicator();
                  }
                  return _MessageBubble(
                    message: _messages[index],
                    showAvatar: _shouldShowAvatar(index),
                  );
                },
              ),
            ),
          
          // Image preview
          if (_pendingImageBase64 != null)
            Container(
              padding: const EdgeInsets.all(HopeSpacing.sm),
              margin: const EdgeInsets.symmetric(horizontal: HopeSpacing.md),
              decoration: BoxDecoration(
                color: isDark ? HopeColors.onyxLight : HopeColors.surfaceElevated,
                borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
              ),
              child: Row(
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.circular(HopeSpacing.radiusSm),
                    child: Image.memory(
                      base64Decode(_pendingImageBase64!),
                      width: 56,
                      height: 56,
                      fit: BoxFit.cover,
                    ),
                  ),
                  const SizedBox(width: HopeSpacing.sm),
                  Expanded(
                    child: Text(
                      _language == 'fr' ? 'Image prête' : 'Image ready',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ),
                  IconButton(
                    icon: Icon(Icons.close_rounded, size: 20),
                    onPressed: () => setState(() => _pendingImageBase64 = null),
                    color: HopeColors.slateMuted,
                  ),
                ],
              ),
            ),
          
          // Input area
          _ChatInput(
            controller: _messageController,
            focusNode: _focusNode,
            onSend: _sendMessage,
            onAttach: _showImagePicker,
            enabled: true,
            language: _language,
          ),
        ],
      ),
    );
  }

  bool _shouldShowAvatar(int index) {
    if (index == 0) return true;
    final current = _messages[index];
    final previous = _messages[index - 1];
    return current.isUser != previous.isUser;
  }
}

// ============================================================================
// MESSAGE BUBBLE - Soft, rounded, human-like
// ============================================================================

class _MessageBubble extends StatelessWidget {
  final ChatDisplayMessage message;
  final bool showAvatar;

  const _MessageBubble({
    required this.message,
    required this.showAvatar,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final isUser = message.isUser;
    
    return Padding(
      padding: EdgeInsets.only(
        bottom: showAvatar ? HopeSpacing.md : HopeSpacing.xs,
        left: isUser ? HopeSpacing.xxl : 0,
        right: isUser ? 0 : HopeSpacing.xxl,
      ),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          // AI Avatar
          if (!isUser && showAvatar) ...[
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primary.withOpacity(0.15),
                borderRadius: BorderRadius.circular(HopeSpacing.radiusSm),
              ),
              child: HopeIcons.butterfly(
                size: 18,
                color: Theme.of(context).colorScheme.primary,
              ),
            ),
            const SizedBox(width: HopeSpacing.sm),
          ] else if (!isUser) ...[
            const SizedBox(width: 44), // Space for avatar
          ],
          
          // Message bubble
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(
                horizontal: HopeSpacing.md,
                vertical: HopeSpacing.sm + 2,
              ),
              decoration: BoxDecoration(
                color: isUser
                    ? Theme.of(context).colorScheme.primary
                    : message.isError
                        ? HopeColors.coral.withOpacity(0.1)
                        : (isDark ? HopeColors.onyxLight : HopeColors.surface),
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(20),
                  topRight: const Radius.circular(20),
                  bottomLeft: Radius.circular(isUser ? 20 : 6),
                  bottomRight: Radius.circular(isUser ? 6 : 20),
                ),
                boxShadow: isUser ? null : HopeShadows.light,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Image if present
                  if (message.imageBase64 != null) ...[
                    ClipRRect(
                      borderRadius: BorderRadius.circular(HopeSpacing.radiusSm),
                      child: Image.memory(
                        base64Decode(message.imageBase64!),
                        fit: BoxFit.cover,
                        width: double.infinity,
                      ),
                    ),
                    const SizedBox(height: HopeSpacing.sm),
                  ],
                  // Message text
                  Text(
                    message.content,
                    style: TextStyle(
                      color: isUser
                          ? Colors.white
                          : message.isError
                              ? HopeColors.coral
                              : null,
                      fontSize: 15,
                      height: 1.5,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ============================================================================
// TYPING INDICATOR - Human-like, gentle
// ============================================================================

class _TypingIndicator extends StatefulWidget {
  const _TypingIndicator();

  @override
  State<_TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<_TypingIndicator>
    with TickerProviderStateMixin {
  late List<AnimationController> _controllers;
  late List<Animation<double>> _animations;

  @override
  void initState() {
    super.initState();
    _controllers = List.generate(3, (index) {
      return AnimationController(
        duration: const Duration(milliseconds: 600),
        vsync: this,
      );
    });
    
    _animations = _controllers.map((controller) {
      return Tween<double>(begin: 0, end: 1).animate(
        CurvedAnimation(parent: controller, curve: Curves.easeInOut),
      );
    }).toList();
    
    // Stagger the animations
    for (int i = 0; i < _controllers.length; i++) {
      Future.delayed(Duration(milliseconds: i * 150), () {
        if (mounted) {
          _controllers[i].repeat(reverse: true);
        }
      });
    }
  }

  @override
  void dispose() {
    for (final controller in _controllers) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return Padding(
      padding: const EdgeInsets.only(bottom: HopeSpacing.md),
      child: Row(
        children: [
          // Avatar
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primary.withOpacity(0.15),
              borderRadius: BorderRadius.circular(HopeSpacing.radiusSm),
            ),
            child: HopeIcons.butterfly(
              size: 18,
              color: Theme.of(context).colorScheme.primary,
            ),
          ),
          const SizedBox(width: HopeSpacing.sm),
          // Typing dots
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: HopeSpacing.md,
              vertical: HopeSpacing.sm + 4,
            ),
            decoration: BoxDecoration(
              color: isDark ? HopeColors.onyxLight : HopeColors.surface,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(20),
                topRight: Radius.circular(20),
                bottomLeft: Radius.circular(6),
                bottomRight: Radius.circular(20),
              ),
              boxShadow: HopeShadows.light,
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: List.generate(3, (index) {
                return AnimatedBuilder(
                  animation: _animations[index],
                  builder: (context, child) {
                    return Container(
                      margin: EdgeInsets.only(
                        left: index > 0 ? 4 : 0,
                      ),
                      width: 8,
                      height: 8,
                      decoration: BoxDecoration(
                        color: Theme.of(context)
                            .colorScheme
                            .primary
                            .withOpacity(0.3 + (_animations[index].value * 0.5)),
                        shape: BoxShape.circle,
                      ),
                    );
                  },
                );
              }),
            ),
          ),
        ],
      ),
    );
  }
}

// ============================================================================
// LOADING INDICATOR
// ============================================================================

class _LoadingIndicator extends StatelessWidget {
  const _LoadingIndicator();

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: 48,
          height: 48,
          child: CircularProgressIndicator(
            strokeWidth: 2.5,
            color: Theme.of(context).colorScheme.primary.withOpacity(0.6),
          ),
        ),
        const SizedBox(height: HopeSpacing.md),
        Text(
          'Connexion...',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
              ),
        ),
      ],
    );
  }
}

// ============================================================================
// CHAT INPUT - Warm, accessible
// ============================================================================

class _ChatInput extends StatelessWidget {
  final TextEditingController controller;
  final FocusNode focusNode;
  final VoidCallback onSend;
  final VoidCallback onAttach;
  final bool enabled;
  final String language;

  const _ChatInput({
    required this.controller,
    required this.focusNode,
    required this.onSend,
    required this.onAttach,
    required this.enabled,
    required this.language,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return Container(
      padding: const EdgeInsets.all(HopeSpacing.md),
      decoration: BoxDecoration(
        color: isDark ? HopeColors.onyx : HopeColors.surface,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        top: false,
        child: Row(
          children: [
            // Attach button
            _InputButton(
              icon: Icons.add_rounded,
              onTap: onAttach,
              color: Theme.of(context).colorScheme.primary,
            ),
            const SizedBox(width: HopeSpacing.sm),
            // Text input
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: isDark ? HopeColors.onyxLight : HopeColors.surfaceElevated,
                  borderRadius: BorderRadius.circular(HopeSpacing.radiusXl),
                ),
                child: TextField(
                  controller: controller,
                  focusNode: focusNode,
                  enabled: enabled,
                  textCapitalization: TextCapitalization.sentences,
                  decoration: InputDecoration(
                    hintText: language == 'fr'
                        ? 'Écris ton message...'
                        : 'Type your message...',
                    border: InputBorder.none,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: HopeSpacing.md,
                      vertical: HopeSpacing.sm + 2,
                    ),
                    hintStyle: TextStyle(
                      color: isDark
                          ? HopeColors.moonlightMuted
                          : HopeColors.slateMuted,
                    ),
                  ),
                  style: TextStyle(
                    fontSize: 15,
                    color: isDark ? HopeColors.moonlight : HopeColors.slate,
                  ),
                  textInputAction: TextInputAction.send,
                  onSubmitted: (_) => onSend(),
                ),
              ),
            ),
            const SizedBox(width: HopeSpacing.sm),
            // Send button
            _InputButton(
              icon: Icons.arrow_upward_rounded,
              onTap: onSend,
              color: Theme.of(context).colorScheme.primary,
              filled: true,
            ),
          ],
        ),
      ),
    );
  }
}

class _InputButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;
  final Color color;
  final bool filled;

  const _InputButton({
    required this.icon,
    required this.onTap,
    required this.color,
    this.filled = false,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: filled ? color : Colors.transparent,
      borderRadius: BorderRadius.circular(HopeSpacing.radiusFull),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(HopeSpacing.radiusFull),
        child: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            border: filled ? null : Border.all(color: color.withOpacity(0.3)),
          ),
          child: Icon(
            icon,
            color: filled ? Colors.white : color,
            size: 22,
          ),
        ),
      ),
    );
  }
}
